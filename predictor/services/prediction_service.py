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
    
    def calculate_healthy_weight_range(self, height_cm):
        """Calculate healthy weight range (kg) for BMI 18.5–24.9"""
        height_m = height_cm / 100
        min_weight = 18.5 * (height_m ** 2)
        max_weight = 24.9 * (height_m ** 2)
        return min_weight, max_weight
    
    def generate_health_tips(self, blood_pressure, weight, height):
        """Generate personalized health tips based on blood pressure and weight"""
        tips = []
        
        # Blood Pressure-based tips
        systolic = blood_pressure  # Assuming blood_pressure is systolic for simplicity
        if systolic > 140:
            tips.append("Your blood pressure is high. Reduce sodium intake by avoiding processed foods and adding more fresh vegetables to your diet.")
            tips.append("Engage in stress-reducing activities like meditation or deep breathing exercises to help manage blood pressure.")
            tips.append("Consult a healthcare provider to discuss potential medication or further evaluation.")
        elif systolic >= 120:
            tips.append("Your blood pressure is elevated. Incorporate 30 minutes of aerobic exercise, such as brisk walking or cycling, most days of the week.")
            tips.append("Limit caffeine and alcohol consumption to help maintain healthy blood pressure levels.")
        else:
            tips.append("Your blood pressure is normal. Continue regular physical activity to maintain cardiovascular health.")
            tips.append("Monitor your blood pressure periodically to ensure it remains in the healthy range.")
        
        # Weight-based tips (using healthy weight range for height)
        min_weight, max_weight = self.calculate_healthy_weight_range(height)
        bmi = self.calculate_bmi(weight, height)
        if bmi >= 25:
            tips.append(f"Your weight ({weight} kg) is above the healthy range ({min_weight:.1f}–{max_weight:.1f} kg) for your height. Aim for gradual weight loss by reducing calorie intake and increasing physical activity.")
            tips.append("Try portion control and include more fiber-rich foods like fruits, vegetables, and whole grains to support weight management.")
        elif bmi < 18.5:
            tips.append(f"Your weight ({weight} kg) is below the healthy range ({min_weight:.1f}–{max_weight:.1f} kg) for your height. Consult a dietitian to ensure adequate nutrition and healthy weight gain.")
            tips.append("Incorporate calorie-dense, nutrient-rich foods like nuts, avocados, and lean proteins into your diet.")
        else:
            tips.append(f"Your weight ({weight} kg) is within the healthy range ({min_weight:.1f}–{max_weight:.1f} kg) for your height. Maintain this with a balanced diet and regular exercise.")
            tips.append("Stay active with a mix of cardio and strength training to support overall health.")
        
        return tips
    
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
                - diabetes_pedigree (float)
                
        Returns:
            dict: {'risk_level': 'Low/Moderate/High', 'diabetes_probability': float, 'bmi': float, 'health_tips': list}
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
            input_data['diabetes_pedigree'],
            input_data['age'],
        ]
        
        # Scale the features
        scaled_features = self.scaler.transform([features])
        
        # Make prediction
        prediction = self.model.predict(scaled_features)[0]
        probabilities = self.model.predict_proba(scaled_features)[0]
        
        # Map prediction to risk level
        if probabilities[1] >= 0.7:
            risk_level = 'High'
        elif probabilities[1] >= 0.3:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'
        
        # Generate health tips
        health_tips = self.generate_health_tips(
            input_data['blood_pressure'],
            input_data['weight'],
            input_data['height']
        )
        
        return {
            'risk_level': risk_level,
            'diabetes_probability': probabilities[1],
            'bmi': bmi,
            'health_tips': health_tips
        }