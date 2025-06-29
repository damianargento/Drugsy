import React, { useState, useEffect } from 'react';
import patientService, { Patient } from '../../services/patientService';
import './Patients.css';

interface PatientSelectorProps {
  onPatientSelect: (patient: Patient | null) => void;
  selectedPatientId?: number | null;
  onEditPatient?: (patient: Patient) => void;
}

const PatientSelector: React.FC<PatientSelectorProps> = ({ onPatientSelect, selectedPatientId, onEditPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        const data = await patientService.getPatients();
        setPatients(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching patients:', err);
        setError('Failed to load patients. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  const handlePatientChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const patientId = e.target.value;
    if (patientId === '') {
      onPatientSelect(null);
    } else {
      const selectedPatient = patients.find(p => p.id === parseInt(patientId));
      if (selectedPatient) {
        onPatientSelect(selectedPatient);
      }
    }
  };

  if (loading) {
    return <div className="patient-selector-loading">Loading patients...</div>;
  }

  if (error) {
    return <div className="patient-selector-error">{error}</div>;
  }

  const selectedPatient = patients.find(p => p.id === selectedPatientId);
  
  return (
    <div className="patient-selector">
      <div className="patient-selector-container">
        <select 
          value={selectedPatientId?.toString() || ''}
          onChange={handlePatientChange}
          className="patient-select"
        >
          <option value="">Select a patient</option>
          {patients.map(patient => (
            <option key={patient.id} value={patient.id}>
              {patient.first_name} {patient.last_name}
            </option>
          ))}
        </select>
        
        {selectedPatient && onEditPatient && (
          <button 
            className="edit-patient-btn" 
            onClick={() => onEditPatient(selectedPatient)}
            title="Edit patient"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
            </svg>
            Edit
          </button>
        )}
      </div>
    </div>
  );
};

export default PatientSelector;
