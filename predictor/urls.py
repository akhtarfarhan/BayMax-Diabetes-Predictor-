from django.urls import path
from . import views

app_name = 'predictor'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('check-username/', views.check_username, name='check_username'),
    path('check-signup-username/', views.check_signup_username, name='check_signup_username'),
    path('check-signup-email/', views.check_signup_email, name='check_signup_email'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('blog/', views.blog_view, name='blog'),
    path('predict/', views.predict_view, name='predict'),
    path('predict-unauthenticated/', views.predict_unauthenticated_view, name='predict_unauthenticated'),
    path('glucose-trends/', views.glucose_trends_view, name='glucose_trends'),
    path('glucose-data/', views.glucose_data_api, name='glucose_data_api'),
    path('start-prediction/', views.start_prediction, name='start_prediction'),
]