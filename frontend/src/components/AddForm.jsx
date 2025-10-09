import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:5050";

export default function AddForm({ classes, onAddComplete }) {
  const [formType, setFormType] = useState("student");
  const [name, setName] = useState("");
  const [title, setTitle] = useState("");
  const [classId, setClassId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [artistId, setArtistId] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (formType === "class") {
        await axios.post(`${API_BASE}/add_class`, { name });
      } else if (formType === "student") {
        await axios.post(`${API_BASE}/add_student`, { name, class_id: classId });
      } else if (formType === "artist") {
        await axios.post(`${API_BASE}/add_artist`, { name, student_id: studentId });
      } else if (formType === "song") {
        await axios.post(`${API_BASE}/add_song`, { title, artist_id: artistId });
      }

      setName("");
      setTitle("");
      onAddComplete(); 
    } catch (err) {
      console.error("Error adding item:", err);
    }
  };

  return (
    <div
      style={{
        marginTop: "30px",
        background: "#1c1c1c",
        padding: "20px",
        borderRadius: "10px",
        boxShadow: "0 0 10px rgba(255,255,255,0.05)",
      }}
    >
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px", alignItems: "center" }}>
        <select
          value={formType}
          onChange={(e) => setFormType(e.target.value)}
          style={{ background: "#333", color: "white", border: "none", padding: "6px" }}
        >
          <option value="class">Class Period</option>
          <option value="student">Student</option>
          <option value="artist">Artist</option>
          <option value="song">Song</option>
        </select>

        {formType === "class" && (
          <input
            type="text"
            placeholder="Class Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ flex: 1, padding: "6px", background: "#333", color: "white", border: "none" }}
          />
        )}

        {formType === "student" && (
          <>
            <input
              type="text"
              placeholder="Student Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ flex: 1, padding: "6px", background: "#333", color: "white", border: "none" }}
            />
            <select
              value={classId}
              onChange={(e) => setClassId(e.target.value)}
              style={{ background: "#333", color: "white", border: "none", padding: "6px" }}
            >
              <option value="">Select Class</option>
              {classes.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </>
        )}

        {formType === "artist" && (
          <>
            <input
              type="text"
              placeholder="Artist Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ flex: 1, padding: "6px", background: "#333", color: "white", border: "none" }}
            />
            <select
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              style={{ background: "#333", color: "white", border: "none", padding: "6px" }}
            >
              <option value="">Select Student</option>
              {classes.flatMap((c) => c.students).map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </>
        )}

        {formType === "song" && (
          <>
            <input
              type="text"
              placeholder="Song Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              style={{ flex: 1, padding: "6px", background: "#333", color: "white", border: "none" }}
            />
            <select
              value={artistId}
              onChange={(e) => setArtistId(e.target.value)}
              style={{ background: "#333", color: "white", border: "none", padding: "6px" }}
            >
              <option value="">Select Artist</option>
              {classes.flatMap((c) => c.students.flatMap((s) => s.artists)).map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
          </>
        )}

        <button
          type="submit"
          style={{
            background: "#000",
            color: "white",
            padding: "6px 14px",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Add
        </button>
      </form>
    </div>
  );
}
