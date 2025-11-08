import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  useEffect(() => {
    // Check if user is already logged in
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  async function fetchCurrentUser() {
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // Token might be invalid, clear it
      logout();
    } finally {
      setLoading(false);
    }
  }

  async function login(email, password) {
    try {
      console.log('Login attempt:', email);
      const response = await api.login(email, password);
      console.log('Login response:', response);

      const { access_token, user: userData } = response;

      if (!access_token || !userData) {
        console.error('Invalid response structure:', response);
        throw new Error('Invalid response from server');
      }

      console.log('Setting token and user...');
      localStorage.setItem('auth_token', access_token);
      setToken(access_token);
      setUser(userData);
      console.log('User state updated:', userData);
      console.log('Token stored:', access_token);

      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        error: error.message || 'Login failed. Please check your credentials.'
      };
    }
  }

  async function register(email, username, password, fullName) {
    try {
      const response = await api.register(email, username, password, fullName);
      const { access_token, user: userData } = response;

      localStorage.setItem('auth_token', access_token);
      setToken(access_token);
      setUser(userData);

      return { success: true };
    } catch (error) {
      console.error('Registration failed:', error);
      return {
        success: false,
        error: error.message || 'Registration failed. Please try again.'
      };
    }
  }

  function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('chat.conversations');
    localStorage.removeItem('chat.messages');
    setToken(null);
    setUser(null);
  }

  async function updateProfile(updates) {
    try {
      const updatedUser = await api.updateProfile(updates);
      setUser(updatedUser);
      return { success: true };
    } catch (error) {
      console.error('Profile update failed:', error);
      return {
        success: false,
        error: error.message || 'Profile update failed.'
      };
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
