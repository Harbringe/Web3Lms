"use client"; // Ensures it runs only on the client side

import { useEffect, useState, ReactNode } from "react";
import { setUser } from "@/utils/auth";

interface MainWrapperProps {
    children: ReactNode;
}

const MainWrapper: React.FC<MainWrapperProps> = ({ children }) => {
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const checkUser = async () => {
            setLoading(true);
            await setUser(); // Check and set the authenticated user
            setLoading(false);
        };

        checkUser();
    }, []);

    return loading ? <p>Loading...</p> : <>{children}</>;
};

export default MainWrapper;
