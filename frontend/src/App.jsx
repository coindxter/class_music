import React, { useEffect, useState } from "react";
import axios from "axios";
import AddForm from "./components/AddForm";

const API_BASE = "http://localhost:5050";

export default function App() {
  const [classes, setClasses] = useState([]);
  const [expandedClasses, setExpandedClasses] = useState({});
  const [expandedStudents, setExpandedStudents] = useState({});
  const [expandedArtists, setExpandedArtists] = useState({});

  const fetchClasses = async () => {
    try {
      const res = await axios.get(`${API_BASE}/classes_full`);
      setClasses(res.data);
    } catch (err) {
      console.error("Error fetching classes:", err);
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  const toggleClass = (classId) => {
    setExpandedClasses((prev) => ({
      ...prev,
      [classId]: !prev[classId],
    }));
  };

  const toggleStudent = (studentId) => {
    setExpandedStudents((prev) => ({
      ...prev,
      [studentId]: !prev[studentId],
    }));
  };

  const toggleArtist = (artistId) => {
    setExpandedArtists((prev) => ({
      ...prev,
      [artistId]: !prev[artistId],
    }));
  };

  return (
    <div
      style={{
        color: "white",
        backgroundColor: "#202020",
        minHeight: "100vh",
        width: "100vw",
        margin: 0,
        padding: "30px",
        fontFamily: "Arial, sans-serif",
        boxSizing: "border-box",
        overflowX: "hidden",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", fontWeight: "bold" }}>🎵 Class Music Dashboard</h1>

      {classes.map((c) => (
        <div key={c.id} style={{ marginBottom: "20px" }}>
          <button
            onClick={() => toggleClass(c.id)}
            style={{
              background: "none",
              border: "none",
              color: "#91b8ff",
              fontSize: "1.5rem",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            {expandedClasses[c.id] ? "▼" : "▶"} {c.name}
          </button>

          {expandedClasses[c.id] && (
            <ul style={{ marginLeft: "25px", listStyleType: "none" }}>
              {c.students.map((s) => (
                <li key={s.id} style={{ marginBottom: "8px" }}>
                  <button
                    onClick={() => toggleStudent(s.id)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#8fd3ff",
                      cursor: "pointer",
                      fontWeight: "bold",
                      fontSize: "1.1rem",
                    }}
                  >
                    {expandedStudents[s.id] ? "▼" : "▶"} {s.name}
                  </button>

                  {expandedStudents[s.id] && (
                    <ul style={{ marginLeft: "25px", listStyleType: "none" }}>
                      {s.artists.map((a) => (
                        <li key={a.id} style={{ marginBottom: "5px" }}>
                          <button
                            onClick={() => toggleArtist(a.id)}
                            style={{
                              background: "none",
                              border: "none",
                              color: "#ffcc8f",
                              cursor: "pointer",
                              fontWeight: "500",
                            }}
                          >
                            {expandedArtists[a.id] ? "🎤 ▼" : "🎤 ▶"} {a.name}
                          </button>

                          {expandedArtists[a.id] && (
                            <ul
                              style={{
                                marginLeft: "25px",
                                listStyleType: "none",
                                color: "#d8aaff",
                              }}
                            >
                              {a.songs.map((song) => (
                                <li key={song.id}>🎵 {song.title}</li>
                              ))}
                            </ul>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
      <AddForm classes={classes} onAddComplete={fetchClasses} />
    </div>
  );
}
