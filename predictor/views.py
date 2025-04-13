import joblib
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Blog, Prediction
import json
import logging
from .services.prediction_service import DiabetesPredictor

# Initialize the predictor at module level
predictor = DiabetesPredictor()


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the Random Forest model and scaler globally
MODEL_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'random_forest_diabetes_model.joblib')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'scaler.joblib')

try:
    diabetes_model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    logger.info("Machine learning model and scaler loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model or scaler: {str(e)}")
    raise  # Stop the server if loading fails

# Authentication Views
def index_view(request):
    context = {'user_name': request.session.get('user_name')}
    return render(request, 'index.html', context)

def login_view(request):
    context = {'user_name': request.session.get('user_name')}
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        logger.debug(f"Login attempt for username: {user_name}")
        try:
            user = User.objects.get(user_name=user_name)
            if user.check_password(password):
                logger.info(f"Successful login for {user_name}")
                request.session['user_name'] = user.user_name
                request.session['email'] = user.email
                return redirect('predictor:dashboard')
            else:
                logger.warning(f"Incorrect password for {user_name}")
                return render(request, 'login.html', {'error_message': 'Invalid username or password', **context})
        except User.DoesNotExist:
            logger.warning(f"Login attempt for non-existent user: {user_name}")
            return render(request, 'login.html', {'error_message': 'Invalid username or password', **context})
    return render(request, 'login.html', context)

def signup_view(request):
    context = {'user_name': request.session.get('user_name')}
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        retype_password = request.POST.get('retype_password')
        if not all([user_name, email, password, retype_password]):
            return render(request, 'signup.html', {'error_message': 'All fields are required', **context})
        if password != retype_password:
            return render(request, 'signup.html', {'error_message': 'Passwords do not match', **context})
        if User.objects.filter(user_name=user_name).exists() or User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'User already exists', **context})
        user = User.objects.create(user_name=user_name, email=email, password=password)
        user.save()
        logger.info(f"New user created: {user_name}")
        return redirect('predictor:login')
    return render(request, 'signup.html', context)

def logout_view(request):
    if 'user_name' in request.session:
        logger.info(f"User {request.session['user_name']} logged out")
        del request.session['user_name']
    return redirect('predictor:login')

# Dashboard and Content Views
def dashboard_view(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('predictor:login')
    try:
        user = User.objects.get(user_name=user_name)
        predictions = Prediction.objects.filter(user=user).order_by('-created_at')
        context = {
            'name': user.user_name,
            'email': user.email,
            'age': user.age if user.age else 'Not provided',
            'gender': getattr(user, 'gender', 'Not provided'),
            'user_name': user_name,
            'predictions': predictions,
            'latest_prediction': predictions.first() if predictions.exists() else None,
        }
        return render(request, 'dashboard.html', context)
    except User.DoesNotExist:
        if 'user_name' in request.session:
            del request.session['user_name']
        return redirect('predictor:login')

def blog_view(request):
    user_name = request.session.get('user_name')
    if request.method == 'POST':
        if not user_name:
            return JsonResponse({'success': False, 'message': 'Login required'}, status=403)
        try:
            user = User.objects.get(user_name=user_name)
            data = json.loads(request.POST.get('data'))
            title, content = data.get('title'), data.get('content')
            image = request.FILES.get('image')
            if image and not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return JsonResponse({'success': False, 'message': 'Invalid image format'}, status=400)
            if not (title and content):
                return JsonResponse({'success': False, 'message': 'Title and content required'}, status=400)
            blog = Blog.objects.create(title=title, content=content, image=image, author=user)
            author_display = "Created by you" if user.user_name == user_name else f"Created by {user.user_name}"
            return JsonResponse({
                'success': True,
                'id': blog.id,
                'title': blog.title,
                'content': blog.content,
                'image_url': blog.image.url if blog.image else None,
                'author_display': author_display,
                'created_at': blog.created_at.strftime('%B %d, %Y'),
                'author_age': user.age if user.age else 'Not provided'
            })
        except Exception as e:
            logger.error(f"Blog creation error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    context = {'blogs': Blog.objects.all().order_by('-created_at'), 'user_name': user_name}
    return render(request, 'blog.html', context)

# Prediction View with Machine Learning
@csrf_exempt
def predict_view(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('predictor:login')

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')).get('data', {})
            user = User.objects.get(user_name=user_name)

            # Extract form data (add diabetes_pedigree)
            gender = data.get('gender')
            age = int(data.get('age'))
            weight = float(data.get('weight'))
            height = float(data.get('height'))
            pregnancies = int(data.get('pregnancies', 0)) if gender == 'female' else None
            glucose = float(data.get('glucose'))
            blood_pressure = float(data.get('bloodPressure'))
            skin_thickness = float(data.get('skinThickness'))
            insulin = float(data.get('insulin'))
            diabetes_pedigree = float(data.get('diabetesPedigree'))  # New field

            # Update user's age and gender
            user.age = age
            user.gender = gender
            user.save()

            # Make prediction using ML model
            prediction_result = predictor.predict({
                'gender': gender,
                'age': age,
                'weight': weight,
                'height': height,
                'pregnancies': pregnancies,
                'glucose': glucose,
                'blood_pressure': blood_pressure,
                'skin_thickness': skin_thickness,
                'insulin': insulin,
                'diabetes_pedigree': diabetes_pedigree  # New field
            })

            # Save prediction with BMI
            prediction = Prediction.objects.create(
                user=user,
                gender=gender,
                age=age,
                weight=weight,
                height=height,
                bmi=prediction_result['bmi'],
                pregnancies=pregnancies,
                glucose=glucose,
                blood_pressure=blood_pressure,
                skin_thickness=skin_thickness,
                insulin=insulin,
                diabetes_pedigree=diabetes_pedigree,  # New field
                risk_level=prediction_result['risk_level'],
                probability=prediction_result['probability']
            )

            return JsonResponse({
                'success': True,
                'redirect_url': '/dashboard/',
                'risk_level': prediction_result['risk_level'],
                'probability': prediction_result['probability'],
                'prediction_id': prediction.id
            })
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return render(request, 'predict.html', {'user_name': user_name})