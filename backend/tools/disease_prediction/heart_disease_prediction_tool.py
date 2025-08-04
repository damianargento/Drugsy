"""
Heart disease prediction tool using a machine learning model.
"""

import os
import pickle
import numpy as np
import json
from pathlib import Path
from langchain_core.tools import BaseTool
from typing import Dict, Any, Optional
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from .model_cache import model_cache

def heart_disease_prediction_tool(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts heart disease risk based on patient data.
    
    Args:
        patient_data: Dictionary containing patient information with the following keys:
            - Age: Age in years
            - Sex: Sex (1=Male, 0=Female)
            - ChestPainType: Type of chest pain (0-3)
            - RestingBP: Resting blood pressure (mm Hg)
            - Cholesterol: Serum cholesterol (mg/dl)
            - FastingBS: Fasting blood sugar > 120 mg/dl (1=True, 0=False)
            - RestingECG: Resting electrocardiographic results (0-2)
            - MaxHR: Maximum heart rate achieved
            - ExerciseAngina: Exercise-induced angina (1=Yes, 0=No)
            - Oldpeak: ST depression induced by exercise relative to rest
            - ST_Slope: Slope of the peak exercise ST segment (0-2)
            
    Returns:
        dict: Prediction results with risk assessment and confidence score
    """
    # Log tool call with parameters
    print(f"Heart disease prediction tool called with parameters: {json.dumps(patient_data)}")
    try:
        # Check if all required fields are present
        required_fields = [
            'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 
            'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 
            'Oldpeak', 'ST_Slope'
        ]
        
        missing_fields = [field for field in required_fields if field not in patient_data]
        if missing_fields:
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }
        
        # Load the model from cache
        model = model_cache.get_model('heart')
        if model is None:
            return {
                "status": "error",
                "error": "Failed to load heart disease prediction model from cache"
            }
        
        # Map our parameters to the expected feature names in the model
        # Feature names from model: ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
        # We need to map our parameters to these names
        
        # Default values for missing features
        ca = 0  # Number of major vessels (0-3)
        thal = 2  # 3 = normal; 6 = fixed defect; 7 = reversible defect (2 is a placeholder)
        
        # Prepare input features in the correct order
        features = np.array([
            [
                float(patient_data['Age']),                  # age
                float(patient_data['Sex']),                  # sex
                float(patient_data['ChestPainType']),        # cp (chest pain type)
                float(patient_data['RestingBP']),            # trestbps (resting blood pressure)
                float(patient_data['Cholesterol']),          # chol (cholesterol)
                float(patient_data['FastingBS']),            # fbs (fasting blood sugar)
                float(patient_data['RestingECG']),           # restecg (resting ECG)
                float(patient_data['MaxHR']),                # thalach (maximum heart rate)
                float(patient_data['ExerciseAngina']),       # exang (exercise induced angina)
                float(patient_data['Oldpeak']),              # oldpeak
                float(patient_data['ST_Slope']),             # slope
                ca,                                          # ca (number of major vessels)
                thal                                         # thal
            ]
        ])
        
        # Make prediction
        prediction = model.predict(features)
        
        # Get prediction probability if available
        confidence = 0.0
        try:
            confidence = float(model.predict_proba(features)[0][1])
        except:
            # Some models don't support predict_proba
            confidence = float(prediction[0])
        
        # Interpret results
        is_at_risk = bool(prediction[0] == 1)
        
        result = {
            "is_at_risk": is_at_risk,
            "confidence": confidence,
            "status": "success",
            "risk_assessment": "High risk of heart disease" if is_at_risk else "Low risk of heart disease"
        }
        
        # Log prediction result
        print(f"Heart disease prediction result: {json.dumps(result)}")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": f"Error during prediction: {str(e)}"
        }
        print(f"Heart disease prediction error: {str(e)}")
        return error_result

# Export the function directly instead of creating a LangChain Tool class
# This avoids Pydantic compatibility issues with the current version
