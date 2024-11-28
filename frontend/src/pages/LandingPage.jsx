import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const LandingPage = () => {
    const [profile, setProfile] = useState(""); // Profil de l'utilisateur
    const [countries, setCountries] = useState([]); // Liste des pays
    const [selectedCountry, setSelectedCountry] = useState(""); // Pays sélectionné
    const [capitalCoordinates, setCapitalCoordinates] = useState(null); // Coordonnées GPS
    const navigate = useNavigate();

    // Charger la liste des pays au montage
    useEffect(() => {
        fetch("https://restcountries.com/v3.1/all")
            .then((response) => response.json())
            .then((data) => {
                const countryList = data.map((country) => ({
                    name: country.name.common,
                    capital: country.capital ? country.capital[0] : "Unknown",
                    latlng: country.capitalInfo?.latlng || null,
                }));
                setCountries(countryList.sort((a, b) => a.name.localeCompare(b.name)));
            })
            .catch((error) => console.error("Error fetching countries:", error));
    }, []);

    const handleProfileChange = (event) => {
        setProfile(event.target.value);
    };

    const handleCountryChange = (event) => {
        const selected = countries.find((c) => c.name === event.target.value);
        setSelectedCountry(selected.name);
        setCapitalCoordinates(selected.latlng);
    };

    const handleSubmit = () => {
        if (profile && selectedCountry && capitalCoordinates) {
            // Stocker les informations dans localStorage
            localStorage.setItem("profile", profile);
            localStorage.setItem("country", selectedCountry);
            localStorage.setItem("coordinates", JSON.stringify(capitalCoordinates));
            // Rediriger vers la page d'accueil
            navigate("/home");
        } else {
            alert("Please select a profile and a country.");
        }
    };

    return (
        <div>
            <h1>Welcome to TripAdvisor Clone</h1>
            <div>
                <h2>Select your profile</h2>
                <label>
                    <input
                        type="radio"
                        value="local"
                        checked={profile === "local"}
                        onChange={handleProfileChange}
                    />
                    Local
                </label>
                <label>
                    <input
                        type="radio"
                        value="tourist"
                        checked={profile === "tourist"}
                        onChange={handleProfileChange}
                    />
                    Tourist
                </label>
                <label>
                    <input
                        type="radio"
                        value="professional"
                        checked={profile === "professional"}
                        onChange={handleProfileChange}
                    />
                    Professional
                </label>
            </div>
            <div>
                <h2>Select your country</h2>
                <select value={selectedCountry} onChange={handleCountryChange}>
                    <option value="">-- Select a Country --</option>
                    {countries.map((country) => (
                        <option key={country.name} value={country.name}>
                            {country.name}
                        </option>
                    ))}
                </select>
            </div>
            <button onClick={handleSubmit}>Continue</button>
        </div>
    );
};

export default LandingPage;
