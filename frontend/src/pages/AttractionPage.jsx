import React, { useEffect, useState } from "react";
import { Container, Card, Button } from "react-bootstrap";

const AttractionPage = ({ match }) => {
    const [attraction, setAttraction] = useState(null);

    useEffect(() => {
        const fetchAttractionDetails = async () => {
            const response = await fetch(`/api/attractions/${match.params.id}`);
            const data = await response.json();
            setAttraction(data);
        };
        fetchAttractionDetails();
    }, [match.params.id]);

    if (!attraction) return <div>Loading...</div>;

    return (
        <Container className="mt-4">
            <Card>
                <Card.Img
                    variant="top"
                    src={attraction.photos[0]?.url || "https://via.placeholder.com/800x400"}
                    alt={attraction.name}
                />
                <Card.Body>
                    <Card.Title>{attraction.name}</Card.Title>
                    <Card.Text>{attraction.description || "No description available."}</Card.Text>
                    <ul>
                        <li><strong>Category:</strong> {attraction.category}</li>
                        <li><strong>Rating:</strong> {attraction.rating || "N/A"}</li>
                        <li><strong>Reviews:</strong> {attraction.num_reviews || "N/A"}</li>
                    </ul>
                    <Button
                        href={attraction.web_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        variant="primary"
                    >
                        View on TripAdvisor
                    </Button>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default AttractionPage;
