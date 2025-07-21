import React, { useState } from 'react';
import PatientSelector from './PatientSelector';
import PatientForm from './PatientForm';
import { Patient } from '../../services/patientService';
import './Patients.css';

interface PatientManagementProps {
  onPatientSelect: (patient: Patient | null) => void;
  selectedPatientId?: number | null;
}

const PatientManagement: React.FC<PatientManagementProps> = ({ onPatientSelect, selectedPatientId }) => {
  const [showPatientModal, setShowPatientModal] = useState<boolean>(false);
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [currentPatient, setCurrentPatient] = useState<Patient | undefined>(undefined);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const handleAddPatientClick = () => {
    setIsEditMode(false);
    setCurrentPatient(undefined);
    setShowPatientModal(true);
  };
  
  const handleEditPatientClick = (patient: Patient) => {
    setIsEditMode(true);
    setCurrentPatient(patient);
    setShowPatientModal(true);
  };

  const handlePatientAdded = () => {
    setShowPatientModal(false);
    // Trigger a refresh of the patient selector
    setRefreshKey(prevKey => prevKey + 1);
  };

  const handleCancelPatientForm = () => {
    setShowPatientModal(false);
  };

  return (
    <div className="patient-management">
      <div className="patient-management-header">
        <div className="patient-management-title">Patients</div>
      </div>
      
      <PatientSelector 
        key={refreshKey}
        onPatientSelect={onPatientSelect}
        selectedPatientId={selectedPatientId}
        onEditPatient={handleEditPatientClick}
      />
      
      <button className="add-patient-btn sidebar-add-btn" onClick={handleAddPatientClick}>
        Add Patient
      </button>
      
      {showPatientModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="close-modal-btn" onClick={handleCancelPatientForm}>×</button>
            <PatientForm 
              onPatientAdded={handlePatientAdded}
              onCancel={handleCancelPatientForm}
              patient={currentPatient}
              isEdit={isEditMode}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientManagement;
