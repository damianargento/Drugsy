import axios from 'axios';
import { BACKEND_URL } from '../config';
import { jwtDecode } from 'jwt-decode';

// Token interface
interface DecodedToken {
  exp: number;
  sub: string;
  token_type: string;
}

// Save access token to local storage
const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

// Get access token from local storage
const getToken = (): string | null => {
  return localStorage.getItem('token');
};

// Remove access token from local storage
const removeToken = () => {
  localStorage.removeItem('token');
};

// Save refresh token to local storage
const setRefreshToken = (token: string) => {
  localStorage.setItem('refreshToken', token);
};

// Get refresh token from local storage
const getRefreshToken = (): string | null => {
  return localStorage.getItem('refreshToken');
};

// Remove refresh token from local storage
const removeRefreshToken = () => {
  localStorage.removeItem('refreshToken');
};

// Check if token is expired
const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true; // If there's an error decoding, consider the token expired
  }
};

// Definir la interfaz para la información del usuario
export interface UserInfo {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

// Save user info to local storage
const setUserInfo = (userInfo: UserInfo) => {
  localStorage.setItem('userInfo', JSON.stringify(userInfo));
};

// Get user info from local storage
const getUserInfo = (): UserInfo | null => {
  const userInfoStr = localStorage.getItem('userInfo');
  return userInfoStr ? JSON.parse(userInfoStr) : null;
};

// Remove user info from local storage
const removeUserInfo = () => {
  localStorage.removeItem('userInfo');
};

// Set auth header for axios requests
const setAuthHeader = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Initialize auth header from local storage
const initAuthHeader = () => {
  const token = getToken();
  setAuthHeader(token);
};

// Login user
const login = async (email: string, password: string) => {
  const response = await axios.post(`${BACKEND_URL}/token`, {
    username: email,
    password: password,
  });
  
  const accessToken = response.data.access_token;
  const refreshToken = response.data.refresh_token;
  
  // Store both tokens
  setToken(accessToken);
  setRefreshToken(refreshToken);
  setAuthHeader(accessToken);
  
  // Get user info
  const userResponse = await axios.get(`${BACKEND_URL}/users/me`);
  setUserInfo(userResponse.data);
  
  return {
    token: accessToken,
    refreshToken,
    userInfo: userResponse.data
  };
};

// Refresh access token using refresh token
const refreshToken = async (): Promise<string | null> => {
  try {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
      return null;
    }
    
    const response = await axios.post(`${BACKEND_URL}/token/refresh`, {
      refresh_token: refreshToken
    });
    
    const newAccessToken = response.data.access_token;
    const newRefreshToken = response.data.refresh_token;
    
    // Store the new tokens
    setToken(newAccessToken);
    setRefreshToken(newRefreshToken);
    setAuthHeader(newAccessToken);
    
    return newAccessToken;
  } catch (error) {
    // If refresh token is invalid or expired, logout the user
    logout();
    return null;
  }
};

// Register user
const register = async (userData: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}) => {
  const response = await axios.post(`${BACKEND_URL}/register`, userData);
  return response.data;
};

// Logout user
const logout = () => {
  removeToken();
  removeRefreshToken();
  removeUserInfo();
  setAuthHeader(null);
};

// Check if user is authenticated
const isAuthenticated = (): boolean => {
  const token = getToken();
  return !!token && !isTokenExpired(token);
};

// Verify token validity and refresh if needed
const verifyTokenAndRefresh = async (): Promise<boolean> => {
  const token = getToken();
  
  // If no token exists, user is not authenticated
  if (!token) {
    return false;
  }
  
  // If token is not expired, user is authenticated
  if (!isTokenExpired(token)) {
    return true;
  }
  
  // If token is expired, try to refresh it
  const newToken = await refreshToken();
  return !!newToken;
};

// Actualizar información del usuario
const updateUserSettings = async (userData: Partial<UserInfo>, token: string) => {
  const response = await axios.put(`${BACKEND_URL}/users/me`, userData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  // Actualizar la información del usuario en el almacenamiento local
  setUserInfo(response.data);
  
  return response.data;
};

// Delete user account and all associated data
const deleteAccount = async (): Promise<{ message: string }> => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/users/me`);
    // Logout after successful account deletion
    logout();
    return response.data;
  } catch (error) {
    console.error('Error deleting account:', error);
    throw error;
  }
};

// Request password reset
const forgotPassword = async (email: string): Promise<{ message: string }> => {
  try {
    const response = await axios.post(`${BACKEND_URL}/forgot-password`, { email });
    return response.data;
  } catch (error) {
    console.error('Error requesting password reset:', error);
    throw error;
  }
};

// Reset password with token
const resetPassword = async (token: string, new_password: string): Promise<{ message: string }> => {
  try {
    const response = await axios.post(`${BACKEND_URL}/reset-password`, {
      token,
      new_password
    });
    return response.data;
  } catch (error) {
    console.error('Error resetting password:', error);
    throw error;
  }
};

const authService = {
  login,
  register,
  logout,
  getToken,
  getRefreshToken,
  getUserInfo,
  isAuthenticated,
  initAuthHeader,
  setToken,
  setRefreshToken,
  setUserInfo,
  updateUserSettings,
  isTokenExpired,
  refreshToken,
  verifyTokenAndRefresh,
  deleteAccount,
  forgotPassword,
  resetPassword,
};

export default authService;
