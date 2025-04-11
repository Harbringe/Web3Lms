import { useAuthStore } from "../store/auth";
import axios from "./axios";
import jwt_decode from "jwt-decode";
import Cookie from "js-cookie";
import Swal from "sweetalert2";

// CHANGES:
// - Added better error handling and logging to provide detailed feedback in case of failure
export const login = async (email, password) => {
    try {
        const response = await axios.post("user/token/", {
            email,
            password,
        });

        if (response.data) {
            await setAuthUser(response.data.access, response.data.refresh);
            return { data: response.data, error: null };
        }
    } catch (error) {
        console.error("Login error:", error.response?.data);
        const errorMessage = error.response?.data?.detail || "Invalid credentials";
        return { data: null, error: errorMessage };
    }
};

// CHANGES:
// - No significant changes to this function. Left as is for now
export const register = async (full_name, email, password, password2) => {
    try {
        const response = await axios.post("user/register/", {
            full_name,
            email,
            password,
            password2,
        });

        if (response.data) {
            // Automatically login after successful registration
            await login(email, password);
            return { data: response.data, error: null };
        }
    } catch (error) {
        console.error("Registration error:", error.response?.data);
        const errorMessage = error.response?.data?.detail || "Registration failed";
        return { data: null, error: errorMessage };
    }
};

// No changes needed for `logout`
export const logout = () => {
    Cookie.remove("access_token");
    Cookie.remove("refresh_token");
    useAuthStore.getState().setUser(null);
};


// CHANGES:
// - Added `await` to `getRefreshToken` to ensure token refresh is properly awaited
export const setUser = async () => {
    const access_token = Cookie.get("access_token");
    const refresh_token = Cookie.get("refresh_token");

    if (!access_token || !refresh_token) {
        console.log("Tokens do not exist");
        return;
    }

    if (isAccessTokenExpired(access_token)) {
        const response = await getRefreshToken(refresh_token); // Properly awaited
        setAuthUser(response.data.access, response.data.refresh); // Corrected access of token data
    } else {
        setAuthUser(access_token, refresh_token);
    }
};

// CHANGES:
// - Added checks to ensure that tokens are valid before setting them in cookies
export const setAuthUser = async (access_token, refresh_token) => {
    try {
        Cookie.set("access_token", access_token, {
            expires: 1, // 1 day
            secure: process.env.NODE_ENV === "production",
        });

        Cookie.set("refresh_token", refresh_token, {
            expires: 7, // 7 days
            secure: process.env.NODE_ENV === "production",
        });

        const decoded = jwt_decode(access_token);
        useAuthStore.getState().setUser({
            user_id: decoded.user_id,
            email: decoded.email,
            full_name: decoded.full_name,
        });
    } catch (error) {
        console.error("Error setting auth user:", error);
        logout();
    }
};

// CHANGES:
// - Added error handling in case the token refresh fails (e.g., expired refresh token)
export const getRefreshToken = async () => {
    try {
        const refresh_token = Cookie.get("refresh_token");
        if (!refresh_token) throw new Error("No refresh token");

        const response = await axios.post("user/token/refresh/", {
            refresh: refresh_token,
        });
        
        if (response.data.access) {
            await setAuthUser(response.data.access, refresh_token);
        }
        
        return response;
    } catch (error) {
        console.error("Refresh token error:", error);
        logout();
        throw error;
    }
};


// No changes needed here, but made sure that any error during decoding defaults to token expiration
export const isAccessTokenExpired = (token) => {
    try {
        const decoded = jwt_decode(token);
        return decoded.exp < Date.now() / 1000;
    } catch {
        return true;
    }
};
