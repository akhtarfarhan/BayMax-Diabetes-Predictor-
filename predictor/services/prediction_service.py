import joblib
import numpy as np
import os
from django.conf import settings

class DiabetesPredictor:
    def __init__(self):
        # Load model and scaler
        model_path = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'random_forest_diabetes_model.joblib')
        scaler_path = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'scaler.joblib')
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
    
    def calculate_bmi(self, weight_kg, height_cm):
        """Calculate BMI from weight in kg and height in cm"""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def predict(self, input_data):
        """
        Make a prediction based on input data
        
        Args:
            input_data: Dictionary containing:
                - gender (str): 'male' or 'female'
                - age (int)
                - weight (float): in kg
                - height (float): in cm
                - pregnancies (int or None)
                - glucose (float)
                - blood_pressure (float)
                - skin_thickness (float)
                - insulin (float)
                - diabetes_pedigree (float)  # New field
                
        Returns:
            dict: {'risk_level': 'Low/Medium/High', 'probability': float, 'bmi': float}
        """
        # Calculate BMI
        bmi = self.calculate_bmi(input_data['weight'], input_data['height'])
        
        # Convert gender to numerical (0 for male, 1 for female)
        gender = 1 if input_data['gender'] == 'female' else 0
        
        # Prepare feature array in the exact order the model expects
        features = [
            input_data['pregnancies'] if input_data['gender'] == 'female' else 0,
            input_data['glucose'],
            input_data['blood_pressure'],
            input_data['skin_thickness'],
            input_data['insulin'],
            bmi,
            input_data['diabetes_pedigree'],  # New field
            input_data['age'],
            # gender
        ]
        
        # Scale the features
        scaled_features = self.scaler.transform([features])
        
        # Make prediction
        prediction = self.model.predict(scaled_features)[0]
        probabilities = self.model.predict_proba(scaled_features)[0]
        
        # Map prediction to risk level
        risk_levels = ['Low', 'Moderate', 'High']
        risk_level = risk_levels[prediction]
        
        return {
            'risk_level': risk_level,
            'probability': max(probabilities),
            'bmi': bmi
        }