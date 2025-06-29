import React, { useState } from 'react';
import LoginModal from './LoginModal';
import RegisterModal from './RegisterModal';
import UserMenu from './UserMenu';
import UserSettingsModal from './UserSettingsModal';
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

  const handleUpdateSuccess = (updatedUserInfo: UserInfo) => {
    // Update user info in global state
    login(localStorage.getItem('token') || '', updatedUserInfo);
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
          onLogin={login}
          onRegisterClick={() => {
            setShowLoginModal(false);
            setShowRegisterModal(true);
          }}
        />
      )}

      {showRegisterModal && (
        <RegisterModal
          onClose={() => setShowRegisterModal(false)}
          onRegister={(token: string, userInfo: any) => {
            login(token, userInfo);
            setShowRegisterModal(false);
          }}
          onLoginClick={() => {
            setShowRegisterModal(false);
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
    </div>
  );
};

export default AuthButton;
