import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

interface LoginModalProps {
  onClose: () => void;
  onLogin: (token: string, userInfo: any) => void;
  onRegisterClick: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ onClose, onLogin, onRegisterClick }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // First, get the token
      // Usar URLSearchParams para enviar los datos en formato form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', email); // FastAPI OAuth2 expects 'username' field
      formData.append('password', password);
      
      const tokenResponse = await axios.post('http://localhost:9000/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = tokenResponse.data.access_token;

      // Then, get the user info using the token
      const userResponse = await axios.get('http://localhost:9000/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Call the onLogin callback with the token and user info
      onLogin(token, userResponse.data);
      onClose();
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        // Convertir el detalle del error a string si es un objeto
        const errorDetail = error.response.data.detail;
        if (typeof errorDetail === 'object') {
          setError(JSON.stringify(errorDetail));
        } else {
          setError(String(errorDetail));
        }
      } else {
        setError('Invalid email or password. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Login</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
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
            />
          </div>
          <div className="form-actions">
            <button type="button" onClick={onClose} className="cancel-button">
              Cancel
            </button>
            <button type="submit" className="submit-button" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </form>
        <div className="switch-form">
          Don't have an account?{' '}
          <button type="button" onClick={onRegisterClick} className="text-button">
            Register
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
