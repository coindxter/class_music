import React, { useEffect, useRef, useState } from "react";
import "./MusicPlayer.css";

const API_BASE = "http://localhost:5050";

export default function MusicPlayer() {
  const [songs, setSongs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef(null);

  // 🎶 Fetch song list from backend on load
  useEffect(() => {
    const fetchSongs = async () => {
      try {
        const res = await fetch(`${API_BASE}/list_songs`);
        const data = await res.json();
        if (data.songs) {
          const formatted = data.songs.map((filename) => ({
            title: filename.replace(/\.mp3$/i, "").replace(/_/g, " "),
            src: `${API_BASE}/songs/${filename}`,
          }));
          setSongs(formatted);
        }
      } catch (err) {
        console.error("Failed to load songs:", err);
      }
    };
    fetchSongs();
  }, []);

  // ⏯ Progress bar
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      if (audio.duration) {
        setProgress((audio.currentTime / audio.duration) * 100);
      }
    };
    audio.addEventListener("timeupdate", handleTimeUpdate);
    return () => audio.removeEventListener("timeupdate", handleTimeUpdate);
  }, []);

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
    setCurrentIndex((i) => (i + 1) % songs.length);
    setIsPlaying(false);
  };

  const prevSong = () => {
    setCurrentIndex((i) => (i - 1 + songs.length) % songs.length);
    setIsPlaying(false);
  };

  // Auto play when song changes
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || songs.length === 0) return;
    audio.load();
    if (isPlaying) audio.play();
  }, [currentIndex, songs]);

  if (songs.length === 0) {
    return <div className="simple-player">🎧 No songs found</div>;
  }

  const currentSong = songs[currentIndex];

  return (
    <div className="simple-player">
      <div className="simple-player__info">
        <div className="simple-player__title">{currentSong.title}</div>
        <div className="simple-player__progress">
          <div
            className="simple-player__progress-bar"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="simple-player__controls">
        <button onClick={prevSong}>⏮️</button>
        <button onClick={togglePlay}>{isPlaying ? "⏸️" : "▶️"}</button>
        <button onClick={nextSong}>⏭️</button>
      </div>

      <audio ref={audioRef}>
        <source src={currentSong.src} type="audio/mpeg" />
      </audio>
    </div>
  );
}
