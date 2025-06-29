import React, { useState } from 'react';
import patientService, { PatientCreate, Medication, Patient, PatientUpdate } from '../../services/patientService';
import './Patients.css';

interface PatientFormProps {
  onPatientAdded: () => void;
  onCancel: () => void;
  patient?: Patient; // If provided, we're in edit mode
  isEdit?: boolean;
}

const PatientForm: React.FC<PatientFormProps> = ({ onPatientAdded, onCancel, patient, isEdit = false }) => {
  const [firstName, setFirstName] = useState<string>(patient?.first_name || '');
  const [lastName, setLastName] = useState<string>(patient?.last_name || '');
  const [dateOfBirth, setDateOfBirth] = useState<string>(patient?.date_of_birth ? patient.date_of_birth.split('T')[0] : '');
  const [chronicConditions, setChronicConditions] = useState<string>(patient?.chronic_conditions || '');
  const [medications, setMedications] = useState<Medication[]>(
    patient?.medications?.length ? patient.medications : [{ name: '', dosage: '', frequency: '' }]
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddMedication = () => {
    setMedications([...medications, { name: '', dosage: '', frequency: '' }]);
  };

  const handleRemoveMedication = (index: number) => {
    const updatedMedications = [...medications];
    updatedMedications.splice(index, 1);
    setMedications(updatedMedications);
  };

  const handleMedicationChange = (index: number, field: keyof Medication, value: string) => {
    const updatedMedications = [...medications];
    updatedMedications[index][field] = value;
    setMedications(updatedMedications);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!firstName.trim() || !lastName.trim() || !dateOfBirth) {
      setError('Please fill in all required fields');
      return;
    }

    // Filter out empty medications
    const filteredMedications = medications.filter(med => med.name.trim() !== '');

    const patientData: PatientCreate | PatientUpdate = {
      first_name: firstName,
      last_name: lastName,
      date_of_birth: dateOfBirth,
      chronic_conditions: chronicConditions.trim() || undefined,
      medications: filteredMedications.length > 0 ? filteredMedications : undefined
    };

    try {
      setLoading(true);
      if (isEdit && patient?.id) {
        await patientService.updatePatient(patient.id, patientData);
      } else {
        await patientService.createPatient(patientData as PatientCreate);
      }
      onPatientAdded();
      setError(null);
    } catch (err) {
      console.error(`Error ${isEdit ? 'updating' : 'creating'} patient:`, err);
      setError(`Failed to ${isEdit ? 'update' : 'create'} patient. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="patient-form-container">
      <h2>{isEdit ? 'Edit Patient' : 'Add New Patient'}</h2>
      {error && <div className="patient-form-error">{error}</div>}
      <form onSubmit={handleSubmit} className="patient-form">
        <div className="form-group">
          <label htmlFor="firstName">First Name *</label>
          <input
            type="text"
            id="firstName"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="lastName">Last Name *</label>
          <input
            type="text"
            id="lastName"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="dateOfBirth">Date of Birth *</label>
          <input
            type="date"
            id="dateOfBirth"
            value={dateOfBirth}
            onChange={(e) => setDateOfBirth(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="chronicConditions">Chronic Conditions</label>
          <textarea
            id="chronicConditions"
            value={chronicConditions}
            onChange={(e) => setChronicConditions(e.target.value)}
            rows={3}
          />
        </div>
        
        <div className="medications-section">
          <h3>Medications</h3>
          {medications.map((medication, index) => (
            <div key={index} className="medication-item">
              <div className="medication-fields">
                <input
                  type="text"
                  placeholder="Medication name"
                  value={medication.name}
                  onChange={(e) => handleMedicationChange(index, 'name', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Dosage"
                  value={medication.dosage}
                  onChange={(e) => handleMedicationChange(index, 'dosage', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Frequency"
                  value={medication.frequency}
                  onChange={(e) => handleMedicationChange(index, 'frequency', e.target.value)}
                />
                <button 
                  type="button" 
                  className="remove-medication-btn"
                  onClick={() => handleRemoveMedication(index)}
                  title="Remove medication"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fillRule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                  </svg>
                </button>
              </div>
            </div>
          ))}
          <button 
            type="button" 
            className="add-medication-btn"
            onClick={handleAddMedication}
          >
            Add Medication
          </button>
        </div>
        
        <div className="form-actions">
          <button type="button" onClick={onCancel} className="cancel-btn">
            Cancel
          </button>
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Saving...' : isEdit ? 'Update Patient' : 'Save Patient'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PatientForm;
