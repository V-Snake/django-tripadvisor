import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Form, Button, Container, Row, Col } from "react-bootstrap";

const LandingPage = () => {
    const [profile, setProfile] = useState("");
    const [countries, setCountries] = useState([]);
    const [selectedCountry, setSelectedCountry] = useState("");
    const [capitalCoordinates, setCapitalCoordinates] = useState(null);
    const navigate = useNavigate();

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

    const handleSubmit = () => {
        if (profile && selectedCountry && capitalCoordinates) {
            localStorage.setItem("profile", profile);
            localStorage.setItem("country", selectedCountry);
            localStorage.setItem("coordinates", JSON.stringify(capitalCoordinates));
            navigate("/home");
        } else {
            alert("Please select a profile and a country.");
        }
    };

    return (
        <Container className="mt-5">
            <h1 className="text-center mb-4">Welcome to TripAdvisor Clone</h1>
            <Row>
                <Col md={6}>
                    <h2>Select Your Profile</h2>
                    <Form>
                        <Form.Check
                            type="radio"
                            label="Local"
                            value="local"
                            name="profile"
                            onChange={(e) => setProfile(e.target.value)}
                            checked={profile === "local"}
                        />
                        <Form.Check
                            type="radio"
                            label="Tourist"
                            value="tourist"
                            name="profile"
                            onChange={(e) => setProfile(e.target.value)}
                            checked={profile === "tourist"}
                        />
                        <Form.Check
                            type="radio"
                            label="Professional"
                            value="professional"
                            name="profile"
                            onChange={(e) => setProfile(e.target.value)}
                            checked={profile === "professional"}
                        />
                    </Form>
                </Col>
                <Col md={6}>
                    <h2>Select Your Country</h2>
                    <Form.Select
                        onChange={(e) => {
                            const selected = countries.find((c) => c.name === e.target.value);
                            setSelectedCountry(selected.name);
                            setCapitalCoordinates(selected.latlng);
                        }}
                    >
                        <option value="">-- Select a Country --</option>
                        {countries.map((country) => (
                            <option key={country.name} value={country.name}>
                                {country.name}
                            </option>
                        ))}
                    </Form.Select>
                </Col>
            </Row>
            <div className="text-center mt-4">
                <Button variant="primary" onClick={handleSubmit}>
                    Continue
                </Button>
            </div>
        </Container>
    );
};

export default LandingPage;
