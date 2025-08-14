import React, { useState, useEffect } from 'react';
import patientService, { Patient } from '../../services/patientService';
import './Patients.css';

interface PatientSelectorProps {
  onPatientSelect: (patient: Patient | null) => void;
  selectedPatientId?: number | null;
  onEditPatient?: (patient: Patient) => void;
  onAddPatient?: () => void;
}

// Define patient tab item type
interface PatientTabItem {
  id: number;
  name: string;
  patient: Patient;
}

const PatientSelector: React.FC<PatientSelectorProps> = ({ onPatientSelect, selectedPatientId, onEditPatient, onAddPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientTabItems, setPatientTabItems] = useState<PatientTabItem[]>([]);
  const [filteredTabItems, setFilteredTabItems] = useState<PatientTabItem[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        const data = await patientService.getPatients();
        setPatients(data);
        
        // Convert patients to tab items
        const tabItems = data.map(patient => ({
          id: patient.id,
          name: `${patient.first_name} ${patient.last_name}`,
          patient: patient
        }));
        
        setPatientTabItems(tabItems);
        setFilteredTabItems(tabItems);
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

  const handlePatientClick = (tabItem: PatientTabItem) => {
    onPatientSelect(tabItem.patient);
  };
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value.toLowerCase();
    setSearchQuery(query);
    
    if (query.trim() === '') {
      setFilteredTabItems(patientTabItems);
    } else {
      const filtered = patientTabItems.filter(item => 
        item.name.toLowerCase().includes(query)
      );
      setFilteredTabItems(filtered);
    }
  };
  
  const handleClearSearch = () => {
    setSearchQuery('');
    setFilteredTabItems(patientTabItems);
  };

  const selectedPatient = selectedPatientId
    ? patients.find(p => p.id === selectedPatientId)
    : null;
  
  if (loading) {
    return <div className="patient-selector-loading">Loading patients...</div>;
  }

  if (error) {
    return <div className="patient-selector-error">{error}</div>;
  }
  

  
  return (
    <div className="patient-selector">
      <div className="patient-selector-header">
        <div className="search-container">
          <input
            type="text"
            className="patient-search-input"
            placeholder="Search patients..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
          {searchQuery && (
            <button 
              className="clear-search-btn" 
              onClick={handleClearSearch}
              title="Clear search"
            >
              ×
            </button>
          )}
        </div>
        {onAddPatient && (
          <button 
            className="add-patient-btn header-add-btn" 
            onClick={onAddPatient}
            title="Add new patient"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
            <span>Add Patient</span>
          </button>
        )}
      </div>
      
      <div className="patient-tabs-container">
        {filteredTabItems.length === 0 && searchQuery && (
          <div className="no-patients-found">No patients found matching "{searchQuery}"</div>
        )}
        {filteredTabItems.map((tabItem) => (
          <div 
            key={tabItem.id}
            className={`patient-tab ${selectedPatientId === tabItem.id ? 'patient-tab-active' : ''}`}
            onClick={() => handlePatientClick(tabItem)}
          >
            <span className="patient-tab-name">{tabItem.name}</span>
            {selectedPatientId === tabItem.id && onEditPatient && (
              <button 
                className="edit-patient-btn tab-edit-btn" 
                onClick={(e) => {
                  e.stopPropagation();
                  onEditPatient(tabItem.patient);
                }}
                title="Edit patient"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PatientSelector;
