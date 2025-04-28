from django.db import models
import datetime
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    user_name = models.CharField(max_length=120, primary_key=True, help_text="Unique username for the user")
    email = models.EmailField(max_length=120, unique=True, help_text="User's email address")
    password = models.CharField(max_length=120, help_text="Hashed password for the user")
    age = models.PositiveIntegerField(blank=True, null=True, help_text="User's age in years")
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True, null=True, help_text="User's gender")
    created_at = models.DateTimeField(default=datetime.datetime.now, help_text="Timestamp of user creation")

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        return self.email

class Blog(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the blog post")
    content = models.TextField(help_text="Main content of the blog post")
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, help_text="Optional image for the blog post")
    author = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who authored this blog post")
    created_at = models.DateTimeField(default=datetime.datetime.now, help_text="Timestamp of blog creation")

    def __str__(self):
        return self.title

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who made this prediction")
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], help_text="User's gender")
    age = models.PositiveIntegerField(help_text="User's age in years")
    weight = models.FloatField(help_text="User's weight in kg")
    height = models.FloatField(help_text="User's height in cm")
    bmi = models.FloatField(null=True, blank=True, help_text="User's Body Mass Index (kg/m²)")
    pregnancies = models.PositiveIntegerField(null=True, blank=True, help_text="Number of pregnancies (for females)")
    glucose = models.FloatField(help_text="Glucose level in mg/dL")
    blood_pressure = models.FloatField(help_text="Blood pressure in mm Hg")
    skin_thickness = models.FloatField(help_text="Skin thickness in mm")
    insulin = models.FloatField(help_text="Insulin level in μU/mL")
    diabetes_pedigree = models.FloatField(help_text="Diabetes Pedigree Function", default=0.0)
    risk_level = models.CharField(max_length=20, help_text="Predicted risk level (Low, Moderate, High)")
    created_at = models.DateTimeField(default=datetime.datetime.now, help_text="Timestamp of prediction")
    diabetes_probability = models.FloatField(null=True, blank=True, help_text="Probability of having diabetes (0 to 1)")
    health_tips = models.TextField(null=True, blank=True, help_text="Personalized health tips based on prediction results (JSON string)")

    def __str__(self):
        return f"{self.user.user_name} - {self.risk_level} ({self.created_at})"