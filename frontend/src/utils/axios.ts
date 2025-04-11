import axios, { AxiosInstance } from 'axios';
import { getRefreshToken, isAccessTokenExpired, logout } from './auth';
import Cookie from 'js-cookie';
import Cookies from 'js-cookie';

const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1/',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-CSRFToken': Cookies.get('csrftoken'),
  },
});

api.interceptors.request.use(
  async (config) => {
    const accessToken = Cookie.get('access_token');
    
    if (accessToken) {
      if (isAccessTokenExpired(accessToken)) {
        try {
          const response = await getRefreshToken();
          const newAccessToken = response.data.access;
          config.headers.Authorization = `Bearer ${newAccessToken}`;
        } catch (error) {
          console.error('Token refresh failed:', error);
          logout();
        }
      } else {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
    }
    
    config.headers['X-CSRFToken'] = Cookies.get('csrftoken');
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      logout();
    }
    return Promise.reject(error);
  }
);

export default api; 