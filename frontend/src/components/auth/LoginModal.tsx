import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';
import { BACKEND_URL } from '../../config';

interface LoginModalProps {
  onClose: () => void;
  onLogin: (token: string, refreshToken: string, userInfo: any) => void;
  onRegisterClick: () => void;
  onForgotPasswordClick: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ onClose, onLogin, onRegisterClick, onForgotPasswordClick }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // First, get the token - use axios instance without global error handling
      const formData = new URLSearchParams();
      formData.append('username', email); // FastAPI OAuth2 expects 'username' field
      formData.append('password', password);
      
      // Create a new axios instance for this request to avoid global error handlers
      const axiosInstance = axios.create();
      
      try {
        const tokenResponse = await axiosInstance.post(`${BACKEND_URL}/token`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          // Prevent axios from throwing for HTTP error status codes
          validateStatus: () => true,
        });
        
        // Check if the response was successful
        if (tokenResponse.status !== 200) {
          // Handle error response
          const errorDetail = tokenResponse.data.detail || 'Authentication failed';
          setError(typeof errorDetail === 'object' ? JSON.stringify(errorDetail) : String(errorDetail));
          return; // Exit early without closing modal
        }
        
        const token = tokenResponse.data.access_token;
        const refreshToken = tokenResponse.data.refresh_token;

        // Then, get the user info using the token
        const userResponse = await axiosInstance.get(`${BACKEND_URL}/users/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          validateStatus: () => true,
        });
        
        if (userResponse.status !== 200) {
          setError('Failed to get user information');
          return; // Exit early without closing modal
        }

        // Only call onLogin on successful authentication
        onLogin(token, refreshToken, userResponse.data);
        // Close the modal explicitly on success
        onClose();
      } catch (axiosError) {
        // This will only catch network errors, not HTTP status errors
        console.error('Network error during login:', axiosError);
        setError('Network error. Please check your connection and try again.');
      }
    } catch (error: any) {
      console.error('Unexpected login error:', error);
      setError('An unexpected error occurred. Please try again.');
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
            <div className="forgot-password">
              <button type="button" onClick={onForgotPasswordClick} className="text-button">
                Forgot Password?
              </button>
            </div>
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
