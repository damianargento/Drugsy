import React, { useState } from 'react';
import axios from 'axios';
import { UserInfo } from '../../services/authService';
import { BACKEND_URL } from '../../config';
import './Auth.css';

interface RegisterModalProps {
  onClose: () => void;
  onRegister: (token: string, refreshToken: string, userInfo: any) => void;
  onLoginClick: () => void;
}

const RegisterModal: React.FC<RegisterModalProps> = ({ onClose, onRegister, onLoginClick }) => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);





  // Handle form submission for registration
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    // Validate password length
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setIsLoading(false);
      return;
    }

    try {
      // Register the user
      const registerResponse = await axios.post(`${BACKEND_URL}/register`, {
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password
      });

      // If registration is successful, login automatically
      // Usar URLSearchParams para enviar los datos en formato form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const tokenResponse = await axios.post(`${BACKEND_URL}/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const token = tokenResponse.data.access_token;
      const refreshToken = tokenResponse.data.refresh_token;

      // Call the onRegister callback with the token, refresh token, and user info
      onRegister(token, refreshToken, registerResponse.data);
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

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Create Account</h2>
        {error && <div className="error-message">{error}</div>}
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
            <button type="submit" className="submit-button" disabled={isLoading}>
              {isLoading ? 'Registering...' : 'Register'}
            </button>
          </div>
        </form>
        
        <div className="switch-form">
          Already have an account?{' '}
          <button type="button" onClick={onLoginClick} className="text-button">
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegisterModal;
