from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sys, os
import pandas as pd
import numpy as np
import joblib
from fuzzywuzzy import fuzz, process
from werkzeug.utils import secure_filename
import requests

# Add src path safely
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
except NameError:
    import pathlib
    sys.path.append(str(pathlib.Path().resolve().parent))

from src.data_preprocessing import load_and_preprocess_data
from src.prediction import SymptomPredictor
from src.logger import setup_logger
from db import authenticate_user, create_user, create_users_table, get_user_id, save_symptom_check, get_user_profile, update_user_profile, get_past_symptom_checks, get_doctors_by_pincode_and_specialty, get_user_demographics, get_symptom_trends, get_system_performance_metrics, get_user_activity_logs, get_db_connection, delete_user, hash_password
from scraper import scrape_disease_info

# Ensure database tables and columns are up to date
create_users_table()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return count
    return 0

def get_symptom_checks_today():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM symptom_checks WHERE DATE(timestamp) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return count
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

@app.route('/admin/data/overview')
@login_required
def get_overview_stats():
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    # Calculate stats
    connection = get_db_connection()
    total_users = 0
    symptom_checks_today = 0
    active_users = 0
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        # Symptom checks today
        cursor.execute("SELECT COUNT(*) FROM symptom_checks WHERE DATE(timestamp) = CURDATE()")
        symptom_checks_today = cursor.fetchone()[0]
        # Active users today (users who checked symptoms today)
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM symptom_checks WHERE DATE(timestamp) = CURDATE()")
        active_users = cursor.fetchone()[0]
        cursor.close()
        connection.close()
    return jsonify(total_users=total_users, symptom_checks_today=symptom_checks_today, active_users=active_users)

@app.route('/admin/delete_user/<username>', methods=['POST'])
@login_required
def delete_user_route(username):
    if getattr(current_user, 'role', 'user') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    if username == 'admin':
        return jsonify({'error': 'Cannot delete admin'}), 400
    if delete_user(username):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to delete'}), 500

predictor = None
df = None
symptoms = []
symptom_descriptions = {}
disease_cache = {}
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
            session['step'] = 4
            return redirect(url_for('symptom_checker'))
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
            # Clear only symptom checker related session data
            session.pop('step', None)
            session.pop('age', None)
            session.pop('sex', None)
            session.pop('selected_symptoms', None)
            session.pop('prediction_result', None)
            session['step'] = 1
            return redirect(url_for('symptom_checker'))

    selected_symptoms = session.get('selected_symptoms', {})
    selected_list = [s for s, sel in selected_symptoms.items() if sel]
    disease_info = None
    if step >= 4:
        disease = session.get('prediction_result', {}).get('primary_prediction', '')
        if disease:
            # Force fresh scraping to test
            try:
                disease_info = scrape_disease_info(disease)
                logger.info(f"Disease info fetched for {disease}: {disease_info}")
                if not disease_info:
                    disease_info = get_mock_disease_info(disease)
                disease_cache[disease] = disease_info
            except Exception as e:
                logger.error(f"Error scraping disease info: {e}")
                disease_info = get_mock_disease_info(disease)
                disease_cache[disease] = disease_info
    return render_template('symptom_checker.html', step=step, symptoms=symptoms, symptom_descriptions=symptom_descriptions, selected_list=selected_list, disease_info=disease_info)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_id = get_user_id(current_user.username)
    if not user_id:
        flash("User not found.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender')
        medical_history = request.form.get('medical_history')
        blood_group = request.form.get('blood_group')
        email = request.form.get('email')
        notifications = request.form.get('notifications')
        avatar = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                avatar = filename
        if update_user_profile(user_id, name, phone, age, gender, medical_history, blood_group, email, notifications, avatar):
            flash("Profile updated successfully!")
        else:
            flash("Failed to update profile.")
        return redirect(url_for('dashboard'))

    profile = get_user_profile(user_id)
    past_checks = get_past_symptom_checks(user_id)

    # Compute symptom trends for the user
    symptom_counts = {}
    for check in past_checks:
        symptoms = json.loads(check['symptoms']) if isinstance(check['symptoms'], str) else check['symptoms']
        for symptom, present in symptoms.items():
            if present:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

    # Add mock data if no real data for demonstration
    if not symptom_counts:
        symptom_counts = {'Fever': 3, 'Cough': 2, 'Headache': 1, 'Fatigue': 2, 'Sore Throat': 1}

    return render_template('dashboard.html', profile=profile, past_checks=past_checks, symptom_counts=symptom_counts)

@app.route('/update_account_settings', methods=['POST'])
@login_required
def update_account_settings():
    user_id = get_user_id(current_user.username)
    if not user_id:
        flash("User not found.")
        return redirect(url_for('dashboard'))

    profile = get_user_profile(user_id)

    username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    email = request.form.get('email') or profile['email']
    notifications = request.form.get('notifications') or profile['notifications']

    # Verify current password if provided
    if current_password and not authenticate_user(current_user.username, current_password):
        flash("Current password is incorrect.")
        return redirect(url_for('dashboard'))

    # Check if username is changing and available
    if 'username' in request.form and username and username != current_user.username:
        if get_user_id(username):
            flash("Username already taken.")
            return redirect(url_for('dashboard'))
        # Update username in DB
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            # Update current_user
            current_user.username = username

    # Update password if provided
    if 'new_password' in request.form and new_password:
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('dashboard'))
        hashed_password = hash_password(new_password)
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, user_id))
            connection.commit()
            cursor.close()
            connection.close()

    # Update email if provided
    if 'email' in request.form and request.form.get('email'):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
            connection.commit()
            cursor.close()
            connection.close()

    # Update notifications if provided
    if 'notifications' in request.form and request.form.get('notifications'):
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET notifications = %s WHERE id = %s", (notifications, user_id))
            connection.commit()
            cursor.close()
            connection.close()

    flash("Account settings updated successfully!")
    return redirect(url_for('dashboard'))

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

@app.route('/api/health_news')
def health_news():
    api_key = os.environ.get('REACT_APP_NEWS_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
    try:
        url = f'https://newsapi.org/v2/top-headlines?category=health&apiKey={api_key}&pageSize=6'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        # Filter or format as needed
        news = []
        for article in articles:
            news.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'urlToImage': article.get('urlToImage', '')
            })
        return jsonify(news)
    except requests.RequestException as e:
        logger.error(f"Error fetching health news: {e}")
        return jsonify({'error': 'Failed to fetch news'}), 500

@app.route('/disease_details/<disease>')
def disease_details(disease):
    # Fetch disease details using the scraper with caching
    if disease in disease_cache:
        logger.info(f"Using cached data for disease: {disease}")
        disease_info = disease_cache[disease]
    else:
        logger.info(f"Scraping data for disease: {disease}")
        try:
            disease_info = scrape_disease_info(disease)
            if not disease_info:
                disease_info = get_mock_disease_info(disease)
            disease_cache[disease] = disease_info
        except Exception as e:
            logger.error(f"Error scraping disease info: {e}")
            disease_info = get_mock_disease_info(disease)
            disease_cache[disease] = disease_info

    return render_template('disease_details.html', disease_info=disease_info)

@app.route('/disease_details/<disease>/treatments')
def disease_treatments(disease):
    # Fetch treatments for the disease
    if disease in disease_cache:
        disease_info = disease_cache[disease]
    else:
        try:
            disease_info = scrape_disease_info(disease)
            if not disease_info:
                disease_info = {'name': disease, 'treatments': [], 'source': ''}
            disease_cache[disease] = disease_info
        except Exception as e:
            logger.error(f"Error scraping disease info: {e}")
            disease_info = {'name': disease, 'treatments': [], 'source': ''}

    return render_template('disease_treatments.html', disease_info=disease_info)

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
    app.run(debug=True, port=5001)
