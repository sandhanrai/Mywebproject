# MediCheck - AI-Powered Health Symptom Checker

MediCheck is a comprehensive web-based health symptom checker application that uses machine learning to analyze user symptoms and provide possible disease predictions. The application combines AI-driven diagnostics with detailed medical information scraped from reliable sources like MedlinePlus.

## 🚀 Features

### Core Functionality
- **AI Symptom Analysis**: Machine learning-powered disease prediction based on user-reported symptoms
- **Multi-Step Symptom Checker**: Guided process for accurate symptom input and analysis
- **Disease Details**: Comprehensive information including causes, symptoms, diagnosis, prevention, and treatments
- **Doctor Finder**: Search for healthcare professionals by location and specialty
- **Health News**: Real-time health-related news integration via NewsAPI
- **User Dashboard**: Personal health tracking and profile management

### User Management
- **Authentication**: Secure user registration and login system
- **Profile Management**: Complete user profiles with medical history, demographics, and preferences
- **Past Checks History**: Track and review previous symptom analyses
- **Account Settings**: Update username, password, email, and notification preferences

### Admin Features
- **Analytics Dashboard**: System-wide statistics and user demographics
- **User Management**: View and manage user accounts
- **Performance Metrics**: Monitor system usage and prediction trends
- **Activity Logs**: Track user interactions and system events

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework for Python
- **MySQL**: Database for user data and symptom checks
- **Scikit-learn**: Machine learning library for disease prediction
- **BeautifulSoup**: Web scraping for medical information
- **bcrypt**: Password hashing for security

### Frontend
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Icon library
- **Tailwind CSS**: Utility-first CSS framework
- **SweetAlert2**: Enhanced alert dialogs
- **Chart.js**: Data visualization

### Machine Learning
- **Random Forest**: Primary prediction model (optimized via GridSearchCV)
- **Alternative Models**: Decision Tree, SVM, Multinomial Naive Bayes
- **Data Preprocessing**: Standard and MinMax scaling
- **Feature Engineering**: Symptom-based binary classification

## 📊 Dataset

The application uses a comprehensive medical dataset containing:
- **41 Diseases**: Including common conditions like flu, diabetes, hypertension, etc.
- **132 Symptoms**: Binary symptom indicators
- **4920 Records**: Training data for machine learning models
- **Sources**: MedlinePlus for detailed medical information

## 🏗️ Architecture

```
health-symptom-checker/
├── app/                    # Flask application
│   ├── __init__.py
│   ├── app.py             # Main Flask application
│   ├── db.py              # Database operations
│   ├── scraper.py         # MedlinePlus web scraper
│   ├── templates/         # Jinja2 templates
│   └── static/            # Static assets
├── src/                   # Source code
│   ├── data_preprocessing.py
│   ├── prediction.py
│   ├── model_training.py
│   └── logger.py
├── data/                  # Datasets and URLs
├── models/                # Trained ML models
├── tests/                 # Unit tests
└── requirements.txt       # Python dependencies
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- pip package manager

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/health-symptom-checker.git
cd health-symptom-checker
```

### 2. Create Virtual Environment
```bash
# Using the provided script
./setup_venv_and_install.sh

# Or manually
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Configure MySQL connection in .env file
# Example:
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=health_symptom_checker

# Run database setup
python setup_db.py
```

### 5. Train Machine Learning Model
```bash
python src/model_training.py
```

### 6. Run Application
```bash
python app/app.py
```

Visit `http://localhost:5001` in your browser.

## 🔧 Configuration

### Environment Variables (.env)
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_symptom_checker
REACT_APP_NEWS_API_KEY=your_newsapi_key
SECRET_KEY=your_flask_secret_key
```

### Database Schema
- **users**: User accounts and profiles
- **symptom_checks**: Stored symptom analysis results
- **doctors**: Healthcare provider information

## 🤖 Machine Learning Pipeline

### Model Training
1. **Data Loading**: Import disease-symptom dataset
2. **Preprocessing**: Feature scaling and encoding
3. **Model Selection**: Compare multiple algorithms
4. **Hyperparameter Tuning**: Grid search optimization
5. **Evaluation**: Cross-validation and metrics analysis

### Prediction Process
1. **Symptom Input**: User selects symptoms via web interface
2. **Feature Vector**: Convert symptoms to model input format
3. **Prediction**: Generate disease probabilities
4. **Results**: Return top predictions with confidence scores

## 🌐 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET/POST /login` - User authentication
- `GET/POST /signup` - User registration
- `GET/POST /symptom_checker` - Main symptom analysis
- `GET/POST /find_doctor` - Healthcare provider search

### Protected Endpoints
- `GET /dashboard` - User profile and history
- `POST /update_account_settings` - Account management
- `GET /admin` - Admin dashboard (admin only)

### API Routes
- `GET /api/symptom_suggestions` - Fuzzy symptom search
- `GET /api/health_news` - Latest health news
- `GET /disease_details/<disease>` - Detailed disease information

## 🧪 Testing

### Unit Tests
```bash
python -m unittest tests/test_scraper.py
```

### Manual Testing
- Run `temp_scraper_test.py` for scraper validation
- Use `test_scraper_debug.py` for debugging
- Check `user_interactions.log` for application logs

## 📈 Performance Metrics

### Model Accuracy
- **Random Forest**: ~95% accuracy (primary model)
- **Decision Tree**: ~90% accuracy
- **SVM**: ~92% accuracy
- **Naive Bayes**: ~88% accuracy

### System Performance
- Response time: <2 seconds for predictions
- Concurrent users: Supports multiple simultaneous sessions
- Database queries: Optimized for fast retrieval

## 🔒 Security Features

- **Password Hashing**: bcrypt encryption
- **Session Management**: Flask-Session with filesystem storage
- **Input Validation**: Server-side form validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Template escaping

## 📱 Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Progressive Enhancement**: Works on all screen sizes
- **Accessibility**: WCAG compliant design
- **Cross-Browser**: Compatible with modern browsers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**MediCheck is not a substitute for professional medical advice, diagnosis, or treatment.** Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read on this application.

## 📞 Support

- **Email**: support@medicheck.com
- **Emergency**: Call 911 for immediate medical assistance
- **Documentation**: See inline code comments and docstrings

## 🔄 Future Enhancements

- [ ] Integration with electronic health records
- [ ] Multi-language support
- [ ] Advanced analytics and reporting
- [ ] Mobile application development
- [ ] Integration with telemedicine platforms
- [ ] Enhanced ML models with larger datasets

---

**Built with ❤️ for better health outcomes**