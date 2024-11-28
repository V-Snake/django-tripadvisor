import React, { useEffect, useState } from "react";

const AttractionPage = ({ match }) => {
    const [attraction, setAttraction] = useState(null);

    useEffect(() => {
        // Fetch attraction details using the ID
        const fetchAttractionDetails = async () => {
            const response = await fetch(`/api/attractions/${match.params.id}`);
            const data = await response.json();
            setAttraction(data);
        };
        fetchAttractionDetails();
    }, [match.params.id]);

    if (!attraction) return <div>Loading...</div>;

    return (
        <div>
            <h1>{attraction.name}</h1>
            <p>{attraction.description}</p>
            {/* Add other details */}
        </div>
    );
};

export default AttractionPage;
