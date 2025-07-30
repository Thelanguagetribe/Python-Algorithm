# 🌍 The Language Tribe

A sophisticated language learning platform that connects language learners with native speakers using an intelligent matching algorithm.

## ✨ Features

### 🧠 Smart Matching Algorithm
- **Language Compatibility**: Exact language matching with secondary language support
- **Proximity-Based Matching**: Uses Haversine formula for accurate distance calculation
- **Age Compatibility**: Matches users within preferred age ranges (configurable)
- **Schedule Synchronization**: Finds overlapping availability between learners and teachers
- **Budget Optimization**: Considers hourly rates and budget constraints
- **Lesson Type Preferences**: Supports in-person, online, or flexible arrangements

### 🎯 Weighted Scoring System
- Language Match: 30%
- Lesson Type Compatibility: 20%
- Proximity (for in-person): 20%
- Age Compatibility: 15%
- Availability Overlap: 10%
- Budget Compatibility: 5%

### 🌐 Beautiful Web Interface
- **Responsive Design**: Modern, mobile-first interface using Bootstrap 5
- **Interactive Dashboard**: Real-time analytics with Chart.js visualizations
- **Profile Management**: Detailed learner and teacher profiles
- **Match Visualization**: Clear compatibility scores and detailed match analysis

### 📊 Analytics & Insights
- Language distribution charts
- Teaching experience analytics
- Lesson type preferences
- Rating and pricing statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/language-tribe.git
   cd language-tribe
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database with sample data**
   ```bash
   python main.py
   ```

4. **Run the web application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🏗️ Project Structure

```
language-tribe/
├── models.py              # Data models and enums
├── matching_algorithm.py  # Core matching logic
├── database.py           # SQLite database operations
├── app.py               # Flask web application
├── main.py              # Demo script with sample data
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   ├── base.html       # Base template with styling
│   ├── index.html      # Home page
│   ├── learners.html   # Language learners page
│   ├── speakers.html   # Native speakers page
│   ├── matches.html    # Matching results page
│   └── dashboard.html  # Analytics dashboard
└── static/             # CSS, JS, and images (auto-generated)
```

## 💡 How It Works

### 1. Data Models
The system uses comprehensive data models for:
- **Language Learners**: Profile, target language, experience level, budget, availability
- **Native Speakers**: Languages taught, experience, rates, availability, ratings
- **Matches**: Compatibility scores, distance, overlapping schedules

### 2. Matching Algorithm
The core `LanguageMatchingAlgorithm` class:
- Evaluates each potential teacher-learner pairing
- Calculates weighted compatibility scores
- Considers geographical proximity using GPS coordinates
- Matches availability windows and time preferences
- Returns ranked results with detailed explanations

### 3. Database Integration
- SQLite database for easy deployment
- JSON serialization for complex data types
- Efficient querying and filtering
- Sample data generation for testing

## 🎨 Design Features

### Modern UI/UX
- **Gradient Backgrounds**: Beautiful purple-to-blue gradients
- **Card-Based Layout**: Clean, organized information display
- **Interactive Elements**: Hover effects and smooth animations
- **Responsive Grid**: Works perfectly on all device sizes
- **Icon Integration**: Font Awesome icons throughout

### Color Scheme
- Primary: `#4f46e5` (Indigo)
- Secondary: `#7c3aed` (Purple)
- Success: `#10b981` (Emerald)
- Warning: `#f59e0b` (Amber)

## 📈 Sample Data

The system includes realistic sample data featuring:
- **4 Language Learners** seeking Spanish, French, German, and Italian
- **5 Native Speakers** from different countries and backgrounds
- **Diverse Profiles** with varying experience levels, rates, and availability
- **Realistic Scenarios** including both online and in-person preferences

## 🔧 Configuration

### Algorithm Weights
Easily adjustable in `matching_algorithm.py`:
```python
self.weights = {
    'language_match': 0.30,
    'lesson_type': 0.20,
    'proximity': 0.20,
    'age_compatibility': 0.15,
    'availability': 0.10,
    'budget_compatibility': 0.05
}
```

### Geographic Settings
```python
self.max_distance_km = 50  # Maximum distance for in-person lessons
self.age_range_years = 10  # Preferred age range
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
The application is ready for deployment on platforms like:
- **Heroku**: Include `Procfile` with `web: gunicorn app:app`
- **Railway**: Built-in Python support
- **PythonAnywhere**: Direct Flask deployment
- **Docker**: Add Dockerfile for containerization

### Environment Variables
For production, set:
- `FLASK_ENV=production`
- `SECRET_KEY=your-secret-key`
- `DATABASE_URL=your-database-url` (if using PostgreSQL)

## 🧪 Testing

### Run the Demo
```bash
python main.py
```
This will:
- Create a fresh database
- Populate with sample data
- Run the matching algorithm
- Display results in the console

### Web Interface Testing
1. Start the web server: `python app.py`
2. Visit the dashboard: `http://localhost:5000/dashboard`
3. Browse learners: `http://localhost:5000/learners`
4. View teachers: `http://localhost:5000/speakers`
5. Test matching: Click "Find Matches" on any learner profile

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Future Enhancements

- **Real-time Chat**: WebSocket-based messaging between users
- **Video Calling**: Integrated video lessons
- **Payment Integration**: Stripe/PayPal integration
- **Review System**: Student feedback and ratings
- **Mobile App**: React Native or Flutter app
- **AI Recommendations**: Machine learning for better matching
- **Multi-language Support**: Internationalization
- **Calendar Integration**: Google Calendar sync

## 📞 Support

For questions or support, please:
- Open an issue on GitHub
- Email: hello@languagetribe.com
- Visit: https://thelanguagetribe.com

---

**Built with ❤️ for language learners worldwide**
