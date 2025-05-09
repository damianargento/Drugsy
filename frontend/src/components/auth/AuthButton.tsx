import React, { useState } from 'react';
import LoginModal from './LoginModal';
import RegisterModal from './RegisterModal';
import UserMenu from './UserMenu';
import UserSettingsModal from './UserSettingsModal';
import { UserInfo } from '../../services/authService';
import './Auth.css';

// Usar la interfaz UserInfo importada del servicio de autenticación

interface AuthButtonProps {
  isLoggedIn: boolean;
  userInfo: UserInfo | null;
  onLogin: (token: string, userInfo: UserInfo) => void;
  onLogout: () => void;
}

const AuthButton: React.FC<AuthButtonProps> = ({ 
  isLoggedIn, 
  userInfo, 
  onLogin, 
  onLogout 
}) => {
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
    onLogout();
  };

  const handleSettingsClick = () => {
    setShowSettingsModal(true);
  };

  const handleUpdateSuccess = (updatedUserInfo: UserInfo) => {
    // Actualizar la información del usuario en el estado global
    onLogin(localStorage.getItem('token') || '', updatedUserInfo);
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
          onLogin={onLogin}
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
            onLogin(token, userInfo);
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
