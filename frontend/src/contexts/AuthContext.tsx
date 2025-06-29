import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import authService, { UserInfo } from '../services/authService';

// Define the shape of our context
interface AuthContextType {
  isLoggedIn: boolean;
  userInfo: UserInfo | null;
  login: (token: string, userInfo: UserInfo) => void;
  logout: () => void;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  isLoggedIn: false,
  userInfo: null,
  login: () => {},
  logout: () => {},
});

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

// Provider component that wraps the app and makes auth object available to any child component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);

  // Initialize authentication state from local storage
  useEffect(() => {
    authService.initAuthHeader();
    const token = authService.getToken();
    const storedUserInfo = authService.getUserInfo();
    
    if (token && storedUserInfo) {
      setIsLoggedIn(true);
      setUserInfo(storedUserInfo);
    }
  }, []);

  // Handle login
  const login = (token: string, userInfo: UserInfo) => {
    // Save token and user info in localStorage
    authService.setToken(token);
    authService.setUserInfo(userInfo);
    
    // Update local state
    setIsLoggedIn(true);
    setUserInfo(userInfo);
  };

  // Handle logout
  const logout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setUserInfo(null);
  };

  // Value object that will be passed to provider
  const value = {
    isLoggedIn,
    userInfo,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
