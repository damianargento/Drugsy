import React, { useState, FormEvent, ChangeEvent } from 'react';
import authService from '../../services/authService';
import './Auth.css';

interface ForgotPasswordModalProps {
  onClose: () => void;
  onLoginClick: () => void;
}

const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({ onClose, onLoginClick }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      // Validate email
      if (!email) {
        setError('Please enter your email address');
        setIsSubmitting(false);
        return;
      }

      // Request password reset
      const response = await authService.forgotPassword(email);
      setSuccess(response.message);
      setEmail('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Forgot Password</h2>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              required
              disabled={!!success}
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
              {isSubmitting ? 'Sending...' : 'Reset Password'}
            </button>
          </div>
        </form>
        
        <div className="switch-form">
          Remember your password?{' '}
          <button type="button" onClick={onLoginClick} className="text-button">
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordModal;
