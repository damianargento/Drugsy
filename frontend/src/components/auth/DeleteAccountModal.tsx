import React, { useState } from 'react';
import authService from '../../services/authService';
import './Auth.css';

interface DeleteAccountModalProps {
  onClose: () => void;
  onDeleteSuccess: () => void;
}

const DeleteAccountModal: React.FC<DeleteAccountModalProps> = ({ onClose, onDeleteSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmText, setConfirmText] = useState('');

  const handleDeleteAccount = async () => {
    if (confirmText !== 'DELETE') {
      setError('Please type DELETE to confirm account deletion');
      return;
    }

    try {
      setIsLoading(true);
      await authService.deleteAccount();
      onDeleteSuccess();
    } catch (err: any) {
      console.error('Error deleting account:', err);
      setError(err.response?.data?.detail || 'Failed to delete account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="delete-account-modal-overlay">
      <div className="delete-account-modal-content">
        <h2>Delete Account</h2>
        <p className="delete-warning">
          Warning: This action cannot be undone. All your data will be permanently deleted.
        </p>
        <p>
          This includes your account information, patients, and all other associated data.
        </p>
        <p>
          To confirm, please type <strong>DELETE</strong> in the field below:
        </p>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <input
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="Type DELETE to confirm"
            className="delete-confirm-input"
          />
        </div>
        
        <div className="delete-account-actions">
          <button 
            className="cancel-delete-btn"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button 
            className="confirm-delete-btn"
            onClick={handleDeleteAccount}
            disabled={isLoading || confirmText !== 'DELETE'}
          >
            {isLoading ? 'Deleting...' : 'Delete My Account'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteAccountModal;
