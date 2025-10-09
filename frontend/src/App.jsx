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

    fetchClasses();
  } catch (error) {
    console.error("Delete error:", error);
  }
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
    {/* Title */}
    <h1 style={{ fontSize: "2.5rem", fontWeight: "bold", marginBottom: "20px" }}>
      🎵 Class Music Dashboard
    </h1>

    {/* Top control bar */}
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "20px",
        marginBottom: "30px",
        flexWrap: "wrap",
      }}
    >
      {/* Delete ALL Data button */}
      <button
        onClick={() => {handleDelete("all");}}
        style={{
          backgroundColor: "#ff4d4d",
          color: "white",
          border: "none",
          padding: "10px 20px",
          borderRadius: "8px",
          cursor: "pointer",
          fontSize: "1rem",
          fontWeight: "bold",
          transition: "background-color 0.2s ease",
        }}
        onMouseEnter={(e) => (e.target.style.backgroundColor = "#ff1a1a")}
        onMouseLeave={(e) => (e.target.style.backgroundColor = "#ff4d4d")}
      >
        🧨 Delete ALL Data
      </button>

      {/* AddForm stays fixed under title */}
      <AddForm classes={classes} onAddComplete={fetchClasses} />
    </div>

    {/* Class cards grid */}
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
        gap: "20px",
        alignItems: "start",
      }}
    >
      {classes.map((c) => (
        <div
          key={c.id}
          onClick={() => toggleClass(c.id)}
          style={{
            backgroundColor: "#2b2b2b",
            borderRadius: "10px",
            padding: "20px",
            width: "100%",
            boxShadow: "0 4px 10px rgba(0,0,0,0.3)",
            cursor: "pointer",
            transition: "all 0.25s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.05)";
            e.currentTarget.style.boxShadow = "0 0 15px rgba(145,184,255,0.6)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
            e.currentTarget.style.boxShadow = "0 4px 10px rgba(0,0,0,0.3)";
          }}
        >
          {/* Class title + delete */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: "10px",
              fontSize: "1.5rem",
              fontWeight: "bold",
              color: "#91b8ff",
              marginBottom: "10px",
              textAlign: "center",
            }}
          >
            <span>{c.name}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDelete("class", c.id);
              }}
              style={{
                background: "none",
                border: "none",
                color: "#aaa",
                cursor: "pointer",
                fontSize: "1rem",
                filter: "drop-shadow(0 0 2px rgba(255,255,255,0.1))",
                transition: "color 0.2s ease, transform 0.15s ease",
              }}
              onMouseEnter={(e) => {
                e.target.style.color = "#ff6666";
                e.target.style.transform = "scale(1.3)";
              }}
              onMouseLeave={(e) => {
                e.target.style.color = "#aaa";
                e.target.style.transform = "scale(1)";
              }}
              title="Delete Class"
            >
              🗑
            </button>
          </div>

          {/* Expanded students */}
          <div
            style={{
              maxHeight: expandedClasses[c.id] ? "1000px" : "0",
              overflow: "hidden",
              transition: "max-height 0.4s ease",
            }}
          >
            <ul
              style={{
                marginLeft: "5px",
                listStyleType: "none",
                padding: 0,
                marginTop: "10px",
              }}
            >
              {c.students.map((s) => (
                <li key={s.id} style={{ marginBottom: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center" }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleStudent(s.id);
                      }}
                      style={{
                        background: "none",
                        border: "none",
                        color: "#8fd3ff",
                        cursor: "pointer",
                        fontWeight: "bold",
                        fontSize: "1rem",
                        flexGrow: 1,
                        textAlign: "left",
                      }}
                    >
                      {expandedStudents[s.id] ? "▼" : "▶"} {s.name}
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete("student", s.id);
                      }}
                      style={{
                        background: "none",
                        border: "none",
                        color: "#aaa",
                        cursor: "pointer",
                        fontSize: "1rem",
                        filter: "drop-shadow(0 0 2px rgba(255,255,255,0.1))",
                        transition: "color 0.2s ease, transform 0.15s ease",
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.color = "#ff6666";
                        e.target.style.transform = "scale(1.3)";
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.color = "#aaa";
                        e.target.style.transform = "scale(1)";
                      }}
                      title="Delete Student"
                    >
                      🗑
                    </button>
                  </div>

                  {/* Artists */}
                  <div
                    style={{
                      maxHeight: expandedStudents[s.id] ? "800px" : "0",
                      overflow: "hidden",
                      transition: "max-height 0.3s ease",
                    }}
                  >
                    <ul
                      style={{
                        marginLeft: "15px",
                        listStyleType: "none",
                        padding: 0,
                      }}
                    >
                      {s.artists.map((a) => (
                        <li key={a.id} style={{ marginBottom: "5px" }}>
                          <div style={{ display: "flex", alignItems: "center" }}>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleArtist(a.id);
                              }}
                              style={{
                                background: "none",
                                border: "none",
                                color: "#ffcc8f",
                                cursor: "pointer",
                                fontWeight: "500",
                                flexGrow: 1,
                                textAlign: "left",
                              }}
                            >
                              {expandedArtists[a.id] ? "🎤 ▼" : "🎤 ▶"} {a.name}
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete("artist", a.id);
                              }}
                              style={{
                                background: "none",
                                border: "none",
                                color: "#aaa",
                                cursor: "pointer",
                                fontSize: "1rem",
                                filter: "drop-shadow(0 0 2px rgba(255,255,255,0.1))",
                                transition: "color 0.2s ease, transform 0.15s ease",
                              }}
                              onMouseEnter={(e) => {
                                e.target.style.color = "#ff6666";
                                e.target.style.transform = "scale(1.3)";
                              }}
                              onMouseLeave={(e) => {
                                e.target.style.color = "#aaa";
                                e.target.style.transform = "scale(1)";
                              }}
                              title="Delete Artist"
                            >
                              🗑
                            </button>
                          </div>

                          {/* Songs */}
                          <div
                            style={{
                              maxHeight: expandedArtists[a.id] ? "500px" : "0",
                              overflow: "hidden",
                              transition: "max-height 0.3s ease",
                            }}
                          >
                            <ul
                              style={{
                                marginLeft: "15px",
                                listStyleType: "none",
                                color: "#d8aaff",
                              }}
                            >
                              {a.songs.map((song) => (
                                <li
                                  key={song.id}
                                  style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                  }}
                                >
                                  🎵 {song.title}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleDelete("song", song.id);
                                    }}
                                    style={{
                                      background: "none",
                                      border: "none",
                                      color: "#aaa",
                                      cursor: "pointer",
                                      fontSize: "1rem",
                                      filter:
                                        "drop-shadow(0 0 2px rgba(255,255,255,0.1))",
                                      transition:
                                        "color 0.2s ease, transform 0.15s ease",
                                    }}
                                    onMouseEnter={(e) => {
                                      e.target.style.color = "#ff6666";
                                      e.target.style.transform = "scale(1.3)";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.target.style.color = "#aaa";
                                      e.target.style.transform = "scale(1)";
                                    }}
                                    title="Delete Song"
                                  >
                                    🗑
                                  </button>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ))}
    </div>
  </div>
);

}