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
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // No medication or chronic conditions management needed anymore

  // Enviar el formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsLoading(true);

    try {
      const response = await axios.put(
        `${BACKEND_URL}/users/me`,
        {
          first_name: firstName,
          last_name: lastName,
          email
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
          
          {/* Medications and chronic conditions fields removed */}
          
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
