import React, { useEffect, useState } from "react";
import { Container, Card, ListGroup } from "react-bootstrap";
import { useParams } from "react-router-dom";

const AttractionPage = () => {
    const { id } = useParams();
    const [attraction, setAttraction] = useState(null);

    useEffect(() => {
        const fetchAttractionDetails = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/api/attractions/${id}/`);
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
                    src={attraction.photos?.[0]?.url || "https://via.placeholder.com/800x400"}
                    alt={attraction.name}
                />
                <Card.Body>
                    <Card.Title>{attraction.name}</Card.Title>
                    <Card.Text>{attraction.description || "No description available."}</Card.Text>

                    <ListGroup variant="flush">
                        <ListGroup.Item>
                            <strong>Category:</strong> {attraction.category || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Subcategory:</strong> {attraction.subcategory || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Price Level:</strong> {attraction.price_level || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Rating:</strong> {attraction.rating || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Number of Reviews:</strong> {attraction.num_reviews || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Address:</strong> {attraction.address?.address_string || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Phone:</strong> {attraction.phone || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Website:</strong>{" "}
                            {attraction.website ? (
                                <a href={attraction.website} target="_blank" rel="noopener noreferrer">
                                    {attraction.website}
                                </a>
                            ) : (
                                "N/A"
                            )}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Opening Hours:</strong>
                            {attraction.hours?.weekday_text?.length > 0 ? (
                                <ul>
                                    {attraction.hours.weekday_text.map((day, index) => (
                                        <li key={index}>{day}</li>
                                    ))}
                                </ul>
                            ) : (
                                "N/A"
                            )}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Cuisine (if restaurant):</strong>
                            {attraction.cuisine?.length > 0 ? (
                                <ul>
                                    {attraction.cuisine.map((item, index) => (
                                        <li key={index}>{item.localized_name}</li>
                                    ))}
                                </ul>
                            ) : (
                                "N/A"
                            )}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Style (if hotel):</strong> {attraction.style || "N/A"}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Groups (Trip Types):</strong>
                            {attraction.trip_types?.length > 0 ? (
                                <ul>
                                    {attraction.trip_types.map((type, index) => (
                                        <li key={index}>
                                            {type.localized_name}: {type.value}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                "N/A"
                            )}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Awards:</strong>
                            {attraction.awards?.length > 0 ? (
                                <ul>
                                    {attraction.awards.map((award, index) => (
                                        <li key={index}>{award.display_name}</li>
                                    ))}
                                </ul>
                            ) : (
                                "No awards available."
                            )}
                        </ListGroup.Item>
                        <ListGroup.Item>
                            <strong>Photos:</strong>
                            {attraction.photos?.length > 0 ? (
                                <div>
                                    {attraction.photos.map((photo, index) => (
                                        <img
                                            key={index}
                                            src={photo.url}
                                            alt={photo.caption || `Photo ${index + 1}`}
                                            style={{ width: "100%", marginBottom: "1rem" }}
                                        />
                                    ))}
                                </div>
                            ) : (
                                "No photos available."
                            )}
                        </ListGroup.Item>
                    </ListGroup>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default AttractionPage;
