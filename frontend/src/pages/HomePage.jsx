import React from "react";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.clear(); // Efface les données utilisateur
        navigate("/"); // Redirige vers la Landing Page
    };

    return (
        <div>
            <h1>Home Page</h1>
            <p>Welcome! You are using the profile: {localStorage.getItem("profile")}</p>
            <p>Selected country: {localStorage.getItem("country")}</p>
            <button onClick={handleLogout}>Change Profile / Country</button>
        </div>
    );
};

export default HomePage;
