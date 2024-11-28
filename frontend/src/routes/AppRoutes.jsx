import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "../pages/LandingPage";
import HomePage from "../pages/HomePage";
import AttractionPage from "../pages/AttractionPage";

const AppRoutes = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/home" element={<HomePage />} />
                <Route path="/attraction/:id" element={<AttractionPage />} />
            </Routes>
        </Router>
    );
};

export default AppRoutes;
