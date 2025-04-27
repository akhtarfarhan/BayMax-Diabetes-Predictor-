# import joblib
# import os
# from django.conf import settings
# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import User, Blog, Prediction
# import json
# import logging
# from .services.prediction_service import DiabetesPredictor
# from django.contrib import messages
# import re

# # Initialize the predictor at module level
# predictor = DiabetesPredictor()


# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Load the Random Forest model and scaler globally
# MODEL_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'random_forest_diabetes_model.joblib')
# SCALER_PATH = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'scaler.joblib')

# try:
#     diabetes_model = joblib.load(MODEL_PATH)
#     scaler = joblib.load(SCALER_PATH)
#     logger.info("Machine learning model and scaler loaded successfully.")
# except Exception as e:
#     logger.error(f"Error loading model or scaler: {str(e)}")
#     raise  # Stop the server if loading fails

# # Authentication Views
# def index_view(request):
#     context = {'user_name': request.session.get('user_name')}
#     return render(request, 'index.html', context)


# #Login View
# logger = logging.getLogger(__name__)

# def login_view(request):
#        if request.method == 'POST':
#            logger.debug(f"Received POST request: {request.headers}")
#            if request.headers.get('Content-Type') == 'application/json':
#                try:
#                    data = json.loads(request.body)
#                    logger.debug(f"JSON data: {data}")
#                    username = data.get('username')
#                    password = data.get('password')
#                except json.JSONDecodeError as e:
#                    logger.error(f"JSON decode error: {str(e)}")
#                    return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
#            else:
#                username = request.POST.get('username')
#                password = request.POST.get('password')
           
#            if not username or not password:
#                error_msg = 'Username and password are required'
#                logger.debug(f"Missing credentials: username={username}")
#                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
#                else:
#                    messages.error(request, error_msg)
#                    return render(request, 'login.html')
           
#            try:
#                user = User.objects.get(user_name=username)
#                if user.check_password(password):
#                    request.session['user_name'] = user.user_name
#                    request.session['email'] = user.email
#                    logger.info(f"User {username} authenticated, session set: user_name={user.user_name}, email={user.email}")
#                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                        return JsonResponse({
#                            'success': True, 
#                            'redirect_url': reverse('predictor:dashboard')
#                        })
#                    else:
#                        return redirect('predictor:dashboard')
#                else:
#                    error_msg = 'Invalid username or password'
#                    logger.debug(f"Password check failed for user {username}")
#            except User.DoesNotExist:
#                error_msg = 'Invalid username or password'
#                logger.debug(f"User {username} does not exist")
           
#            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                return JsonResponse({'success': False, 'error': error_msg}, status=400)
#            else:
#                messages.error(request, error_msg)
       
#        logger.debug("Rendering login page")
#        return render(request, 'login.html')

# #Username
# @csrf_exempt
# def check_username(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             username = data.get('username', '').strip()
            
#             # Check if username exists
#             exists = User.objects.filter(user_name__iexact=username).exists()
            
#             return JsonResponse({'exists': exists})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

# # Signup View
# logger = logging.getLogger(__name__)

#    def signup_view(request):
#        if request.method == 'POST':
#            logger.debug(f"Received POST request: {request.POST}")
#            username = request.POST.get('username', '').strip()
#            email = request.POST.get('email', '').strip()
#            password = request.POST.get('password')
#            password2 = request.POST.get('password2')
           
#            errors = {}
           
#            # Username validation
#            if not username:
#                errors['username'] = 'Username is required'
#            elif len(username) < 3:
#                errors['username'] = 'Username must be at least 3 characters'
#            elif User.objects.filter(user_name__iexact=username).exists():
#                errors['username'] = 'Username already exists'
           
#            # Email validation
#            if not email:
#                errors['email'] = 'Email is required'
#            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
#                errors['email'] = 'Enter a valid email address'
#            elif User.objects.filter(email__iexact=email).exists():
#                errors['email'] = 'Email already exists'
           
#            # Password validation
#            if not password:
#                errors['password'] = 'Password is required'
#            elif len(password) < 8:
#                errors['password'] = 'Password must be at least 8 characters'
#            elif not re.search(r'[A-Z]', password):
#                errors['password'] = 'Password must contain at least one uppercase letter'
#            elif not re.search(r'[0-9]', password):
#                errors['password'] = 'Password must contain at least one number'
#            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
#                errors['password'] = 'Password must contain at least one special character'
           
#            # Password confirmation
#            if password != password2:
#                errors['password2'] = 'Passwords do not match'
           
#            if errors:
#                logger.debug(f"Validation errors: {errors}")
#                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                    return JsonResponse({'errors': errors}, status=400)
#                else:
#                    for field, error in errors.items():
#                        messages.error(request, f"{field}: {error}")
#                    return render(request, 'signup.html')
           
#            # Create user
#            try:
#                user = User.objects.create(
#                    user_name=username,
#                    email=email,
#                    password=password  # Password will be hashed in the model's save method
#                )
#                logger.info(f"User created: {username}")
#                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                    return JsonResponse({'success': True, 'redirect_url': reverse('predictor:login')})
#                else:
#                    messages.success(request, 'Account created successfully! Please log in.')
#                    return redirect('predictor:login')
#            except Exception as e:
#                error_msg = 'An error occurred during account creation. Please try again.'
#                logger.error(f"User creation error: {str(e)}")
#                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                    return JsonResponse({'errors': {'__all__': error_msg}}, status=400)
#                else:
#                    messages.error(request, error_msg)
#                    return render(request, 'signup.html')
       
#        logger.debug("Rendering signup page")
#        return render(request, 'signup.html')


# @csrf_exempt
# def check_signup_username(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             username = data.get('username', '').strip()
            
#             # Check if username exists
#             exists = User.objects.filter(user_name__iexact=username).exists()
            
#             return JsonResponse({'available': not exists})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

# @csrf_exempt
# def check_signup_email(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email', '').strip()
            
#             # Check if email exists
#             exists = User.objects.filter(email__iexact=email).exists()
            
#             return JsonResponse({'available': not exists})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

# # Logout View
# def logout_view(request):
#     if 'user_name' in request.session:
#         logger.info(f"User {request.session['user_name']} logged out")
#         del request.session['user_name']
#     return redirect('predictor:login')

# # Dashboard and Content Views
# def dashboard_view(request):
#     user_name = request.session.get('user_name')
#     if not user_name:
#         return redirect('predictor:login')
#     try:
#         user = User.objects.get(user_name=user_name)
#         predictions = Prediction.objects.filter(user=user).order_by('-created_at')
#         context = {
#             'name': user.user_name,
#             'email': user.email,
#             'age': user.age if user.age else 'Not provided',
#             'gender': getattr(user, 'gender', 'Not provided'),
#             'user_name': user_name,
#             'predictions': predictions,
#             'latest_prediction': predictions.first() if predictions.exists() else None,
#         }
#         return render(request, 'dashboard.html', context)
#     except User.DoesNotExist:
#         if 'user_name' in request.session:
#             del request.session['user_name']
#         return redirect('predictor:login')

# # Blog View
# def blog_view(request):
#     user_name = request.session.get('user_name')
#     if request.method == 'POST':
#         if not user_name:
#             return JsonResponse({'success': False, 'message': 'Login required'}, status=403)
#         try:
#             user = User.objects.get(user_name=user_name)
#             data = json.loads(request.POST.get('data'))
#             title, content = data.get('title'), data.get('content')
#             image = request.FILES.get('image')
#             if image and not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
#                 return JsonResponse({'success': False, 'message': 'Invalid image format'}, status=400)
#             if not (title and content):
#                 return JsonResponse({'success': False, 'message': 'Title and content required'}, status=400)
#             blog = Blog.objects.create(title=title, content=content, image=image, author=user)
#             author_display = "Created by you" if user.user_name == user_name else f"Created by {user.user_name}"
#             return JsonResponse({
#                 'success': True,
#                 'id': blog.id,
#                 'title': blog.title,
#                 'content': blog.content,
#                 'image_url': blog.image.url if blog.image else None,
#                 'author_display': author_display,
#                 'created_at': blog.created_at.strftime('%B %d, %Y'),
#                 'author_age': user.age if user.age else 'Not provided'
#             })
#         except Exception as e:
#             logger.error(f"Blog creation error: {str(e)}")
#             return JsonResponse({'success': False, 'message': str(e)}, status=500)
#     context = {'blogs': Blog.objects.all().order_by('-created_at'), 'user_name': user_name}
#     return render(request, 'blog.html', context)

# # Prediction View with Machine Learning
# @csrf_exempt
# def predict_view(request):
#     user_name = request.session.get('user_name')
#     if not user_name:
#         return redirect('predictor:login')

#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body.decode('utf-8')).get('data', {})
#             user = User.objects.get(user_name=user_name)

#             # Extract form data (add diabetes_pedigree)
#             gender = data.get('gender')
#             age = int(data.get('age'))
#             weight = float(data.get('weight'))
#             height = float(data.get('height'))
#             pregnancies = int(data.get('pregnancies', 0)) if gender == 'female' else None
#             glucose = float(data.get('glucose'))
#             blood_pressure = float(data.get('bloodPressure'))
#             skin_thickness = float(data.get('skinThickness'))
#             insulin = float(data.get('insulin'))
#             diabetes_pedigree = float(data.get('diabetesPedigree'))  # New field

#             # Update user's age and gender
#             user.age = age
#             user.gender = gender
#             user.save()

#             # Make prediction using ML model
#             prediction_result = predictor.predict({
#                 'gender': gender,
#                 'age': age,
#                 'weight': weight,
#                 'height': height,
#                 'pregnancies': pregnancies,
#                 'glucose': glucose,
#                 'blood_pressure': blood_pressure,
#                 'skin_thickness': skin_thickness,
#                 'insulin': insulin,
#                 'diabetes_pedigree': diabetes_pedigree  # New field
#             })

#             # Save prediction with BMI
#             prediction = Prediction.objects.create(
#                 user=user,
#                 gender=gender,
#                 age=age,
#                 weight=weight,
#                 height=height,
#                 bmi=prediction_result['bmi'],
#                 pregnancies=pregnancies,
#                 glucose=glucose,
#                 blood_pressure=blood_pressure,
#                 skin_thickness=skin_thickness,
#                 insulin=insulin,
#                 diabetes_pedigree=diabetes_pedigree,  # New field
#                 risk_level=prediction_result['risk_level'],
#                 probability=prediction_result['probability']
#             )

#             return JsonResponse({
#                 'success': True,
#                 'redirect_url': '/dashboard/',
#                 'risk_level': prediction_result['risk_level'],
#                 'probability': prediction_result['probability'],
#                 'prediction_id': prediction.id
#             })
#         except Exception as e:
#             logger.error(f"Prediction error: {str(e)}")
#             return JsonResponse({'success': False, 'message': str(e)}, status=400)

#     return render(request, 'predict.html', {'user_name': user_name})



# def glucose_trends_view(request):
#     user_name = request.session.get('user_name')
#     if not user_name:
#         return redirect('predictor:login')
#     return render(request, 'glucose_trends.html', {'user_name': user_name})


# from django.http import JsonResponse
# from .models import Prediction

# @csrf_exempt
# def glucose_data_api(request):
#     user_name = request.session.get('user_name')
#     if not user_name:
#         return JsonResponse({'error': 'Unauthorized'}, status=401)
#     try:
#         user = User.objects.get(user_name=user_name)
#         predictions = Prediction.objects.filter(user=user).order_by('created_at')
#         data = [{'date': pred.created_at.strftime('%Y-%m-%d'), 'glucose': pred.glucose} for pred in predictions]
#         return JsonResponse(data, safe=False)
#     except User.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)



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

# Login View (Updated for traditional form submission)
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
                return redirect('predictor:dashboard')
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

# Username Availability Check (Not needed for non-AJAX login, but kept for completeness)
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

# Signup View (Already updated for non-AJAX in previous response)
def signup_view(request):
    if request.method == 'POST':
        logger.debug(f"Received POST request: {request.POST}")
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validation
        errors = {}
        
        # Check for existing username and email
        if User.objects.filter(user_name__iexact=username).exists():
            errors['username'] = 'Username already exists'
            logger.debug(f"Duplicate username detected: {username}")
        if User.objects.filter(email__iexact=email).exists():
            errors['email'] = 'Email already exists'
            logger.debug(f"Duplicate email detected: {email}")
        
        # Additional validations
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
            for field, error in errors.items():
                messages.error(request, f"{field}: {error}")
            return render(request, 'signup.html')
        
        # Create user
        try:
            user = User.objects.create(
                user_name=username,
                email=email,
                password=password  # Password will be hashed in the model's save method
            )
            logger.info(f"User created: {username}")
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('predictor:login')
        except IntegrityError as e:
            logger.error(f"IntegrityError during user creation: {str(e)}")
            if 'user_name' in str(e).lower():
                messages.error(request, "username: Username already exists")
            elif 'email' in str(e).lower():
                messages.error(request, "email: Email already exists")
            else:
                messages.error(request, "An error occurred during account creation. Please try again.")
            return render(request, 'signup.html')
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {str(e)}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return render(request, 'signup.html')
    
    logger.debug("Rendering signup page")
    return render(request, 'signup.html')

# Check Signup Username Availability (Not needed for non-AJAX, but kept for completeness)
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

# Check Signup Email Availability (Not needed for non-AJAX, but kept for completeness)
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

# Logout View
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

# Blog View
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

# Glucose Trends View
def glucose_trends_view(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return redirect('predictor:login')
    return render(request, 'glucose_trends.html', {'user_name': user_name})

# Glucose Data API
@csrf_exempt
def glucose_data_api(request):
    user_name = request.session.get('user_name')
    if not user_name:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        user = User.objects.get(user_name=user_name)
        predictions = Prediction.objects.filter(user=user).order_by('created_at')
        data = [{'date': pred.created_at.strftime('%Y-%m-%d'), 'glucose': pred.glucose} for pred in predictions]
        return JsonResponse(data, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)