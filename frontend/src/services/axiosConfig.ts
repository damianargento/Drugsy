import axios from 'axios';
import authService from './authService';

// Add a response interceptor to handle 401 Unauthorized errors
axios.interceptors.response.use(
  (response) => {
    // Any status code within the range of 2xx causes this function to trigger
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is due to an unauthorized request (401) and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const newToken = await authService.refreshToken();
        
        if (newToken) {
          // If token refresh was successful, retry the original request
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return axios(originalRequest);
        } else {
          // If token refresh failed, logout the user
          authService.logout();
          // Redirect to login page or show login modal if needed
          window.location.reload(); // Force reload to reset app state
        }
      } catch (refreshError) {
        // If there was an error refreshing the token, logout the user
        authService.logout();
        // Redirect to login page or show login modal if needed
        window.location.reload(); // Force reload to reset app state
      }
    }
    
    // If the error wasn't a 401 or we've already tried to refresh, just reject the promise
    return Promise.reject(error);
  }
);

export default axios;
