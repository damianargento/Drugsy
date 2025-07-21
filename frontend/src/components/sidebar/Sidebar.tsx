import React, { useState } from 'react';
import './Sidebar.css';
import PatientManagement from '../../components/patients/PatientManagement';
import { Patient } from '../../services/patientService';
import { useAuth } from '../../contexts/AuthContext';
import { usePatient } from '../../contexts/PatientContext';

const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isLoggedIn } = useAuth();
  const { selectedPatient, setSelectedPatient } = usePatient();

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handlePatientSelect = (patient: Patient | null) => {
    setSelectedPatient(patient);
  };

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <button className="toggle-button" onClick={toggleSidebar}>
        {isOpen ? '✕' : '☰'}
      </button>
      
      {isOpen && (
        <div className="sidebar-auth">
          {isLoggedIn && (
            <div className="patient-section">
              <PatientManagement 
                onPatientSelect={handlePatientSelect}
                selectedPatientId={selectedPatient?.id}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Sidebar;
