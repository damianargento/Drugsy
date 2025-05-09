import React, { useState } from 'react';
import axios from 'axios';
import { UserInfo } from '../../services/authService';
import './Auth.css';

interface RegisterModalProps {
  onClose: () => void;
  onRegister: (token: string, userInfo: any) => void;
  onLoginClick: () => void;
}

const RegisterModal: React.FC<RegisterModalProps> = ({ onClose, onRegister, onLoginClick }) => {
  // Estado para controlar el paso actual del registro
  const [step, setStep] = useState(1);
  
  // Datos del paso 1
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Datos del paso 2
  const [medications, setMedications] = useState<Array<{
    name: string;
    dosage: string;
    frequency: string;
  }>>([{ name: '', dosage: '', frequency: '' }]);
  const [chronicConditions, setChronicConditions] = useState('');
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

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

  // Manejar el paso 1 del formulario
  const handleStep1Submit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    // Avanzar al paso 2
    setStep(2);
  };

  // Manejar el paso 2 del formulario y completar el registro
  const handleStep2Submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Filtrar medicaciones vacías
    const filteredMedications = medications.filter(
      med => med.name.trim() !== '' || med.dosage.trim() !== '' || med.frequency.trim() !== ''
    );

    try {
      // Register the user with all information
      const registerResponse = await axios.post('http://localhost:9000/register', {
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
        medications: filteredMedications.length > 0 ? filteredMedications : null,
        chronic_conditions: chronicConditions.trim() !== '' ? chronicConditions : null
      });

      // If registration is successful, login automatically
      // Usar URLSearchParams para enviar los datos en formato form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const tokenResponse = await axios.post('http://localhost:9000/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const token = tokenResponse.data.access_token;

      // Call the onRegister callback with the token and user info
      onRegister(token, registerResponse.data);
    } catch (error: any) {
      console.error('Registration error:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        // Convertir el detalle del error a string si es un objeto
        const errorDetail = error.response.data.detail;
        if (typeof errorDetail === 'object') {
          setError(JSON.stringify(errorDetail));
        } else {
          setError(String(errorDetail));
        }
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Volver al paso 1
  const goBackToStep1 = () => {
    setStep(1);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>{step === 1 ? 'Register' : 'Health Information'}</h2>
        {error && <div className="error-message">{error}</div>}
        
        {step === 1 ? (
          // Paso 1: Información básica
          <form onSubmit={handleStep1Submit}>
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
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-actions">
              <button type="button" onClick={onClose} className="cancel-button">
                Cancel
              </button>
              <button type="submit" className="submit-button">
                Next
              </button>
            </div>
          </form>
        ) : (
          // Paso 2: Información de salud
          <form onSubmit={handleStep2Submit}>
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
            
            <div className="form-actions">
              <button type="button" onClick={goBackToStep1} className="cancel-button">
                Back
              </button>
              <button type="submit" className="submit-button" disabled={isLoading}>
                {isLoading ? 'Registering...' : 'Complete Registration'}
              </button>
            </div>
          </form>
        )}
        
        {step === 1 && (
          <div className="switch-form">
            Already have an account?{' '}
            <button type="button" onClick={onLoginClick} className="text-button">
              Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegisterModal;
