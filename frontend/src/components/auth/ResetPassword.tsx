import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import authService from '../../services/authService';
import './Auth.css';

const ResetPassword: React.FC = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [token, setToken] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const tokenParam = queryParams.get('token');
    
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      setError('Invalid or missing reset token');
    }
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      if (!password) {
        setError('Please enter a new password');
        setIsSubmitting(false);
        return;
      }

      if (password.length < 8) {
        setError('Password must be at least 8 characters long');
        setIsSubmitting(false);
        return;
      }

      if (password !== confirmPassword) {
        setError('Passwords do not match');
        setIsSubmitting(false);
        return;
      }

      if (!token) {
        setError('Invalid or missing reset token');
        setIsSubmitting(false);
        return;
      }

      const response = await authService.resetPassword(token, password);
      setSuccess(response.message);
      
      setPassword('');
      setConfirmPassword('');
      
      setTimeout(() => {
        window.location.href = '/login';
      }, 3000);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Reset Password</h2>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="password">New Password</label>
            <input
              type="password"
              id="password"
              name="password"
              autoComplete="new-password"
              value={password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              required
              disabled={!token || isSubmitting || !!success}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={confirmPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
              required
              disabled={!token || isSubmitting || !!success}
            />
          </div>
          
          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => window.history.back()} 
              className="cancel-button"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="submit-button" 
              disabled={!token || isSubmitting || !!success}
            >
              {isSubmitting ? 'Resetting...' : 'Set New Password'}
            </button>
          </div>
        </form>
        
        <div className="switch-form">
          <button type="button" onClick={() => window.history.back()} className="text-button">
            Back to Login
          </button>
        </div>
        
        {success && (
          <div className="success-redirect">
            Redirecting to login in 3 seconds...
          </div>
        )}
      </div>
    </div>
  );
};

export default ResetPassword;
