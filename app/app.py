from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sys, os
import pandas as pd
import numpy as np
import joblib
from fuzzywuzzy import fuzz, process

# Add src path safely
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
except NameError:
    import pathlib
    sys.path.append(str(pathlib.Path().resolve().parent))

from src.data_preprocessing import load_and_preprocess_data
from src.prediction import SymptomPredictor
from src.logger import setup_logger
from .db import authenticate_user, create_user, create_users_table, get_user_id, save_symptom_check, get_user_profile, update_user_profile, get_past_symptom_checks, get_doctors_by_pincode_and_specialty

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role='user'):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    # Load user role from DB or default to 'user'
    # For simplicity, assuming username == id and role stored in DB
    # Here, we mock role as 'admin' if username is 'admin', else 'user'
    role = 'admin' if user_id == 'admin' else 'user'
    return User(user_id, user_id, role)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'role', 'user') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            role = 'admin' if username == 'admin' else 'user'
            user = User(username, username, role)
            login_user(user)
            flash('Logged in successfully!')
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if not username:
            flash('Please enter a username.')
        elif password != confirm_password:
            flash('Passwords do not match.')
        elif username == 'admin':
            flash('Admin signup is not allowed here.')
        else:
            if create_user(username, password):
                user = User(username, username)
                login_user(user)
                flash('Account created and logged in successfully!')
                return redirect(url_for('dashboard'))
            else:
                flash('Username already exists.')
    return render_template('signup.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if getattr(current_user, 'role', 'user') != 'admin':
        flash('Access denied.')
        return redirect(url_for('home'))

    total_users = get_total_users()
    symptom_checks_today = get_symptom_checks_today()
    active_users = get_active_users()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           symptom_checks_today=symptom_checks_today,
                           active_users=active_users)

logger = setup_logger()
logger.info("Flask application started")

create_users_table()

def get_total_users():
    try:
        from app.db import get_user_count
        return get_user_count()
    except ImportError:
        return 0

def get_symptom_checks_today():
    try:
        from app.db import get_symptom_checks_count_today
        return get_symptom_checks_count_today()
    except ImportError:
        return 0

def get_active_users():
    try:
        from app.db import get_active_user_count
        return get_active_user_count()
    except ImportError:
        return 0

@app.route('/admin/data/user_demographics')
@login_required
def get_user_demographics_data():
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    demographics = get_user_demographics()
    return jsonify(demographics)

@app.route('/admin/data/symptom_trends')
@login_required
def get_symptom_trends_data():
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    trends = get_symptom_trends()
    return jsonify(trends)

@app.route('/admin/data/system_metrics')
@login_required
def get_system_metrics_data():
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    metrics = get_system_performance_metrics()
    return jsonify(metrics)

@app.route('/admin/data/user_activity')
@login_required
def get_user_activity_data():
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    logs = get_user_activity_logs()
    return jsonify(logs)

predictor = None
df = None
symptoms = []
symptom_descriptions = {}
try:
    data_path = os.path.join(os.path.dirname(__file__), "../data/disease.csv")
    model_path = os.path.join(os.path.dirname(__file__), "../models/best_model.joblib")
    encoder_path = os.path.join(os.path.dirname(__file__), "../models/label_encoder.joblib")
    X_train_std, X_test_std, X_train_mm, X_test_mm, y_train, y_test, label_encoder, df, symptoms, demographics = load_and_preprocess_data(
        data_path
    )
    predictor = SymptomPredictor(model_path=model_path, encoder_path=encoder_path)
    symptom_descriptions = predictor.get_symptom_descriptions()
    logger.info("Model and data loaded successfully")
except Exception as e:
    logger.error(f"Error loading model/data: {e}")
    print(f"Error loading model/data: {e}")
    predictor = None
    df = None
    symptoms = []
    symptom_descriptions = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/symptom_checker', methods=['GET', 'POST'])
def symptom_checker():
    if predictor is None or df is None:
        flash("Predictor or data not available.")
        return redirect(url_for('home'))

    step = session.get('step', 1)

    if request.method == 'POST':
        if 'continue_step1' in request.form:
            age = request.form.get('age')
            sex = request.form.get('sex')
            if not age or not sex:
                flash("Please fill in all required fields.")
                return redirect(url_for('symptom_checker'))
            session['age'] = int(age)
            session['sex'] = sex
            session['step'] = 2
            return redirect(url_for('symptom_checker'))
        elif 'back_step2' in request.form:
            session['step'] = 1
            return redirect(url_for('symptom_checker'))
        elif 'get_prediction' in request.form:
            selected_symptoms_raw = request.form.get('selected_symptoms', '')
            selected_symptoms_list = [s.strip() for s in selected_symptoms_raw.split(',') if s.strip()]
            selected_symptoms = {symptom: symptom in selected_symptoms_list for symptom in symptoms}

            if not any(selected_symptoms.values()):
                flash("Please select at least one symptom.")
                return redirect(url_for('symptom_checker'))
            session['selected_symptoms'] = selected_symptoms
            session['step'] = 3
            symptom_input = {symptom: int(selected) for symptom, selected in selected_symptoms.items()}
            try:
                result = predictor.predict_disease(symptom_input, df)
                session['prediction_result'] = result
                if current_user.is_authenticated:
                    user_id = get_user_id(current_user.username)
                    if user_id:
                        save_symptom_check(
                            user_id=user_id,
                            age=session['age'],
                            sex=session['sex'],
                            symptoms=selected_symptoms,
                            prediction=result
                        )
            except Exception as e:
                flash(f"Error making prediction: {e}")
                return redirect(url_for('symptom_checker'))
            return redirect(url_for('symptom_checker'))
        elif 'back_step3' in request.form:
            session['step'] = 2
            return redirect(url_for('symptom_checker'))
        elif 'next_step3' in request.form:
            # Redirect to disease details page instead of step 4
            return redirect(url_for('disease_details', disease=session['prediction_result']['primary_prediction']))
        elif 'back_step4' in request.form:
            session['step'] = 3
            return redirect(url_for('symptom_checker'))
        elif 'next_step4' in request.form:
            session['step'] = 5
            return redirect(url_for('symptom_checker'))
        elif 'back_step5' in request.form:
            session['step'] = 4
            return redirect(url_for('symptom_checker'))
        elif 'restart' in request.form:
            session.clear()
            session['step'] = 1
            return redirect(url_for('symptom_checker'))

    selected_symptoms = session.get('selected_symptoms', {})
    selected_list = [s for s, sel in selected_symptoms.items() if sel]
    return render_template('symptom_checker.html', step=step, symptoms=symptoms, symptom_descriptions=symptom_descriptions, selected_list=selected_list)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_id = get_user_id(current_user.username)
    if not user_id:
        flash("User not found.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        age = request.form.get('age', type=int)
        gender = request.form['gender']
        medical_history = request.form['medical_history']
        allergies = request.form['allergies']
        if update_user_profile(user_id, age, gender, medical_history, allergies):
            flash("Profile updated successfully!")
        else:
            flash("Failed to update profile.")
        return redirect(url_for('dashboard'))

    profile = get_user_profile(user_id)
    past_checks = get_past_symptom_checks(user_id)

    return render_template('dashboard.html', profile=profile, past_checks=past_checks)

@app.route('/find_doctor', methods=['GET', 'POST'])
def find_doctor():
    doctors = []
    if request.method == 'POST':
        pincode = request.form.get('location')
        specialty = request.form.get('specialty')
        if not pincode:
            flash("Please enter a pincode.")
            return redirect(url_for('find_doctor'))
        doctors = get_doctors_by_pincode_and_specialty(pincode, specialty if specialty != "" else None)
    return render_template('find_doctor.html', doctors=doctors)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/api/symptom_suggestions')
def symptom_suggestions():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    suggestions = process.extract(query, symptoms, limit=10, scorer=fuzz.partial_ratio)
    filtered_suggestions = [s[0] for s in suggestions if s[1] > 70]
    return jsonify(filtered_suggestions)

@app.route('/disease_details/<disease>')
def disease_details(disease):
    # Fetch disease details from MedlinePlus API or use mock data
    import requests
    try:
        # MedlinePlus API endpoint for health topics
        api_url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term={disease}&retmax=1"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data.get('esearchresult', {}).get('idlist'):
                id = data['esearchresult']['idlist'][0]
                summary_url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopicsDetailed&term={id}&retmax=1"
                summary_response = requests.get(summary_url)
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    # Extract relevant information
                    disease_info = {
                        'name': disease,
                        'summary': summary_data.get('result', {}).get(id, {}).get('summary', 'No summary available.'),
                        'url': f"https://medlineplus.gov/ency/article/{id}.htm"
                    }
                else:
                    disease_info = get_mock_disease_info(disease)
            else:
                disease_info = get_mock_disease_info(disease)
        else:
            disease_info = get_mock_disease_info(disease)
    except Exception as e:
        logger.error(f"Error fetching disease info: {e}")
        disease_info = get_mock_disease_info(disease)
    
    return render_template('disease_details.html', disease_info=disease_info)

def get_mock_disease_info(disease):
    # Mock data for demonstration
    mock_data = {
        'Flu': {
            'name': 'Influenza (Flu)',
            'summary': 'Influenza is a contagious respiratory illness caused by influenza viruses. It can cause mild to severe illness, and at times can lead to death.',
            'url': 'https://medlineplus.gov/flu.html'
        },
        'COVID-19': {
            'name': 'COVID-19',
            'summary': 'COVID-19 is a disease caused by a new coronavirus called SARS-CoV-2. WHO first learned of this new virus on 31 December 2019.',
            'url': 'https://medlineplus.gov/covid19.html'
        }
    }
    return mock_data.get(disease, {
        'name': disease,
        'summary': f'Information about {disease} is not available at the moment. Please consult a healthcare professional.',
        'url': 'https://medlineplus.gov/'
    })

if __name__ == "__main__":
    app.run(debug=True)
