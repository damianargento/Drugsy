from models.disease_prediction_model import disease_model
from typing import Dict, Any, Optional
from langchain_core.tools import BaseTool

def disease_prediction_tool(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict disease risk for a patient based on their health data.
    
    Args:
        patient_data: Dictionary containing patient health information with the following fields:
            - age: int (patient age in years)
            - sex: int (0=Female, 1=Male)
            - blood_pressure: int (systolic blood pressure in mmHg)
            - cholesterol: int (total cholesterol level in mg/dL)
            - glucose_level: int (fasting blood glucose level in mg/dL)
            - bmi: float (body mass index)
            - family_history: int (0=No, 1=Yes for family history of cardiovascular disease)
            
    Returns:
        dict: Prediction results with risk assessment and confidence score
    """
    try:
        # Call the disease prediction model
        return disease_model.predict_disease_risk(patient_data)
    except Exception as e:
        # Return error information if prediction fails
        return {
            "status": "error",
            "error": f"Error during prediction: {str(e)}",
            "message": "Could not complete disease risk prediction due to an error."
        }
