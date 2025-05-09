import axios from 'axios';

const API_URL = 'http://localhost:9000';

// Save token to local storage
const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

// Get token from local storage
const getToken = (): string | null => {
  return localStorage.getItem('token');
};

// Remove token from local storage
const removeToken = () => {
  localStorage.removeItem('token');
};

// Definir la interfaz para la información del usuario
export interface UserInfo {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  medications?: Array<{
    name: string;
    dosage: string;
    frequency: string;
  }>;
  chronic_conditions?: string;
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
  const response = await axios.post(`${API_URL}/token`, {
    username: email,
    password: password,
  });
  
  const token = response.data.access_token;
  setToken(token);
  setAuthHeader(token);
  
  // Get user info
  const userResponse = await axios.get(`${API_URL}/users/me`);
  setUserInfo(userResponse.data);
  
  return {
    token,
    userInfo: userResponse.data
  };
};

// Register user
const register = async (userData: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}) => {
  const response = await axios.post(`${API_URL}/register`, userData);
  return response.data;
};

// Logout user
const logout = () => {
  removeToken();
  removeUserInfo();
  setAuthHeader(null);
};

// Check if user is authenticated
const isAuthenticated = (): boolean => {
  return !!getToken();
};

// Actualizar información del usuario
const updateUserSettings = async (userData: Partial<UserInfo>, token: string) => {
  const response = await axios.put(`${API_URL}/users/me`, userData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  // Actualizar la información del usuario en el almacenamiento local
  setUserInfo(response.data);
  
  return response.data;
};

const authService = {
  login,
  register,
  logout,
  getToken,
  getUserInfo,
  isAuthenticated,
  initAuthHeader,
  setToken,
  setUserInfo,
  updateUserSettings,
};

export default authService;
