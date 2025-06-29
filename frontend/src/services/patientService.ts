import axios from 'axios';
import { BACKEND_URL } from '../config';

// Patient types
export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
}

export interface ProgressNote {
  date: string;
  content: string;
}

export interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  medications?: Medication[];
  chronic_conditions?: string;
  progress_notes?: ProgressNote[];
  doctor_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PatientCreate {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  medications?: Medication[];
  chronic_conditions?: string;
  progress_notes?: ProgressNote[];
}

export interface PatientUpdate {
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  medications?: Medication[];
  chronic_conditions?: string;
}

export interface ProgressNoteCreate {
  content: string;
}

// Get all patients for the current doctor
const getPatients = async (): Promise<Patient[]> => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${BACKEND_URL}/patients`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.data;
};

// Get a specific patient by ID
const getPatient = async (patientId: number): Promise<Patient> => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${BACKEND_URL}/patients/${patientId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.data;
};

// Create a new patient
const createPatient = async (patient: PatientCreate): Promise<Patient> => {
  const token = localStorage.getItem('token');
  const response = await axios.post(`${BACKEND_URL}/patients`, patient, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.data;
};

// Update a patient
const updatePatient = async (patientId: number, patientData: PatientUpdate): Promise<Patient> => {
  const token = localStorage.getItem('token');
  const response = await axios.put(`${BACKEND_URL}/patients/${patientId}`, patientData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.data;
};

// Delete a patient
const deletePatient = async (patientId: number): Promise<any> => {
  const token = localStorage.getItem('token');
  const response = await axios.delete(`${BACKEND_URL}/patients/${patientId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.data;
};

// Add a progress note to a patient
const addProgressNote = async (patientId: number, note: ProgressNoteCreate): Promise<Patient> => {
  const token = localStorage.getItem('token');
  const response = await axios.post(`${BACKEND_URL}/patients/${patientId}/notes`, note, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.data;
};

const patientService = {
  getPatients,
  getPatient,
  createPatient,
  updatePatient,
  deletePatient,
  addProgressNote
};

export default patientService;
