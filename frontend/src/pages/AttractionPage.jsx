import React, { useEffect, useState } from "react";
import { Container, Card } from "react-bootstrap";
import { useParams } from "react-router-dom";

const AttractionPage = () => {
    const { id } = useParams();
    const [attraction, setAttraction] = useState(null);

    useEffect(() => {
        const fetchAttractionDetails = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/api/attractions/${id}`);
                if (response.ok) {
                    const data = await response.json();
                    setAttraction(data);
                } else {
                    console.error("Failed to fetch attraction details:", await response.text());
                }
            } catch (error) {
                console.error("Error fetching attraction details:", error);
            }
        };

        fetchAttractionDetails();
    }, [id]);

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
                        <li><strong>Price Level:</strong> {attraction.price_level || "N/A"}</li>
                        <li><strong>Rating:</strong> {attraction.rating || "N/A"}</li>
                        <li><strong>Reviews:</strong> {attraction.num_reviews || "N/A"}</li>
                        <li><strong>Address:</strong> {attraction.address?.address_string || "N/A"}</li>
                        <li><strong>Phone:</strong> {attraction.phone || "N/A"}</li>
                        <li><strong>Website:</strong> <a href={attraction.website} target="_blank" rel="noopener noreferrer">{attraction.website}</a></li>
                    </ul>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default AttractionPage;
