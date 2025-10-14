import React, { useEffect, useRef, useState } from "react";

const API_BASE = "http://localhost:5050";

export default function MusicPlayer({ refreshTrigger, currentStudentName }) {  
  const [songs, setSongs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef(null);

useEffect(() => {
  const fetchSongs = async () => {
    try {
      const res = await fetch(`${API_BASE}/list_songs`);
      const data = await res.json();
      if (res.ok) {
        const urls = data.songs.map(
          (filename) => `${API_BASE}/songs/${encodeURIComponent(filename)}`
        );
        setSongs(urls);
        if (urls.length > 0) {
          setCurrentIndex(0);
          setTimeout(() => {
            if (audioRef.current) {
              audioRef.current.play();
              setIsPlaying(true);
            }
          }, 300);
        } else {
          setIsPlaying(false);
        }
      }
    } catch (err) {
      console.error("Error fetching songs:", err);
    }
  };

  fetchSongs();
}, [refreshTrigger]); 

  const handleTimeUpdate = () => {
    const audio = audioRef.current;
    if (audio && audio.duration > 0) {
      setProgress((audio.currentTime / audio.duration) * 100);
    }
  };

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const nextSong = () => {
    if (songs.length === 0) return;
    const nextIndex = (currentIndex + 1) % songs.length;
    setCurrentIndex(nextIndex);
    setProgress(0);
    setTimeout(() => {
      audioRef.current.play();
      setIsPlaying(true);
    }, 100);
  };

  const prevSong = () => {
    if (songs.length === 0) return;
    const prevIndex = (currentIndex - 1 + songs.length) % songs.length;
    setCurrentIndex(prevIndex);
    setProgress(0);
    setTimeout(() => {
      audioRef.current.play();
      setIsPlaying(true);
    }, 100);
  };

return (
  <div
    style={{
      backgroundColor: "#2b2b2b",
      padding: "20px",
      borderRadius: "15px",
      textAlign: "center",
      width: "350px",
      boxShadow: "0 4px 10px rgba(0,0,0,0.4)",
    }}
  >
    {/* 🎶 Song filename display */}
    <div style={{ marginBottom: "10px", fontWeight: "bold" }}>
      {songs.length > 0
        ? decodeURIComponent(songs[currentIndex].split("/songs/")[1])
        : "No songs available"}
    </div>

    {/* 🔵 Progress bar */}
    <div
      style={{
        width: "100%",
        height: "6px",
        backgroundColor: "#444",
        borderRadius: "3px",
        marginBottom: "10px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          backgroundColor: "#91b8ff",
          transition: "width 0.2s linear",
        }}
      />
    </div>

    {/* ⏯️ Controls */}
    <div style={{ display: "flex", justifyContent: "center", gap: "20px" }}>
      <button onClick={prevSong}>⏮️</button>
      <button onClick={togglePlay}>{isPlaying ? "⏸️" : "▶️"}</button>
      <button onClick={nextSong}>⏭️</button>
    </div>

    {/* Now Playing */}
    {currentStudentName && (
      <div
        style={{
          textAlign: "center",
          fontWeight: "bold",
          color: "#91b8ff",
          marginTop: "10px",
        }}
      >
        Now Playing: {currentStudentName}'s Playlist
      </div>
    )}

    <audio
      ref={audioRef}
      src={songs[currentIndex]}
      onTimeUpdate={handleTimeUpdate}
      onEnded={nextSong}
      autoPlay
    />
  </div>
);
}