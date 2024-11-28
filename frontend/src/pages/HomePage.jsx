import React from "react";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
    const navigate = useNavigate();

    // Récupérer les coordonnées stockées dans le localStorage
    const coordinates = JSON.parse(localStorage.getItem("coordinates"));

    // Afficher les coordonnées dans la console
    console.log("Coordinates:", coordinates);

    const handleLogout = () => {
        localStorage.clear(); // Efface les données utilisateur
        navigate("/"); // Redirige vers la Landing Page
    };

    return (
        <div>
            <h1>Home Page</h1>
            <p>Welcome! You are using the profile: {localStorage.getItem("profile")}</p>
            <p>Selected country: {localStorage.getItem("country")}</p>
            <p>Coordinates: {coordinates ? `Latitude: ${coordinates[0]}, Longitude: ${coordinates[1]}` : "Not available"}</p>
            <button onClick={handleLogout}>Change Profile / Country</button>
        </div>
    );
};

export default HomePage;
