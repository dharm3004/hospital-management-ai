# Hospital AI  Professional Hospital Management System with AI Diagnosis

A modern, responsive Django web application for hospital management with integrated AI diagnosis using machine learning.

## Features

- **AI Diagnosis**: Uses `model_data.pkl` to predict top 3 diseases based on selected symptoms.
- **User Roles**: Separate dashboards for patients and doctors.
- **Appointment Booking**: Patients can book appointments with doctors.
- **Doctor Availability**: Doctors can set their available time slots.
- **Prescription Management**: Doctors can add prescriptions.
- **Prediction History**: Track user prediction history.
- **Admin Panel**: Manage all data via Django Admin.
- **Responsive UI**: Bootstrap 5 with custom animations and modern design.
- **Security**: CSRF protection, role-based access, form validation.

## Tech Stack

- **Backend**: Python, Django, SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **AI/ML**: Scikit-learn (model in `model_data.pkl`)

## Setup

1. Clone or download the project.

2. Create virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate venv:
   - Windows: `.\.venv\Scripts\Activate.ps1`
   - Linux/Mac: `source .venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser (optional for admin):
   ```bash
   python manage.py createsuperuser
   ```

7. Start server:
   ```bash
   python manage.py runserver
   ```

8. Open `http://127.0.0.1:8000/` in browser.

## Usage

- **Register** as patient or doctor.
- **Login** to access dashboard.
- **AI Diagnosis**: Select symptoms, get top 3 predictions with probabilities.
- **Book Appointments**: Patients can book with doctors.
- **Manage Availability**: Doctors set time slots.
- **Admin**: `http://127.0.0.1:8000/admin/` (use superuser credentials).

## Model Integration

The app loads `model_data.pkl` which should contain a dict with 'model' (sklearn estimator) and 'features' (list of symptom names). Ensure the model has `predict_proba` method.

## Tests

Run unit tests:
```bash
python manage.py test predictor
```

## Production Notes

- Set `DJANGO_SECRET_KEY` environment variable.
- Set `DEBUG=False` and configure static files serving.
- Use PostgreSQL for production database.
- Add HTTPS and security headers.
