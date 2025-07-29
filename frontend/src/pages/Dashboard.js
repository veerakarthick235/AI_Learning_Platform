import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Dashboard = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");

  // Fetch user profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://localhost:5000/profile", {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUsername(response.data.username);
      } catch (error) {
        console.error("Error fetching profile:", error);
        navigate("/login");
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>👋 Welcome, {username || "Learner"}!</h1>

      <div style={styles.cardGrid}>
        <DashboardCard title="📘 Topics" onClick={() => navigate("/topic")} />
        <DashboardCard title="🧭 Roadmap" onClick={() => navigate("/roadmap")} />
        <DashboardCard title="📝 Quiz" onClick={() => navigate("/quiz")} />
        <DashboardCard title="👤 Profile" onClick={() => navigate("/profile")} />
      </div>

      <button style={styles.logoutBtn} onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
};

// Reusable Card Component
const DashboardCard = ({ title, onClick }) => (
  <div style={styles.card} onClick={onClick}>
    <h3>{title}</h3>
  </div>
);

// Inline CSS Styles
const styles = {
  container: {
    textAlign: "center",
    padding: "2rem",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#f9f9f9",
    minHeight: "100vh",
  },
  heading: {
    fontSize: "2rem",
    marginBottom: "2rem",
    color: "#333",
  },
  cardGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "1.5rem",
    padding: "0 2rem",
    maxWidth: "800px",
    margin: "0 auto",
  },
  card: {
    backgroundColor: "#fff",
    border: "1px solid #ccc",
    borderRadius: "12px",
    padding: "1rem",
    cursor: "pointer",
    boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
    transition: "transform 0.2s ease",
  },
  logoutBtn: {
    marginTop: "2rem",
    padding: "0.75rem 2rem",
    fontSize: "1rem",
    borderRadius: "8px",
    border: "none",
    backgroundColor: "#e74c3c",
    color: "white",
    cursor: "pointer",
  },
};

export default Dashboard;
