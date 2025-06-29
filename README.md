# BayMax (Diabetes Predictor)

BayMax is an intelligent, full-stack web application designed to help users track, predict, and manage their health with a focus on diabetes. Built with Django, MySQL, and a modern frontend, it incorporates AI-driven predictions, health analytics, and a supportive community blog.

---

## Overview

BayMax serves both medical and non-medical users, including diabetes patients and anyone interested in monitoring their health. The system provides diabetes risk prediction, comprehensive dashboards, and personalized health suggestions based on user data. Additionally, it includes a blog for users to share their health journeys and tips.

## Features

- **AI-powered Diabetes Prediction:** Instantly predict diabetes risk based on health metrics such as BMI, age, gender, and glucose level.
- **Personalized Dashboard:** Visualize and track your health data, including glucose charts for monitoring trends over time.
- **Diet & Health Recommendations:** Get tailored suggestions based on your health profile to support better lifestyle choices.
- **Guest Prediction:** Use the diabetes prediction tool without registration; data is still saved for dashboard review.
- **Community Blog:** Share experiences, tips, and health journeys with other users.
- **Modern Web Interface:** Includes home, login, registration, blog, and prediction pages. Users can check diabetes risk even without logging in.

## Intended Users

- **Medical Professionals:** For patient monitoring and consultation.
- **General Public:** For health tracking, diabetes risk assessment, and community support.

## Technology Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL (managed via XAMPP)
- **Machine Learning:** Integrated AI/ML model for diabetes prediction

## Getting Started

### Prerequisites

- Python 3.10 and more
- Django
- XAMPP (for MySQL database)
- (Optional) Node.js for advanced frontend workflows

### Setup Instructions

1. **Clone the Repository**
    ```bash
    git clone https://github.com/akhtarfarhan/BayMax.git
    cd BayMax
    ```

2. **Set Up Virtual Environment**
    ```bash
    python -m venv env
    source env/bin/activate      # On Unix/macOS
    .\env\Scripts\activate       # On Windows
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure MySQL via XAMPP**
    - Start MySQL using XAMPP.
    - Import the provided SQL schema into your MySQL server.
    - Update your Django `settings.py` with your database credentials.

5. **Run Database Migrations**
    ```bash
    python manage.py migrate
    ```

6. **Start the Development Server**
    ```bash
    python manage.py runserver
    ```

7. **Access the Application**
    - Open your browser and navigate to [http://localhost:8000](http://localhost:8000)

## Project Structure

```
BayMax/
├── baymax/                   # Django project source code
├── static/                   # Static frontend files (CSS, JS, images)
├── templates/                # HTML templates
├── requirements.txt          # Python dependencies
├── db_schema.sql             # MySQL database schema (if provided)
└── README.md                 # Project documentation
```

## Usage

- **Register/Login:** Create an account for personalized tracking.
- **Diabetes Prediction:** Use the prediction tool as a guest or logged-in user.
- **Dashboard:** Analyze and visualize your health data.
- **Glucose Chart:** Track your glucose levels over time.
- **Blog:** Share and read health stories, tips, and experiences.
- **Health Suggestions:** Receive AI-driven recommendations for diet and lifestyle.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or documentation improvements.

## License

[Specify your license here, e.g., MIT, GPL-3.0, etc.]

---

_Developed by [akhtarfarhan](https://github.com/akhtarfarhan)_
