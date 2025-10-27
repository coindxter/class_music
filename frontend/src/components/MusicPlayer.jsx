import React, { useEffect, useRef, useState } from "react";

const API_BASE = "http://localhost:5050";

export default function MusicPlayer({ refreshTrigger, currentStudentName }) {
  const [songs, setSongs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef(null);

  // ✅ Only loads existing songs on refresh or after download button pressed
  useEffect(() => {
    const loadSongs = async () => {
      try {
        const res = await fetch(`${API_BASE}/list_songs`);
        const data = await res.json();

        if (res.ok && Array.isArray(data.songs)) {
          const urls = data.songs.map(
            (f) => `${API_BASE}/songs/${encodeURIComponent(f)}`
          );

          const hadSongsBefore = songs.length > 0;
          setSongs(urls);

          // ✅ NEW AUTOMATIC PLAY ONLY WHEN NEW SONGS ARRIVE
          if (!hadSongsBefore && urls.length > 0) {
            setCurrentIndex(0);
            setTimeout(() => {
              if (audioRef.current) {
                audioRef.current.play();
                setIsPlaying(true);
              }
            }, 200);
          }
        }
      } catch (err) {
        console.error("Error loading songs:", err);
      }
    };

    loadSongs();
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
      <div style={{ marginBottom: "10px", fontWeight: "bold" }}>
        {songs.length > 0
          ? decodeURIComponent(songs[currentIndex].split("/downloads/")[1])
          : "No downloaded songs yet"}
      </div>

      {/* Progress bar */}
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

      {/* Controls */}
      <div style={{ display: "flex", justifyContent: "center", gap: "20px" }}>
        <button onClick={prevSong} disabled={songs.length === 0}>
          ⏮️
        </button>
        <button onClick={togglePlay} disabled={songs.length === 0}>
          {isPlaying ? "⏸️" : "▶️"}
        </button>
        <button onClick={nextSong} disabled={songs.length === 0}>
          ⏭️
        </button>
      </div>

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
        preload="auto"
      />
    </div>
  );
}
