import React, { useEffect, useState } from "react";
import { Carousel, Card, Container } from "react-bootstrap";

const HomePage = () => {
    const [attractions, setAttractions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAttractions = async () => {
            const coordinates = JSON.parse(localStorage.getItem("coordinates"));
            const profile = localStorage.getItem("profile") || "tourist";

            console.log("Coordinates from localStorage:", coordinates);
            console.log("Profile from localStorage:", profile);

            if (coordinates) {
                try {
                    const requestBody = {
                        latitude: coordinates[0],
                        longitude: coordinates[1],
                        radius: 10000, // Adjust as needed
                        profile,
                    };

                    console.log("Sending data:", requestBody);

                    const response = await fetch("http://127.0.0.1:8000/api/attractions/nearby/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(requestBody),
                    });

                    console.log("API Response status:", response.status);

                    if (response.ok) {
                        const data = await response.json();
                        console.log("API Response data:", data);
                        setAttractions(data);
                    } else {
                        console.error("Failed to fetch attractions:", await response.text());
                    }
                } catch (error) {
                    console.error("Error during fetch:", error);
                }
            } else {
                console.error("No coordinates found in localStorage.");
            }

            setLoading(false);
        };

        fetchAttractions();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (attractions.length === 0) return <div>No attractions found.</div>;

    return (
        <Container className="mt-4">
            <h1 className="text-center mb-4">Popular Attractions</h1>
            <Carousel>
                {attractions.map((attraction) => (
                    <Carousel.Item key={attraction.location_id}>
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
                                <a
                                    href={attraction.web_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="btn btn-primary"
                                >
                                    View on TripAdvisor
                                </a>
                            </Card.Body>
                        </Card>
                    </Carousel.Item>
                ))}
            </Carousel>
        </Container>
    );
};

export default HomePage;
