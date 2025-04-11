import axios from "axios";
import { getRefreshToken, isAccessTokenExpired, setAuthUser } from "../utils/auth";
import Cookie from "js-cookie";

const useAxios = axios.create({
    baseURL: "http://127.0.0.1:8000/api/v1/",
    timeout: 10000000,
    headers: { "Content-Type": "application/json" },
});

useAxios.interceptors.request.use(
    async (config) => {
        let accessToken = Cookie.get("access_token");

        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }

        if (isAccessTokenExpired(accessToken)) {
            const refreshedTokens = await getRefreshToken();
            if (refreshedTokens) {
                setAuthUser(refreshedTokens.access, refreshedTokens.refresh);
                config.headers.Authorization = `Bearer ${refreshedTokens.access}`;
            }
        }

        return config;
    },
    (error) => Promise.reject(error)
);


// Response interceptor for handling errors
useAxios.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle specific error cases if needed
        if (error.response && error.response.status === 401) {
            // Handle unauthorized errors (e.g., redirect to login)
            console.error("Unauthorized access - you may need to log in:", error);
        }

        return Promise.reject(error);
    }
);


export default useAxios;
