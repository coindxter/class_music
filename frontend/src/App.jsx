import { useEffect, useState } from "react";
import axios from "axios";
import ClassList from "./components/ClassList";
import StudentList from "./components/StudentList";
import ArtistList from "./components/ArtistList";
import SongList from "./components/SongList";
import AddForm from "./components/AddForm";
import "./style.css";

const API_BASE = "http://localhost:5050";

function App() {
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [artists, setArtists] = useState([]);
  const [selectedArtist, setSelectedArtist] = useState(null);
  const [songs, setSongs] = useState([]);

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    const res = await axios.get(`${API_BASE}/classes`);
    setClasses(res.data);
  };

  const fetchStudents = async (classId) => {
    setSelectedClass(classId);
    const res = await axios.get(`${API_BASE}/students/${classId}`);
    setStudents(res.data);
    setSelectedStudent(null);
    setArtists([]);
    setSongs([]);
  };

  const fetchArtists = async (studentId) => {
    setSelectedStudent(studentId);
    const res = await axios.get(`${API_BASE}/artists/${studentId}`);
    setArtists(res.data);
    setSelectedArtist(null);
    setSongs([]);
  };

  const fetchSongs = async (artistId) => {
    setSelectedArtist(artistId);
    const res = await axios.get(`${API_BASE}/songs/${artistId}`);
    setSongs(res.data);
  };

  return (
    <div className="app">
      <h1>🎶 Class Music Manager</h1>

      <div className="columns">
        <div>
          <h2>Classes</h2>
          <AddForm
            placeholder="New Class"
            onAdd={async (name) => {
              await axios.post(`${API_BASE}/add_class`, { name });
              fetchClasses();
            }}
          />
          <ClassList classes={classes} onSelect={fetchStudents} />
        </div>

        <div>
          <h2>Students</h2>
          {selectedClass && (
            <AddForm
              placeholder="New Student"
              onAdd={async (name) => {
                await axios.post(`${API_BASE}/add_student`, {
                  name,
                  class_id: selectedClass,
                });
                fetchStudents(selectedClass);
              }}
            />
          )}
          <StudentList students={students} onSelect={fetchArtists} />
        </div>

        <div>
          <h2>Artists</h2>
          {selectedStudent && (
            <AddForm
              placeholder="New Artist"
              onAdd={async (name) => {
                await axios.post(`${API_BASE}/add_artist`, {
                  name,
                  student_id: selectedStudent,
                });
                fetchArtists(selectedStudent);
              }}
            />
          )}
          <ArtistList artists={artists} onSelect={fetchSongs} />
        </div>

        <div>
          <h2>Songs</h2>
          {selectedArtist && (
            <AddForm
              placeholder="New Song"
              onAdd={async (title) => {
                await axios.post(`${API_BASE}/add_song`, {
                  title,
                  artist_id: selectedArtist,
                });
                fetchSongs(selectedArtist);
              }}
            />
          )}
          <SongList songs={songs} />
        </div>
      </div>
    </div>
  );
}

export default App;
