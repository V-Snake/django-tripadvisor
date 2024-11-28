import React, { useState } from "react";
import "./Carousel.css"; // Assurez-vous de créer un fichier CSS ou remplacez par du style inline

const Carousel = ({ items }) => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const handlePrev = () => {
        setCurrentIndex((prevIndex) =>
            prevIndex === 0 ? items.length - 1 : prevIndex - 1
        );
    };

    const handleNext = () => {
        setCurrentIndex((prevIndex) =>
            prevIndex === items.length - 1 ? 0 : prevIndex + 1
        );
    };

    if (!items || items.length === 0) {
        return <p>No items available</p>;
    }

    return (
        <div className="carousel">
            <button onClick={handlePrev} className="carousel-btn">
                {"<"}
            </button>
            <div className="carousel-item">
                <h2>{items[currentIndex].name}</h2>
                <p>{items[currentIndex].description}</p>
                <img
                    src={items[currentIndex].image}
                    alt={items[currentIndex].name}
                    className="carousel-image"
                />
            </div>
            <button onClick={handleNext} className="carousel-btn">
                {">"}
            </button>
        </div>
    );
};

export default Carousel;
