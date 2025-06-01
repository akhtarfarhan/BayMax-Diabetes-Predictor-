from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    user_name = models.CharField(max_length=120, primary_key=True)
    email = models.EmailField(max_length=120, unique=True)
    password = models.CharField(max_length=120)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        return self.user_name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    age = models.PositiveIntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    bmi = models.FloatField(null=True, blank=True)
    pregnancies = models.PositiveIntegerField(null=True, blank=True)
    glucose = models.FloatField()
    blood_pressure = models.FloatField()
    skin_thickness = models.FloatField()
    insulin = models.FloatField()
    diabetes_pedigree = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    diabetes_probability = models.FloatField(null=True, blank=True)
    health_tips = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.user_name} - {self.risk_level}"