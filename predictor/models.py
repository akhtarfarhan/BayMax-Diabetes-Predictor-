# from django.db import models
# import datetime
# from django.contrib.auth.hashers import make_password, check_password

# class User(models.Model):
#     """
#     Model representing a user with authentication capabilities.
#     """
#     # Core identification fields
#     user_name = models.CharField(
#         max_length=120,
#         primary_key=True,
#         help_text="Unique username for the user"
#     )
#     email = models.EmailField(
#         max_length=120,
#         unique=True,
#         help_text="User's email address"
#     )
    
#     # Authentication fields
#     password = models.CharField(
#         max_length=120,
#         blank=True,
#         null=True,
#         help_text="Hashed password for the user"
#     )
#     retype_password = models.CharField(
#         max_length=120,
#         blank=True,
#         null=True,
#         help_text="Temporary field for password confirmation (not stored)"
#     )
    
#     # Additional user information
#     age = models.PositiveIntegerField(
#         blank=True,
#         null=True,
#         help_text="User's age in years"
#     )
#     created_at = models.DateTimeField(
#         default=datetime.datetime.now,
#         help_text="Timestamp of user creation"
#     )

#     def save(self, *args, **kwargs):
#         """
#         Override save method to hash password before saving.
#         """
#         if self.password and not self.password.startswith("pbkdf2_"):
#             self.password = make_password(self.password)
#         super().save(*args, **kwargs)

#     def authenticate(self, user_name=None, password=None):
#         """
#         Authenticate a user based on username and password.
        
#         Args:
#             user_name (str): The username to authenticate
#             password (str): The password to verify
            
#         Returns:
#             User: User object if authentication succeeds, None otherwise
#         """
#         try:
#             user = User.objects.get(user_name=user_name)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None

#     def check_password(self, password):
#         """
#         Verify if the provided password matches the stored hash.
        
#         Args:
#             password (str): The password to check
            
#         Returns:
#             bool: True if password matches, False otherwise
#         """
#         return check_password(password, self.password)

#     def __str__(self):
#         """String representation of the User object."""
#         return self.email


# class Blog(models.Model):
#     """
#     Model representing a blog post created by a user.
#     """
#     # Content fields
#     title = models.CharField(
#         max_length=200,
#         help_text="Title of the blog post"
#     )
#     content = models.TextField(
#         help_text="Main content of the blog post"
#     )
#     image = models.ImageField(
#         upload_to='blog_images/',
#         blank=True,
#         null=True,
#         help_text="Optional image for the blog post"
#     )
    
#     # Relationship fields
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         help_text="User who authored this blog post"
#     )
    
#     # Metadata
#     created_at = models.DateTimeField(
#         default=datetime.datetime.now,
#         help_text="Timestamp of blog creation"
#     )

#     def __str__(self):
#         """String representation of the Blog object."""
#         return self.title


# class Prediction(models.Model):
#     """
#     Model representing a health prediction for a user.
#     """
#     # Relationship fields
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='predictions',
#         help_text="User associated with this prediction"
#     )
    
#     # Demographic data
#     gender = models.CharField(
#         max_length=10,
#         help_text="User's gender"
#     )
#     age = models.PositiveIntegerField(
#         help_text="User's age at time of prediction"
#     )
    
#     # Physical measurements
#     weight = models.FloatField(
#         help_text="User's weight in pounds"
#     )
#     height = models.FloatField(
#         help_text="User's height in feet"
#     )
    
#     # Medical data
#     pregnancies = models.PositiveIntegerField(
#         help_text="Number of pregnancies"
#     )
#     glucose = models.FloatField(
#         help_text="Glucose level"
#     )
#     blood_pressure = models.FloatField(
#         help_text="Blood pressure measurement"
#     )
#     skin_thickness = models.FloatField(
#         help_text="Skin thickness measurement"
#     )
#     insulin = models.FloatField(
#         help_text="Insulin level"
#     )
    
#     # Prediction result
#     risk_level = models.CharField(
#         max_length=10,
#         default='Pending',
#         help_text="Calculated risk level"
#     )
    
#     # Metadata
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="Timestamp of prediction creation"
#     )

#     def __str__(self):
#         """String representation of the Prediction object."""
#         return f"Prediction for {self.user.user_name} on {self.created_at}"




#new

from django.db import models
import datetime
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    """
    Model representing a user with authentication capabilities.
    """
    # Core identification fields
    user_name = models.CharField(
        max_length=120,
        primary_key=True,
        help_text="Unique username for the user"
    )
    email = models.EmailField(
        max_length=120,
        unique=True,
        help_text="User's email address"
    )
    
    # Authentication fields
    password = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Hashed password for the user"
    )
    retype_password = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Temporary field for password confirmation (not stored)"
    )
    
    # Additional user information
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="User's age in years"
    )
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female')],
        blank=True,
        null=True,
        help_text="User's gender"
    )
    created_at = models.DateTimeField(
        default=datetime.datetime.now,
        help_text="Timestamp of user creation"
    )

    def save(self, *args, **kwargs):
        """
        Override save method to hash password before saving.
        """
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def authenticate(self, user_name=None, password=None):
        """
        Authenticate a user based on username and password.
        
        Args:
            user_name (str): The username to authenticate
            password (str): The password to verify
            
        Returns:
            User: User object if authentication succeeds, None otherwise
        """
        try:
            user = User.objects.get(user_name=user_name)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def check_password(self, password):
        """
        Verify if the provided password matches the stored hash.
        
        Args:
            password (str): The password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password(password, self.password)

    def __str__(self):
        """String representation of the User object."""
        return self.email

class Blog(models.Model):
    """
    Model representing a blog post created by a user.
    """
    # Content fields
    title = models.CharField(
        max_length=200,
        help_text="Title of the blog post"
    )
    content = models.TextField(
        help_text="Main content of the blog post"
    )
    image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        help_text="Optional image for the blog post"
    )
    
    # Relationship fields
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who authored this blog post"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        default=datetime.datetime.now,
        help_text="Timestamp of blog creation"
    )

    def __str__(self):
        """String representation of the Blog object."""
        return self.title
    

# prediction
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
    diabetes_pedigree = models.FloatField(help_text="Diabetes Pedigree Function", default=0.0)  # New field
    risk_level = models.CharField(max_length=20, help_text="Predicted risk level (Low, Moderate, High)")
    created_at = models.DateTimeField(default=datetime.datetime.now, help_text="Timestamp of prediction")
    probability = models.FloatField(null=True, blank=True, help_text="Prediction probability (0 to 1)")

    def __str__(self):
        return f"{self.user.user_name} - {self.risk_level} ({self.created_at})"