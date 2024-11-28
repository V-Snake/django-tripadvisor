import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "../pages/LandingPage";
import HomePage from "../pages/HomePage";

const AppRoutes = () => {
    const profile = localStorage.getItem("profile");
    const country = localStorage.getItem("country");

    return (
        <Router>
            <Routes>
                <Route
                    path="/"
                    element={
                        profile && country ? <Navigate to="/home" /> : <LandingPage />
                    }
                />
                <Route path="/home" element={<HomePage />} />
            </Routes>
        </Router>
    );
};

export default AppRoutes;
