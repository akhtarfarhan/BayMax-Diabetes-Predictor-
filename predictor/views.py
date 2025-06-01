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
from django.contrib import messages
import re
from django.urls import reverse
from django.db import IntegrityError
from django.db import transaction

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

def start_prediction(request):
    user_name = request.session.get('user_name')
    if user_name:
        try:
            User.objects.get(user_name=user_name)
            return redirect('predictor:predict')
        except User.DoesNotExist:
            if 'user_name' in request.session:
                del request.session['user_name']
            return redirect('predictor:login')
    return redirect('predictor:login')

def login_view(request):
    if request.method == 'POST':
        logger.debug(f"Received POST request: {request.POST}")
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        
        if not username or not password:
            error_msg = 'Username and password are required'
            logger.debug(f"Missing credentials: username={username}")
            messages.error(request, error_msg)
            return render(request, 'login.html')
        
        try:
            user = User.objects.get(user_name=username)
            if user.check_password(password):
                request.session['user_name'] = user.user_name
                request.session['email'] = user.email
                request.session.modified = True
                logger.info(f"User {username} authenticated, session set: user_name={user.user_name}, email={user.email}")
                return redirect('predictor:dashboard')  # Redirect to dashboard instead of predict
            else:
                error_msg = 'Invalid username or password'
                logger.debug(f"Password check failed for user {username}")
                messages.error(request, error_msg)
        except User.DoesNotExist:
            error_msg = 'Invalid username or password'
            logger.debug(f"User {username} does not exist")
            messages.error(request, error_msg)
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")
        
        return render(request, 'login.html')
    
    logger.debug("Rendering login page")
    return render(request, 'login.html')

@csrf_exempt
def check_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            exists = User.objects.filter(user_name__iexact=username).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def signup_view(request):
    if request.method == 'POST':
        logger.debug(f"Received POST request: {request.POST}")
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        errors = {}
        
        if User.objects.filter(user_name__iexact=username).exists():
            errors['username'] = 'Username already exists'
            logger.debug(f"Duplicate username detected: {username}")
        if User.objects.filter(email__iexact=email).exists():
            errors['email'] = 'Email already exists'
            logger.debug(f"Duplicate email detected: {email}")
        
        if not username:
            errors['username'] = 'Username is required'
        elif len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters'
        
        if not email:
            errors['email'] = 'Email is required'
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors['email'] = 'Enter a valid email address'
        
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        elif not re.search(r'[A-Z]', password):
            errors['password'] = 'Password must contain at least one uppercase letter'
        elif not re.search(r'[0-9]', password):
            errors['password'] = 'Password must contain at least one number'
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors['password'] = 'Password must contain at least one special character'
        
        if password != password2:
            errors['password2'] = 'Passwords do not match'
        
        if errors:
            logger.debug(f"Validation errors: {errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # For AJAX requests, return JSON errors
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            else:
                # For non-AJAX requests, render the form with errors
                for field, error in errors.items():
                    messages.error(request, f"{field}: {error}")
                return render(request, 'signup.html')
        
        try:
            user = User.objects.create(
                user_name=username,
                email=email,
                password=password
            )
            logger.info(f"User created: {username}")
            request.session['user_name'] = user.user_name
            request.session['email'] = user.email
            request.session.modified = True
            messages.success(request, 'Account created successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # For AJAX requests, return JSON with redirect URL
                redirect_url = reverse('predictor:login')  # Redirect to login page after signup
                return JsonResponse({'success': True, 'redirect_url': redirect_url})
            else:
                # For non-AJAX requests, perform HTTP redirect
                return redirect('predictor:login')  # Redirect to login after signup
        except IntegrityError as e:
            logger.error(f"IntegrityError during user creation: {str(e)}")
            if 'user_name' in str(e).lower():
                errors['username'] = 'Username already exists'
            elif 'email' in str(e).lower():
                errors['email'] = 'Email already exists'
            else:
                errors['general'] = 'An error occurred during account creation. Please try again.'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            else:
                for field, error in errors.items():
                    messages.error(request, f"{field}: {error}")
                return render(request, 'signup.html')
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': {'general': f"An unexpected error occurred: {str(e)}"}}, status=500)
            else:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return render(request, 'signup.html')
    
    logger.debug("Rendering signup page")
    return render(request, 'signup.html')

@csrf_exempt
def check_signup_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            exists = User.objects.filter(user_name__iexact=username).exists()
            return JsonResponse({'available': not exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def check_signup_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            exists = User.objects.filter(email__iexact=email).exists()
            return JsonResponse({'available': not exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def logout_view(request):
    if 'user_name' in request.session:
        logger.info(f"User {request.session['user_name']} logged out")
        del request.session['user_name']
        if 'email' in request.session:
            del request.session['email']
    return redirect('predictor:login')

def dashboard_view(request):
    user_name = request.session.get('user_name')
    if not user_name:
        logger.warning("Unauthorized access attempt to dashboard")
        return redirect('predictor:login')
    
    try:
        user = User.objects.get(user_name=user_name)
        predictions = Prediction.objects.filter(user=user).order_by('-created_at')
        context = {
            'name': user.user_name,
            'email': user.email,
            'age': user.age if user.age is not None else 'Not provided',
            'gender': user.gender if user.gender else 'Not provided',
            'user_name': user_name,
            'predictions': predictions,
            'latest_prediction': predictions.first() if predictions.exists() else None,
        }
        logger.debug(f"Rendering dashboard for user {user_name} with context: {context}")
        return render(request, 'dashboard.html', context)
    except User.DoesNotExist:
        logger.error(f"User {user_name} not found")
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

@csrf_exempt
def predict_view(request):
    user_name = request.session.get('user_name')
    if not user_name:
        logger.warning("Unauthorized access attempt to predict view")
        return redirect('predictor:login')
    
    try:
        user = User.objects.get(user_name=user_name)
    except User.DoesNotExist:
        logger.error(f"User {user_name} not found")
        if 'user_name' in request.session:
            del request.session['user_name']
        return redirect('predictor:login')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')).get('data', {})
            
            # Extract form data
            gender = data.get('gender')
            age = int(data.get('age'))
            weight = float(data.get('weight'))
            height = float(data.get('height'))
            pregnancies = int(data.get('pregnancies', 0)) if gender == 'female' else None
            glucose = float(data.get('glucose'))
            blood_pressure = float(data.get('bloodPressure'))
            skin_thickness = float(data.get('skinThickness'))
            insulin = float(data.get('insulin'))
            diabetes_pedigree = float(data.get('diabetesPedigree'))

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
                'diabetes_pedigree': diabetes_pedigree
            })

            # Update user's age and gender in the database
            user.age = age
            user.gender = gender
            user.save()
            logger.info(f"Updated user {user_name} with age={age} and gender={gender}")

            # Save prediction
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
                diabetes_pedigree=diabetes_pedigree,
                risk_level=prediction_result['risk_level'],
                diabetes_probability=prediction_result['diabetes_probability'],
                health_tips=json.dumps(prediction_result['health_tips'])
            )
            logger.info(f"Prediction saved for user {user_name}: {prediction.id}")

            # Return the prediction result with dashboard URL
            return JsonResponse({
                'success': True,
                'risk_level': prediction_result['risk_level'],
                'diabetes_probability': prediction_result['diabetes_probability'],
                'health_tips': prediction_result['health_tips'],
                'bmi': prediction_result['bmi'],
                'dashboard_url': reverse('predictor:dashboard')
            })
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return render(request, 'predict.html', {'user_name': user_name})

@csrf_exempt
def predict_unauthenticated_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')).get('data', {})
            
            # Extract form data
            gender = data.get('gender')
            age = int(data.get('age'))
            weight = float(data.get('weight'))
            height = float(data.get('height'))
            pregnancies = int(data.get('pregnancies', 0)) if gender == 'female' else None
            glucose = float(data.get('glucose'))
            blood_pressure = float(data.get('bloodPressure'))
            skin_thickness = float(data.get('skinThickness'))
            insulin = float(data.get('insulin'))
            diabetes_pedigree = float(data.get('diabetesPedigree'))

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
                'diabetes_pedigree': diabetes_pedigree
            })

            # Return the prediction result without saving
            return JsonResponse({
                'success': True,
                'risk_level': prediction_result['risk_level'],
                'diabetes_probability': prediction_result['diabetes_probability'],
                'health_tips': prediction_result['health_tips'],
                'bmi': prediction_result['bmi']
            })
        except Exception as e:
            logger.error(f"Unauthenticated prediction error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return render(request, 'predict_unauthenticated.html', {})

def glucose_trends_view(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('predictor:login')
    return render(request, 'glucose_trends.html', {'user_name': user_name})

@csrf_exempt
def glucose_data_api(request):
    user_name = request.session.get('user_name')
    logger.debug(f"Glucose data API called for user: {user_name}")
    if not user_name:
        logger.warning("Unauthorized access attempt to glucose data API")
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        with transaction.atomic():  # Use transaction context manager
            user = User.objects.get(user_name=user_name)
            logger.debug(f"User found: {user.user_name}")
            predictions = Prediction.objects.filter(user=user).order_by('created_at')
            logger.debug(f"Found {predictions.count()} predictions for user {user_name}")
            data = [{'date': pred.created_at.strftime('%Y-%m-%d'), 'glucose': pred.glucose} for pred in predictions]
            if not data:
                logger.warning(f"No glucose data available for user {user_name}")
                return JsonResponse({'error': 'No glucose data available'}, status=404)
            logger.debug(f"Returning glucose data: {data}")
            return JsonResponse(data, safe=False)
    except User.DoesNotExist:
        logger.error(f"User {user_name} not found")
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in glucose_data_api: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)