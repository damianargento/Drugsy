import React, { useState, useRef, useEffect } from 'react';
import './Auth.css';

interface UserMenuProps {
  userName: string;
  onSettingsClick: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ userName, onSettingsClick }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleSettingsClick = () => {
    onSettingsClick();
    setIsOpen(false);
  };

  // Cerrar el menú cuando se hace clic fuera de él
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="user-menu-container" ref={menuRef}>
      <div className="user-name" onClick={toggleMenu}>
        {userName} <span className="dropdown-arrow">▼</span>
      </div>
      {isOpen && (
        <div className="user-menu">
          <div className="menu-item" onClick={handleSettingsClick}>
            User Settings
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
