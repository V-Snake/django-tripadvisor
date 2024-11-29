import React, { useEffect, useState } from "react";
import { Carousel, Card, Container, Button } from "react-bootstrap";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useNavigate } from "react-router-dom";

// Fix for Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
    iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Helper component to update map view on attraction change
const FlyToHandler = ({ position }) => {
    const map = useMap();

    useEffect(() => {
        if (position) {
            map.flyTo(position, 15, { animate: true });
        }
    }, [position, map]);

    return null;
};

const HomePage = () => {
    const [attractions, setAttractions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedAttraction, setSelectedAttraction] = useState(null);
    const [userAttractions, setUserAttractions] = useState(() => {
        // Charger les attractions depuis localStorage au chargement initial
        console.log("Fetching user attractions from localStorage...");
        const savedAttractions = localStorage.getItem("userAttractions");
        if (savedAttractions) {
            try {
                const parsedAttractions = JSON.parse(savedAttractions);
                console.log("Loaded user attractions from localStorage:", parsedAttractions);
                return parsedAttractions; // Charger les attractions sauvegardées
            } catch (error) {
                console.error("Failed to parse user attractions from localStorage:", error);
            }
        }
        return []; // Retourne une liste vide si rien n'est trouvé
    });

    const navigate = useNavigate();

    // Sauvegarder les attractions dans le localStorage chaque fois que `userAttractions` change
    useEffect(() => {
        if (userAttractions.length > 0) {
            console.log("Saving user attractions to localStorage:", userAttractions);
            localStorage.setItem("userAttractions", JSON.stringify(userAttractions));
        } else {
            console.log("User attractions list is empty. Skipping save.");
        }
    }, [userAttractions]);

    useEffect(() => {
        const fetchAttractions = async () => {
            const coordinates = JSON.parse(localStorage.getItem("coordinates"));
            const profile = localStorage.getItem("profile") || "tourist";

            if (coordinates) {
                try {
                    console.log("Fetching attractions from API with coordinates:", coordinates);
                    const response = await fetch("http://127.0.0.1:8000/api/attractions/nearby/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            latitude: coordinates[0],
                            longitude: coordinates[1],
                            radius: 10000,
                            profile,
                        }),
                    });

                    if (response.ok) {
                        const data = await response.json();
                        console.log("Fetched attractions from API:", data);
                        setAttractions(data);
                        if (data.length > 0) {
                            setSelectedAttraction(data[0]);
                        }
                    } else {
                        console.error("Failed to fetch attractions:", await response.text());
                    }
                } catch (error) {
                    console.error("Error during fetch:", error);
                }
            } else {
                console.warn("No coordinates found in localStorage.");
            }
            setLoading(false);
        };

        fetchAttractions();
    }, []);

    const handleSelectAttraction = (attraction) => {
        console.log("Adding attraction to user's list:", attraction);
        if (!userAttractions.some((item) => item.location_id === attraction.location_id)) {
            const updatedAttractions = [...userAttractions, attraction];
            setUserAttractions(updatedAttractions);
        } else {
            console.warn("Attraction already in user's list:", attraction);
        }
    };

    const handleViewDetails = (attractionId) => {
        console.log("Navigating to attraction details page for ID:", attractionId);
        navigate(`/attraction/${attractionId}`);
    };

    const handleRemoveAttraction = (location_id) => {
        console.log("Removing attraction from user's list, ID:", location_id);
        const updatedAttractions = userAttractions.filter((item) => item.location_id !== location_id);
        setUserAttractions(updatedAttractions);
    };

    if (loading) return <div>Loading...</div>;
    if (attractions.length === 0) return <div>No attractions found.</div>;

    return (
        <Container className="mt-4">
            <h1 className="text-center mb-4">Popular Attractions</h1>
            <Carousel
                onSelect={(selectedIndex) => {
                    const selected = attractions[selectedIndex];
                    if (selected?.latitude && selected?.longitude) {
                        console.log("Carousel selected attraction:", selected);
                        setSelectedAttraction(selected);
                    }
                }}
            >
                {attractions.map((attraction, index) => (
                    <Carousel.Item key={index}>
                        <Card className="text-center">
                            <Card.Img
                                variant="top"
                                src={attraction.photos[0]?.url || "https://via.placeholder.com/800x400"}
                                alt={attraction.name}
                            />
                            <Card.Body>
                                <Card.Title>{attraction.name}</Card.Title>
                                <Card.Text>
                                    {attraction.description || "No description available."}
                                </Card.Text>
                                <Card.Text>
                                    <strong>Rating:</strong> {attraction.rating || "N/A"}
                                </Card.Text>
                                <Button
                                    variant="primary"
                                    onClick={() => handleViewDetails(attraction.location_id)}
                                >
                                    View Details
                                </Button>
                                <Button
                                    variant="success"
                                    className="ms-2"
                                    onClick={() => handleSelectAttraction(attraction)}
                                >
                                    Add to My Attractions
                                </Button>
                            </Card.Body>
                        </Card>
                    </Carousel.Item>
                ))}
            </Carousel>
            <div className="map-container" style={{ height: "400px", width: "100%", margin: "2rem 0" }}>
                <MapContainer
                    center={selectedAttraction ? [selectedAttraction.latitude, selectedAttraction.longitude] : [0, 0]}
                    zoom={15}
                    scrollWheelZoom={false}
                    style={{ height: "100%", width: "100%" }}
                >
                    <FlyToHandler
                        position={selectedAttraction ? [selectedAttraction.latitude, selectedAttraction.longitude] : null}
                    />
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    {selectedAttraction && (
                        <Marker position={[selectedAttraction.latitude, selectedAttraction.longitude]}>
                            <Popup>{selectedAttraction.name}</Popup>
                        </Marker>
                    )}
                </MapContainer>
            </div>
            <h2 className="text-center mt-4">My Selected Attractions</h2>
            {userAttractions.length > 0 ? (
                userAttractions.map((attraction) => (
                    <Card className="mt-2" key={attraction.location_id}>
                        <Card.Body>
                            <Card.Title>{attraction.name}</Card.Title>
                            <Card.Text>
                                {attraction.description || "No description available."}
                            </Card.Text>
                            <Button
                                variant="danger"
                                onClick={() => handleRemoveAttraction(attraction.location_id)}
                            >
                                Remove
                            </Button>
                            <Button
                                variant="secondary"
                                className="ms-2"
                                onClick={() => handleViewDetails(attraction.location_id)}
                            >
                                View Details
                            </Button>
                        </Card.Body>
                    </Card>
                ))
            ) : (
                <p>No attractions added to your list yet.</p>
            )}
        </Container>
    );
};

export default HomePage;
