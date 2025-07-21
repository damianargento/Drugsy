import React, { useState, useEffect } from 'react';
import LoginModal from './LoginModal';
import RegisterModal from './RegisterModal';
import UserMenu from './UserMenu';
import UserSettingsModal from './UserSettingsModal';
import ForgotPasswordModal from './ForgotPasswordModal';
import ResetPasswordModal from './ResetPasswordModal';
import { useAuth } from '../../contexts/AuthContext';
import { UserInfo } from '../../services/authService';
import './Auth.css';

// Usar la interfaz UserInfo importada del servicio de autenticación

// No longer need props as we're using context

const AuthButton: React.FC = () => {
  const { isLoggedIn, userInfo, login, logout } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);
  const [showResetPasswordModal, setShowResetPasswordModal] = useState(false);
  const [resetToken, setResetToken] = useState('');

  const handleLoginClick = () => {
    setShowLoginModal(true);
  };

  const handleRegisterClick = () => {
    setShowRegisterModal(true);
  };

  const handleLogout = () => {
    logout();
  };

  const handleSettingsClick = () => {
    setShowSettingsModal(true);
  };

  const handleForgotPasswordClick = () => {
    setShowLoginModal(false);
    setShowForgotPasswordModal(true);
  };
  
  // Check URL for reset token on component mount
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const tokenParam = queryParams.get('token');
    
    if (tokenParam) {
      setResetToken(tokenParam);
      setShowResetPasswordModal(true);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleUpdateSuccess = (updatedUserInfo: UserInfo) => {
    // Update user info in global state
    const token = localStorage.getItem('token') || '';
    const refreshToken = localStorage.getItem('refreshToken') || '';
    login(token, refreshToken, updatedUserInfo);
  };

  return (
    <div className="auth-container">
      {isLoggedIn ? (
        <>
          <UserMenu 
            userName={`${userInfo?.first_name} ${userInfo?.last_name}`}
            onSettingsClick={handleSettingsClick}
          />
          <button className="auth-button logout" onClick={handleLogout}>
            Logout
          </button>
        </>
      ) : (
        <>
          <button className="auth-button login" onClick={handleLoginClick}>
            Login
          </button>
          <button className="auth-button register" onClick={handleRegisterClick}>
            Register
          </button>
        </>
      )}

      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
          onLogin={(token, refreshToken, userInfo) => {
            login(token, refreshToken, userInfo);
          }}
          onRegisterClick={() => {
            setShowLoginModal(false);
            setShowRegisterModal(true);
          }}
          onForgotPasswordClick={handleForgotPasswordClick}
        />
      )}

      {showRegisterModal && (
        <RegisterModal
          onClose={() => setShowRegisterModal(false)}
          onRegister={(token: string, refreshToken: string, userInfo: any) => {
            login(token, refreshToken, userInfo);
            setShowRegisterModal(false);
          }}
          onLoginClick={() => {
            setShowLoginModal(true);
          }}
        />
      )}

      {showSettingsModal && userInfo && (
        <UserSettingsModal
          onClose={() => setShowSettingsModal(false)}
          userInfo={userInfo}
          token={localStorage.getItem('token') || ''}
          onUpdateSuccess={handleUpdateSuccess}
        />
      )}

      {showForgotPasswordModal && (
        <ForgotPasswordModal
          onClose={() => setShowForgotPasswordModal(false)}
          onLoginClick={() => {
            setShowForgotPasswordModal(false);
            setShowLoginModal(true);
          }}
        />
      )}

      {showResetPasswordModal && (
        <ResetPasswordModal
          onClose={() => setShowResetPasswordModal(false)}
          onLoginClick={() => {
            setShowResetPasswordModal(false);
            setShowLoginModal(true);
          }}
          token={resetToken}
        />
      )}
    </div>
  );
};

export default AuthButton;
