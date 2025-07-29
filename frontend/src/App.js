import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Loader from "./components/loader/loader";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard"; // Optional
import "./App.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);

  return (
    <div className="App">
      <Router>
        {loading && <Loader>Loading...</Loader>}
        <Routes>
          <Route path="/" element={<Login setLoading={setLoading} setProfileData={setProfileData} />} />
          <Route path="/login" element={<Login setLoading={setLoading} setProfileData={setProfileData} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard profile={profileData} />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
