import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import authService, { UserInfo } from '../services/authService';

// Define the shape of our context
interface AuthContextType {
  isLoggedIn: boolean;
  userInfo: UserInfo | null;
  login: (token: string, refreshToken: string, userInfo: UserInfo) => void;
  logout: () => void;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  isLoggedIn: false,
  userInfo: null,
  login: (_token, _refreshToken, _userInfo) => {},
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

  // Initialize authentication state from local storage with token verification
  useEffect(() => {
    const initAuth = async () => {
      authService.initAuthHeader();
      const token = authService.getToken();
      const storedUserInfo = authService.getUserInfo();
      
      if (token && storedUserInfo) {
        // Verify if token is valid or can be refreshed
        const isValid = await authService.verifyTokenAndRefresh();
        
        if (isValid) {
          // Token is valid or was successfully refreshed
          setIsLoggedIn(true);
          setUserInfo(storedUserInfo);
        } else {
          // Token is invalid and couldn't be refreshed
          authService.logout();
          setIsLoggedIn(false);
          setUserInfo(null);
        }
      }
    };
    
    initAuth();
  }, []);

  // Handle login
  const login = (token: string, refreshToken: string, userInfo: UserInfo) => {
    // Save tokens and user info in localStorage
    authService.setToken(token);
    authService.setRefreshToken(refreshToken);
    authService.setUserInfo(userInfo);
    
    // Explicitly set the auth header to ensure it's updated immediately
    authService.setAuthHeader(token);
    
    // Update local state
    setIsLoggedIn(true);
    setUserInfo(userInfo);
    
    console.log('User logged in, auth header updated');
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
