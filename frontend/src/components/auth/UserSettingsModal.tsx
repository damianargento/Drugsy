import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UserInfo } from '../../services/authService';
import { BACKEND_URL } from '../../config';
import './Auth.css';

// Usamos la interfaz UserInfo importada del servicio de autenticación

interface UserSettingsModalProps {
  onClose: () => void;
  userInfo: UserInfo;
  token: string;
  onUpdateSuccess: (updatedUserInfo: UserInfo) => void;
}

const UserSettingsModal: React.FC<UserSettingsModalProps> = ({ 
  onClose, 
  userInfo, 
  token,
  onUpdateSuccess
}) => {
  const [firstName, setFirstName] = useState(userInfo.first_name || '');
  const [lastName, setLastName] = useState(userInfo.last_name || '');
  const [email, setEmail] = useState(userInfo.email || '');
  const [medications, setMedications] = useState<Array<{
    name: string;
    dosage: string;
    frequency: string;
  }>>(
    userInfo.medications || [{ name: '', dosage: '', frequency: '' }]
  );
  const [chronicConditions, setChronicConditions] = useState(userInfo.chronic_conditions || '');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Agregar una nueva medicación vacía
  const addMedication = () => {
    setMedications([...medications, { name: '', dosage: '', frequency: '' }]);
  };

  // Eliminar una medicación por índice
  const removeMedication = (index: number) => {
    const updatedMedications = [...medications];
    updatedMedications.splice(index, 1);
    setMedications(updatedMedications);
  };

  // Actualizar un campo de medicación
  const updateMedication = (index: number, field: 'name' | 'dosage' | 'frequency', value: string) => {
    const updatedMedications = [...medications];
    updatedMedications[index] = {
      ...updatedMedications[index],
      [field]: value
    };
    setMedications(updatedMedications);
  };

  // Enviar el formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsLoading(true);

    // Filtrar medicaciones vacías
    const filteredMedications = medications.filter(
      med => med.name.trim() !== '' || med.dosage.trim() !== '' || med.frequency.trim() !== ''
    );

    try {
      const response = await axios.put(
        `${BACKEND_URL}/users/me`,
        {
          first_name: firstName,
          last_name: lastName,
          email,
          medications: filteredMedications.length > 0 ? filteredMedications : null,
          chronic_conditions: chronicConditions.trim() !== '' ? chronicConditions : null
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setSuccessMessage('Settings updated successfully!');
      onUpdateSuccess(response.data);
      
      // Cerrar el modal después de 2 segundos
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error: any) {
      console.error('Error updating settings:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        // Convertir el detalle del error a string si es un objeto
        const errorDetail = error.response.data.detail;
        if (typeof errorDetail === 'object') {
          setError(JSON.stringify(errorDetail));
        } else {
          setError(String(errorDetail));
        }
      } else {
        setError('Failed to update settings. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content settings-modal">
        <h2>User Settings</h2>
        {error && <div className="error-message">{error}</div>}
        {successMessage && <div className="success-message">{successMessage}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="firstName">First Name</label>
            <input
              type="text"
              id="firstName"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="lastName">Last Name</label>
            <input
              type="text"
              id="lastName"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Medications</label>
            {medications.map((medication, index) => (
              <div key={index} className="medication-row">
                <div className="medication-fields">
                  <input
                    type="text"
                    placeholder="Medication name"
                    value={medication.name}
                    onChange={(e) => updateMedication(index, 'name', e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Dosage"
                    value={medication.dosage}
                    onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Frequency"
                    value={medication.frequency}
                    onChange={(e) => updateMedication(index, 'frequency', e.target.value)}
                  />
                </div>
                {medications.length > 1 && (
                  <button
                    type="button"
                    className="remove-button"
                    onClick={() => removeMedication(index)}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              className="add-button"
              onClick={addMedication}
            >
              + Add Medication
            </button>
          </div>
          
          <div className="form-group">
            <label htmlFor="chronicConditions">Chronic Conditions</label>
            <textarea
              id="chronicConditions"
              value={chronicConditions}
              onChange={(e) => setChronicConditions(e.target.value)}
              rows={4}
            />
          </div>
          
          <div className="button-group">
            <button
              type="button"
              className="cancel-button"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="save-button"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserSettingsModal;
