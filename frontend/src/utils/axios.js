import axios from "axios";
import { setAuthUser, getRefreshToken, isAccessTokenExpired, logout } from "./auth";
import Cookie from "js-cookie";

const api = axios.create({
    baseURL: "http://localhost:8000/api/v1/",
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
});

// Request interceptor
api.interceptors.request.use(
    async (config) => {
        const accessToken = Cookie.get("access_token");
        
        if (accessToken) {
            if (isAccessTokenExpired(accessToken)) {
                try {
                    const response = await getRefreshToken();
                    const newAccessToken = response.data.access;
                    config.headers.Authorization = `Bearer ${newAccessToken}`;
                } catch (error) {
                    console.error("Token refresh failed:", error);
                    logout();
                }
            } else {
                config.headers.Authorization = `Bearer ${accessToken}`;
            }
        }
        
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
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
