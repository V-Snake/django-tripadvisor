import React, { useEffect, useState } from "react";
import { Carousel, Card, Container, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
    const [attractions, setAttractions] = useState([]);
    const [compiledAttractions, setCompiledAttractions] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    // Charger les attractions compilées depuis le localStorage
    useEffect(() => {
        const savedAttractions = JSON.parse(localStorage.getItem("compiledAttractions")) || [];
        setCompiledAttractions(savedAttractions);
    }, []);

    // Sauvegarder les attractions compilées dans le localStorage
    useEffect(() => {
        localStorage.setItem("compiledAttractions", JSON.stringify(compiledAttractions));
    }, [compiledAttractions]);

    const fetchAttractions = async () => {
        const coordinates = JSON.parse(localStorage.getItem("coordinates"));
        const profile = localStorage.getItem("profile") || "tourist";

        try {
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
                setAttractions(data);
            } else {
                console.error("Failed to fetch attractions:", await response.text());
            }
        } catch (error) {
            console.error("Error fetching attractions:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAttractions();
    }, []);

    const addToCompiled = (attraction) => {
        setCompiledAttractions((prev) => {
            // Éviter les doublons
            if (!prev.some((attr) => attr.location_id === attraction.location_id)) {
                return [...prev, attraction];
            }
            return prev;
        });
    };

    const removeFromCompiled = (id) => {
        setCompiledAttractions((prev) => prev.filter((attr) => attr.location_id !== id));
    };

    const handleLogout = () => {
        localStorage.clear(); // Vide le localStorage
        navigate("/"); // Retourne à la landing page
    };

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
                                <Button onClick={() => addToCompiled(attraction)}>
                                    Add to List
                                </Button>
                                <Button
                                    variant="secondary"
                                    onClick={() => navigate(`/attraction/${attraction.location_id}`)}
                                    className="ms-2"
                                >
                                    View Details
                                </Button>
                            </Card.Body>
                        </Card>
                    </Carousel.Item>
                ))}
            </Carousel>

            <h2 className="mt-4">Compiled Attractions</h2>
            <div>
                {compiledAttractions.map((attraction) => (
                    <Card key={attraction.location_id} className="mb-3">
                        <Card.Body>
                            <Card.Title>{attraction.name}</Card.Title>
                            <Button
                                variant="danger"
                                onClick={() => removeFromCompiled(attraction.location_id)}
                            >
                                Remove
                            </Button>
                            <Button
                                variant="secondary"
                                onClick={() => navigate(`/attraction/${attraction.location_id}`)}
                                className="ms-2"
                            >
                                View Details
                            </Button>
                        </Card.Body>
                    </Card>
                ))}
            </div>

            <Button variant="danger" className="mt-4" onClick={handleLogout}>
                Logout
            </Button>
        </Container>
    );
};

export default HomePage;
