import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./components/HomePage";
import AdminLogin from "./components/AdminLogin";
import AdminDashboard from "./components/AdminDashboard";
import { Toaster } from "./components/ui/sonner";

function App() {
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [adminToken, setAdminToken] = useState(null);

  const handleAdminLogin = (token) => {
    setIsAdminAuthenticated(true);
    setAdminToken(token);
  };

  const handleAdminLogout = () => {
    setIsAdminAuthenticated(false);
    setAdminToken(null);
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route 
            path="/admin" 
            element={
              isAdminAuthenticated ? (
                <AdminDashboard onLogout={handleAdminLogout} />
              ) : (
                <Navigate to="/admin/login" replace />
              )
            } 
          />
          <Route 
            path="/admin/login" 
            element={
              isAdminAuthenticated ? (
                <Navigate to="/admin" replace />
              ) : (
                <AdminLogin onLogin={handleAdminLogin} />
              )
            } 
          />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;