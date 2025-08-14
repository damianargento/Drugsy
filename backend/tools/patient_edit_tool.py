from langchain.tools import tool
import requests
import os
import json
from typing import Dict, Any, Optional, List, Union
from fastapi import HTTPException

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

# Get API token from environment
API_TOKEN = os.getenv("SECRET_KEY", "")

# Function to get authorization headers
def get_auth_headers():
    print(f"\n==== AUTH INFO ====\nAPI_TOKEN exists: {bool(API_TOKEN)}\nAPI_TOKEN length: {len(API_TOKEN) if API_TOKEN else 0}\n=====================\n")
    if not API_TOKEN:
        print("ERROR: API token not configured")
        raise HTTPException(status_code=401, detail="API token not configured")
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

@tool
def edit_patient_data(patient_id: int, update_data: str) -> str:
    """Updates patient data in the Drugsy backend database.
    
    ARGS:
        patient_id: The ID of the patient to update
        update_data: A JSON string containing the fields to update. Can include:
                    - first_name: Patient's first name
                    - last_name: Patient's last name
                    - date_of_birth: Date of birth in YYYY-MM-DD format
                    - chronic_conditions: Text describing chronic conditions
                    - medications: List of medication objects with name, dosage, and frequency
                    - progress_notes: List of progress note objects with date and content
    
    EXAMPLES:
        - Update name: '{"first_name": "John", "last_name": "Smith"}'
        - Update medications: '{"medications": [{"name": "Aspirin", "dosage": "100mg", "frequency": "daily"}]}'
        - Update chronic conditions: '{"chronic_conditions": "Hypertension, Diabetes"}'
        - Update progress notes: '{"progress_notes": [{"date": "2023-01-01", "content": "Patient is feeling well"}]}'
    
    RETURNS:
        A dictionary with the updated patient data or an error message
    """
    print(f"[TOOL CALLED] edit_patient_data with patient_id={patient_id}")
    try:
        # Parse the update data from JSON string
        update_dict = json.loads(update_data)
        
        # Make the API call to update the patient
        url = f"{BACKEND_URL}/patients/{patient_id}"
        headers = get_auth_headers()
        
        response = requests.put(url, json=update_dict, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error updating patient: {response.status_code} - {response.text}"
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON in update_data parameter"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_patient_data(patient_id: int) -> str:
    """Retrieves patient data from the Drugsy backend database.
    
    ARGS:
        patient_id: The ID of the patient to retrieve
    
    RETURNS:
        A dictionary with the patient data or an error message
    """
    print(f"[TOOL CALLED] get_patient_data with patient_id={patient_id}")
    try:
        # Make the API call to get the patient
        url = f"{BACKEND_URL}/patients/{patient_id}"
        headers = get_auth_headers()
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error retrieving patient: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def add_medication(patient_id: int, medication_data: str) -> str:
    """Adds a medication to a patient's record.
    
    ARGS:
        patient_id: The ID of the patient
        medication_data: A JSON string with the medication details:
                        - name: Medication name
                        - dosage: Medication dosage
                        - frequency: How often to take the medication
    
    EXAMPLE:
        '{"name": "Lisinopril", "dosage": "10mg", "frequency": "once daily"}'
    
    RETURNS:
        A dictionary with the updated patient data or an error message
    """
    print(f"[TOOL CALLED] add_medication with patient_id={patient_id}")
    try:
        # Parse the medication data
        medication = json.loads(medication_data)
        
        # First get current patient data
        url = f"{BACKEND_URL}/patients/{patient_id}"
        headers = get_auth_headers()
        
        get_response = requests.get(url, headers=headers)
        
        if get_response.status_code != 200:
            return f"Error retrieving patient: {get_response.status_code} - {get_response.text}"
        
        patient_data = get_response.json()
        
        # Update medications list
        medications = patient_data.get("medications", [])
        medications.append(medication)
        
        # Update patient with new medications list
        update_data = {"medications": medications}
        update_response = requests.put(url, json=update_data, headers=headers)
        
        if update_response.status_code == 200:
            return update_response.json()
        else:
            return f"Error adding medication: {update_response.status_code} - {update_response.text}"
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON in medication_data parameter"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def add_progress_note(patient_id: int, note_content: str) -> str:
    """Adds a progress note to a patient's record.
    ARGS:
        patient_id: The ID of the patient
        note_content: The content of the progress note
    
    RETURNS:
        A dictionary with the updated patient data or an error message
    """
    print(f"[TOOL CALLED] add_progress_note with patient_id={patient_id}")
    try:
        print(f"Patient ID: {patient_id}")
        print(f"Note Content: {note_content}")
        # Prepare the note data
        note_data = {"content": note_content}
        
        # Make the API call to add the note
        url = f"{BACKEND_URL}/patients/{patient_id}/notes"
        headers = get_auth_headers()
        
        print(f"Making API call to URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {note_data}")
        
        try:
            response = requests.post(url, json=note_data, headers=headers)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Error adding progress note: {response.status_code} - {response.text}"
                print(f"ERROR: {error_msg}")
                return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            print(f"ERROR: {error_msg}")
            return error_msg
    
    except Exception as e:
        return f"Error: {str(e)}"
