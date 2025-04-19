from django.urls import path
from . import views

app_name = 'predictor'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('blog/', views.blog_view, name='blog'),
    path('predict/', views.predict_view, name='predict'),
    path('logout/', views.logout_view, name='logout'),
    path('glucose-trends/', views.glucose_trends_view, name='glucose_trends'),
    path('api/glucose-data/', views.glucose_data_api, name='glucose_data_api'),
]