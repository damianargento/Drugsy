import React, { useState, useEffect } from 'react';
import patientService, { Patient } from '../../services/patientService';
import Select from 'react-select';
import './Patients.css';

interface PatientSelectorProps {
  onPatientSelect: (patient: Patient | null) => void;
  selectedPatientId?: number | null;
  onEditPatient?: (patient: Patient) => void;
}

// Define option type for react-select
interface PatientOption {
  value: number;
  label: string;
  patient: Patient;
}

const PatientSelector: React.FC<PatientSelectorProps> = ({ onPatientSelect, selectedPatientId, onEditPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientOptions, setPatientOptions] = useState<PatientOption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        const data = await patientService.getPatients();
        setPatients(data);
        
        // Convert patients to react-select options
        const options = data.map(patient => ({
          value: patient.id,
          label: `${patient.first_name} ${patient.last_name}`,
          patient: patient
        }));
        
        setPatientOptions(options);
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

  const handlePatientChange = (selectedOption: PatientOption | null) => {
    if (selectedOption) {
      onPatientSelect(selectedOption.patient);
    } else {
      // Handle case where no patient is selected
      onPatientSelect(null);
    }
  };

  const selectedPatient = selectedPatientId
    ? patients.find(p => p.id === selectedPatientId)
    : null;
    
  const selectedOption = selectedPatientId 
    ? patientOptions.find(option => option.value === selectedPatientId) 
    : null;
  
  if (loading) {
    return <div className="patient-selector-loading">Loading patients...</div>;
  }

  if (error) {
    return <div className="patient-selector-error">{error}</div>;
  }
  
  // Custom styles for react-select
  const customStyles = {
    control: (provided: any) => ({
      ...provided,
      backgroundColor: '#1A202C',
      borderColor: '#2D3748',
      color: 'white',
      boxShadow: 'none',
      '&:hover': {
        borderColor: '#4A5568'
      }
    }),
    menu: (provided: any) => ({
      ...provided,
      backgroundColor: '#1A202C',
      zIndex: 9999
    }),
    option: (provided: any, state: { isSelected: boolean; isFocused: boolean }) => ({
      ...provided,
      backgroundColor: state.isSelected 
        ? '#2C5282' 
        : state.isFocused 
          ? '#2D3748' 
          : '#1A202C',
      color: 'white',
      '&:active': {
        backgroundColor: '#2C5282'
      }
    }),
    singleValue: (provided: any) => ({
      ...provided,
      color: 'white'
    }),
    input: (provided: any) => ({
      ...provided,
      color: 'white'
    }),
    placeholder: (provided: any) => ({
      ...provided,
      color: '#A0AEC0'
    }),
    dropdownIndicator: (provided: any) => ({
      ...provided,
      color: '#A0AEC0',
      '&:hover': {
        color: 'white'
      }
    }),
    indicatorSeparator: (provided: any) => ({
      ...provided,
      backgroundColor: '#2D3748'
    })
  };
  
  // Custom components to remove indicators
  const DropdownIndicator = () => null;
  const ClearIndicator = () => null;
  
  return (
    <div className="patient-selector">
      <div className="patient-selector-container">
        <Select
          options={patientOptions}
          value={selectedOption}
          onChange={handlePatientChange}
          placeholder="Search patients..."
          isSearchable
          className="patient-select-dropdown"
          classNamePrefix="patient-select"
          styles={customStyles}
          components={{ 
            DropdownIndicator,
            ClearIndicator
          }}
        />
        
        {selectedPatient && onEditPatient && (
          <button 
            className="edit-patient-btn" 
            onClick={() => onEditPatient(selectedPatient)}
            title="Edit patient"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default PatientSelector;
