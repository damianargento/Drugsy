"""
Hypothyroidism prediction tool using a machine learning model.
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

def thyroid_prediction_tool(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts hypothyroidism risk based on patient data.
    
    Args:
        patient_data: Dictionary containing patient information with the following keys:
            - Age: Age in years
            - Sex: Sex (1=Male, 0=Female)
            - TSH: Thyroid Stimulating Hormone level
            - T3: Triiodothyronine level
            - TT4: Total Thyroxine level
            - T4U: Thyroxine Uptake
            - FTI: Free Thyroxine Index
            - OnThyroxine: On thyroxine medication (1=Yes, 0=No)
            - QueryOnThyroxine: Query on thyroxine (1=Yes, 0=No)
            - OnAntithyroidMedication: On antithyroid medication (1=Yes, 0=No)
            - Sick: Sick (1=Yes, 0=No)
            - Pregnant: Pregnant (1=Yes, 0=No)
            - ThyroidSurgery: Thyroid surgery (1=Yes, 0=No)
            - I131Treatment: I131 treatment (1=Yes, 0=No)
            - QueryHypothyroid: Query hypothyroid (1=Yes, 0=No)
            - QueryHyperthyroid: Query hyperthyroid (1=Yes, 0=No)
            - Lithium: Lithium (1=Yes, 0=No)
            - Goitre: Goitre (1=Yes, 0=No)
            - Tumor: Tumor (1=Yes, 0=No)
            - Hypopituitary: Hypopituitary (1=Yes, 0=No)
            - Psych: Psychological symptoms (1=Yes, 0=No)
            - TSHMeasured: TSH measured (1=Yes, 0=No)
            - T3Measured: T3 measured (1=Yes, 0=No)
            - TT4Measured: TT4 measured (1=Yes, 0=No)
            - T4UMeasured: T4U measured (1=Yes, 0=No)
            - FTIMeasured: FTI measured (1=Yes, 0=No)
            - TBGMeasured: TBG measured (1=Yes, 0=No)
            - TBG: Thyroxine Binding Globulin level
            - Referral: Referral source
            
    Returns:
        dict: Prediction results with risk assessment and confidence score
    """
    # Log tool call with parameters
    print(f"Thyroid prediction tool called with parameters: {json.dumps(patient_data)}")
    try:
        # Check if all required fields are present
        required_fields = [
            'Age', 'Sex', 'TSH', 'T3', 'TT4', 'T4U', 'FTI',
            'OnThyroxine', 'QueryOnThyroxine', 'OnAntithyroidMedication',
            'Sick', 'Pregnant', 'ThyroidSurgery', 'I131Treatment',
            'QueryHypothyroid', 'QueryHyperthyroid', 'Lithium',
            'Goitre', 'Tumor', 'Hypopituitary', 'Psych',
            'TSHMeasured', 'T3Measured', 'TT4Measured', 'T4UMeasured',
            'FTIMeasured', 'TBGMeasured', 'TBG', 'Referral'
        ]
        
        missing_fields = [field for field in required_fields if field not in patient_data]
        if missing_fields:
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }
        
        # Load the model from cache
        model = model_cache.get_model('thyroid')
        if model is None:
            return {
                "status": "error",
                "error": "Failed to load thyroid prediction model from cache"
            }
        
        # Map our parameters to the expected feature names in the model
        # Feature names from model: ['age', 'sex', 'on thyroxine', 'TSH', 'T3 measured', 'T3', 'TT4']
        
        # Prepare input features in the correct order based on the model's expected features
        features = np.array([
            [
                float(patient_data['Age']),             # age
                float(patient_data['Sex']),             # sex
                float(patient_data['OnThyroxine']),      # on thyroxine
                float(patient_data['TSH']),             # TSH
                float(patient_data['T3Measured']),       # T3 measured
                float(patient_data['T3']),              # T3
                float(patient_data['TT4'])              # TT4
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
            "risk_assessment": "High risk of hypothyroidism" if is_at_risk else "Low risk of hypothyroidism"
        }
        
        # Log prediction result
        print(f"Thyroid prediction result: {json.dumps(result)}")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": f"Error during prediction: {str(e)}"
        }
        print(f"Thyroid prediction error: {str(e)}")
        return error_result

# Export the function directly instead of creating a LangChain Tool class
# This avoids Pydantic compatibility issues with the current version
