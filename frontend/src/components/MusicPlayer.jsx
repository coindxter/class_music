import React, { useRef, useState, useEffect } from "react";

export default function MusicPlayer({ currentSong, nextSong, prevSong }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  // ✅ Toggle play/pause
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

  // ✅ Autoplay new song when currentSong changes
  useEffect(() => {
    const audio = audioRef.current;
    if (audio && currentSong?.src) {
      audio.load();       // make sure new song is loaded
      audio.play();       // autoplay
      setIsPlaying(true);
    }
  }, [currentSong]);

  // ✅ Update progress bar and handle song end
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      if (!audio.duration) return;
      const percentage = (audio.currentTime / audio.duration) * 100;
      setProgress(percentage);
    };

    audio.addEventListener("timeupdate", updateProgress);
    audio.addEventListener("ended", nextSong); // Auto play next when song ends

    return () => {
      audio.removeEventListener("timeupdate", updateProgress);
      audio.removeEventListener("ended", nextSong);
    };
  }, [nextSong]);

  // ✅ Seek functionality
  const handleSeek = (e) => {
    const audio = audioRef.current;
    if (!audio || !audio.duration) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const newTime = (clickX / width) * audio.duration;
    audio.currentTime = newTime;
  };

  return (
    <div className="simple-player">
      {/* Song Info */}
      <div className="simple-player__info">
        <div className="simple-player__title">
          {currentSong?.title || "No song selected"}
        </div>

        {/* Progress Bar */}
        <div className="simple-player__progress" onClick={handleSeek}>
          <div
            className="simple-player__progress-bar"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Controls */}
      <div className="simple-player__controls">
        <button onClick={prevSong}>⏮️</button>
        <button onClick={togglePlay}>{isPlaying ? "⏸️" : "▶️"}</button>
        <button onClick={nextSong}>⏭️</button>
      </div>

      {/* Audio Element */}
      <audio ref={audioRef} src={currentSong?.src} type="audio/mpeg" />
    </div>
  );
}




