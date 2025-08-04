"""
Diabetes prediction tool using a machine learning model.
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

def estimate_dpf(mother_has_diabetes: int, father_has_diabetes: int, 
                diabetic_siblings: int, diabetic_children: int, 
                second_degree_relatives: int) -> float:
    """
    Estimate Diabetes Pedigree Function (DPF) based on family history.
    
    The DPF provides a measure of diabetes mellitus history in relatives and the genetic
    relationship of those relatives to the patient. Higher values indicate stronger family history.
    
    Args:
        mother_has_diabetes: Whether mother has diabetes (1=Yes, 0=No)
        father_has_diabetes: Whether father has diabetes (1=Yes, 0=No)
        diabetic_siblings: Number of siblings with diabetes
        diabetic_children: Number of children with diabetes
        second_degree_relatives: Whether any second-degree relatives have diabetes (1=Yes, 0=No)
        
    Returns:
        float: Estimated DPF value between 0.0 and 2.5
    """
    # Weights based on genetic proximity
    mother_weight = 0.5
    father_weight = 0.5
    sibling_weight = 0.3
    child_weight = 0.3
    second_degree_weight = 0.1
    
    # Calculate weighted sum
    dpf = (mother_has_diabetes * mother_weight + 
           father_has_diabetes * father_weight + 
           min(diabetic_siblings, 5) * sibling_weight + 
           min(diabetic_children, 5) * child_weight + 
           second_degree_relatives * second_degree_weight)
    
    # Clamp value between 0 and 2.5 (typical range for DPF)
    return min(max(dpf, 0.0), 2.5)

def diabetes_prediction_tool(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts diabetes risk based on patient data.
    
    Args:
        patient_data: Dictionary containing patient information with the following keys:
            - Pregnancies: Number of pregnancies
            - Glucose: Plasma glucose concentration
            - BloodPressure: Diastolic blood pressure (mm Hg)
            - SkinThickness: Triceps skin fold thickness (mm)
            - Insulin: 2-Hour serum insulin (mu U/ml)
            - BMI: Body mass index
            - Age: Age in years
            - MotherHasDiabetes: Whether mother has diabetes (1=Yes, 0=No)
            - FatherHasDiabetes: Whether father has diabetes (1=Yes, 0=No)
            - DiabeticSiblings: Number of siblings with diabetes
            - DiabeticChildren: Number of children with diabetes
            - SecondDegreeRelatives: Whether any second-degree relatives have diabetes (1=Yes, 0=No)
            
    Returns:
        dict: Prediction results with risk assessment and confidence score
    """
    # Log tool call with parameters
    print(f"Diabetes prediction tool called with parameters: {json.dumps(patient_data)}")
    try:
        # Check if all required fields are present
        required_fields = [
            'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
            'Insulin', 'BMI', 'Age', 'MotherHasDiabetes', 'FatherHasDiabetes',
            'DiabeticSiblings', 'DiabeticChildren', 'SecondDegreeRelatives'
        ]
        
        missing_fields = [field for field in required_fields if field not in patient_data]
        if missing_fields:
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }
        
        # Calculate Diabetes Pedigree Function from family history
        dpf = estimate_dpf(
            patient_data['MotherHasDiabetes'],
            patient_data['FatherHasDiabetes'],
            patient_data['DiabeticSiblings'],
            patient_data['DiabeticChildren'],
            patient_data['SecondDegreeRelatives']
        )
        
        # Load the model from cache
        model = model_cache.get_model('diabetes')
        if model is None:
            return {
                "status": "error",
                "error": "Failed to load diabetes prediction model from cache"
            }
        
        # Prepare input features in the correct order
        features = np.array([
            [
                float(patient_data['Pregnancies']),
                float(patient_data['Glucose']),
                float(patient_data['BloodPressure']),
                float(patient_data['SkinThickness']),
                float(patient_data['Insulin']),
                float(patient_data['BMI']),
                dpf,  # Using calculated DPF
                float(patient_data['Age'])
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
            "dpf_calculated": dpf,
            "risk_assessment": "High risk of diabetes" if is_at_risk else "Low risk of diabetes"
        }
        
        # Log prediction result
        print(f"Diabetes prediction result: {json.dumps(result)}")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": f"Error during prediction: {str(e)}"
        }
        print(f"Diabetes prediction error: {str(e)}")
        return error_result

# Export the function directly instead of creating a LangChain Tool class
# This avoids Pydantic compatibility issues with the current version
