from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from models.disease_prediction_model import disease_model

router = APIRouter(tags=["Predictions"])

@router.post("/predictions/disease-risk", response_model=Dict[str, Any])
def predict_disease_risk(
    patient_data: Dict[str, Any],
):
    """
    Predict disease risk based on patient health data
    
    This endpoint takes patient health metrics and returns a risk assessment
    for developing certain diseases based on the provided data.
    """
    print("LLM is using the endpoints")
    # Call the disease prediction model
    result = disease_model.predict_disease_risk(patient_data)
    
    # Handle missing data case
    if result.get("status") == "incomplete_data":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Missing required data for prediction"),
            headers={"missing_fields": ",".join(result.get("missing_fields", []))}
        )
    
    # Handle error case
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "An error occurred during prediction")
        )
    
    return result