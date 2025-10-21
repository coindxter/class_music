import React, { useEffect, useRef, useState } from "react";

const API_BASE = "http://localhost:5050";

export default function MusicPlayer({ refreshTrigger, currentStudentName, studentId = 1 }) {
  const [songs, setSongs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    const startDownload = async () => {
      try {
        console.log("Starting song downloads for student:", studentId);
        const res = await fetch(`${API_BASE}/download_student_songs/${studentId}`);
        const data = await res.json();

        if (data.file) {
          const firstSongUrl = `${API_BASE}${data.file}`;
          console.log("First song ready:", firstSongUrl);
          setSongs([firstSongUrl]);
          setCurrentIndex(0);

          setTimeout(() => {
            if (audioRef.current) {
              audioRef.current.play();
              setIsPlaying(true);
            }
          }, 300);
        } else {
          console.warn("No song ready immediately:", data);
        }

        pollDownloads();
      } catch (err) {
        console.error("Error starting downloads:", err);
      }
    };

    startDownload();
  }, [refreshTrigger, studentId]);

  const pollDownloads = () => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/download_progress/${studentId}`);
        const data = await res.json();
        if (Array.isArray(data)) {
          const urls = data.map((song) => `${API_BASE}${song.path}`);
          if (urls.length !== songs.length) {
            console.log("✅ New song(s) detected:", urls);
            setSongs(urls);
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 5000); 

    return () => clearInterval(interval);
  };

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
          ? decodeURIComponent(songs[currentIndex].split("/downloads/")[1])
          : "Waiting for first song..."}
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
        src={songs[currentIndex] || ""}
        onTimeUpdate={handleTimeUpdate}
        onEnded={nextSong}
        autoPlay={isPlaying}
        preload="auto"
      />
    </div>
  );
}
