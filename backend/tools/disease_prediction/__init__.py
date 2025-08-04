"""
Disease prediction tools package.
This package contains tools for predicting various diseases using machine learning models.
"""

from .diabetes_prediction_tool import diabetes_prediction_tool
from .heart_disease_prediction_tool import heart_disease_prediction_tool
from .lung_cancer_prediction_tool import lung_cancer_prediction_tool
from .thyroid_prediction_tool import thyroid_prediction_tool
from .tools_wrapper import (
    diabetes_prediction_wrapper,
    heart_disease_prediction_wrapper,
    lung_cancer_prediction_wrapper,
    thyroid_prediction_wrapper
)

__all__ = [
    'diabetes_prediction_tool',
    'heart_disease_prediction_tool',
    'lung_cancer_prediction_tool',
    'thyroid_prediction_tool',
    'diabetes_prediction_wrapper',
    'heart_disease_prediction_wrapper',
    'lung_cancer_prediction_wrapper',
    'thyroid_prediction_wrapper'
]
