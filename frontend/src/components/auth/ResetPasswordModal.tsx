import React, { useState, FormEvent, ChangeEvent } from 'react';
import authService from '../../services/authService';
import './Auth.css';

interface ResetPasswordModalProps {
  onClose: () => void;
  onLoginClick: () => void;
  token: string;
}

const ResetPasswordModal: React.FC<ResetPasswordModalProps> = ({ onClose, onLoginClick, token }) => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      // Validate inputs
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

      // Reset password
      const response = await authService.resetPassword(token, password);
      setSuccess(response.message);
      
      // Clear form
      setPassword('');
      setConfirmPassword('');
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        onLoginClick();
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
              value={password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              required
              disabled={isSubmitting || !!success}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
              required
              disabled={isSubmitting || !!success}
            />
          </div>
          
          <div className="form-actions">
            <button type="button" onClick={onClose} className="cancel-button">
              Cancel
            </button>
            <button 
              type="submit" 
              className="submit-button" 
              disabled={isSubmitting || !!success}
            >
              {isSubmitting ? 'Resetting...' : 'Set New Password'}
            </button>
          </div>
        </form>
        
        {success && (
          <div className="success-redirect">
            Redirecting to login in 3 seconds...
          </div>
        )}
      </div>
    </div>
  );
};

export default ResetPasswordModal;
