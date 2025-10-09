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

  const toggleClass = (classId) =>
    setExpandedClasses((prev) => ({ ...prev, [classId]: !prev[classId] }));

  const toggleStudent = (studentId) =>
    setExpandedStudents((prev) => ({ ...prev, [studentId]: !prev[studentId] }));

  const toggleArtist = (artistId) =>
    setExpandedArtists((prev) => ({ ...prev, [artistId]: !prev[artistId] }));

const handleDelete = async (type, id) => {
  console.log("handleDelete called:", type, id);

  try {
    let endpoint = "";

    if (type === "all") {
      endpoint = `${API_BASE}/delete/all`;
    } else {
      endpoint = `${API_BASE}/delete/${type}/${id}`;
    }

    const response = await axios.delete(endpoint);
    console.log("✅ Server response:", response.data);

    // Refresh the data after delete
    fetchClasses();
  } catch (error) {
    console.error("❌ Delete error:", error);
  }
};




  return (
    <div
      style={{
        color: "white",
        backgroundColor: "#202020",
        minHeight: "100vh",
        width: "100vw",
        padding: "30px",
        fontFamily: "Arial, sans-serif",
        boxSizing: "border-box",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", fontWeight: "bold" }}>🎵 Class Music Dashboard</h1>

      <button
          onClick={() => handleDelete("all")}       
          style={{
          backgroundColor: "#ff4d4d",
          color: "white",
          border: "none",
          padding: "10px 15px",
          borderRadius: "6px",
          cursor: "pointer",
          fontWeight: "bold",
          marginBottom: "25px",
          boxShadow: "0 2px 6px rgba(0,0,0,0.3)",
        }}
      >
        🧨 Delete ALL Data
      </button>

      {classes.map((c) => (
        <div key={c.id} style={{ marginBottom: "20px" }}>
          {/* CLASS HEADER */}
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

          {/* Delete Class */}
          <button
            onClick={() => handleDelete("class", c.id)}
            style={{
              marginLeft: "8px",
              background: "transparent",
              border: "none",
              color: "#666",
              cursor: "pointer",
              fontSize: "1rem",
              transition: "color 0.2s ease",
            }}
            onMouseEnter={(e) => (e.target.style.color = "#ff6666")}
            onMouseLeave={(e) => (e.target.style.color = "#666")}
            title="Delete class"
          >
            🗑
          </button>

          {/* Expanded Class Content */}
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

                  <button
                    onClick={() => handleDelete("student", s.id)}
                    style={{
                      marginLeft: "8px",
                      background: "transparent",
                      border: "none",
                      color: "#666",
                      cursor: "pointer",
                      fontSize: "1rem",
                      transition: "color 0.2s ease",
                    }}
                    onMouseEnter={(e) => (e.target.style.color = "#ff6666")}
                    onMouseLeave={(e) => (e.target.style.color = "#666")}
                    title="Delete student"
                  >
                    🗑
                  </button>

                  {/* Expanded Student Content */}
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

                          <button
                            onClick={() => handleDelete("artist", a.id)}
                            style={{
                              marginLeft: "8px",
                              background: "transparent",
                              border: "none",
                              color: "#666",
                              cursor: "pointer",
                              fontSize: "1rem",
                              transition: "color 0.2s ease",
                            }}
                            onMouseEnter={(e) => (e.target.style.color = "#ff6666")}
                            onMouseLeave={(e) => (e.target.style.color = "#666")}
                            title="Delete artist"
                          >
                            🗑
                          </button>

                          {/* Expanded Artist Content */}
                          {expandedArtists[a.id] && (
                            <ul
                              style={{
                                marginLeft: "25px",
                                listStyleType: "none",
                                color: "#d8aaff",
                              }}
                            >
                              {a.songs.map((song) => (
                                <li key={song.id}>
                                  🎵 {song.title}
                                  <button
                                    onClick={() => handleDelete("song", song.id)}
                                    style={{
                                      marginLeft: "8px",
                                      background: "transparent",
                                      border: "none",
                                      color: "#666",
                                      cursor: "pointer",
                                      fontSize: "1rem",
                                      transition: "color 0.2s ease",
                                    }}
                                    onMouseEnter={(e) => (e.target.style.color = "#ff6666")}
                                    onMouseLeave={(e) => (e.target.style.color = "#666")}
                                    title="Delete song"
                                  >
                                    🗑
                                  </button>
                                </li>
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
