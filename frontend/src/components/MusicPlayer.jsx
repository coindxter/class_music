import React, { useState } from "react";
import "./MusicPlayer.css"; // use this if you saved your CSS/SCSS file separately

export default function MusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  return (
    <div className="player">
      <div id="info" className={`info ${isPlaying ? "active" : ""}`}>
        <span className="artist">Flume</span>
        <span className="name">Say it</span>
        <div className="progress-bar">
          <div className="bar"></div>
        </div>
      </div>

      <div
        id="control-panel"
        className={`control-panel ${isPlaying ? "active" : ""}`}
      >
        <div className="album-art"></div>

        <div className="controls">
          <div className="prev"></div>
          <div id="play" className="play" onClick={togglePlay}></div>
          <div className="next"></div>
        </div>
      </div>
    </div>
  );
}
