import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";

const App = () => {
  const videoRef = useRef(null);
  const [bpm, setBpm] = useState(0);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:6789");

    ws.onmessage = (event) => {

      const newBpm = parseFloat(event.data);
      console.log(`Received BPM: ${newBpm}`);
      setBpm(newBpm);
      if (videoRef.current) {
        videoRef.current.playbackRate = newBpm / 135;
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ textAlign: "center", background: "#111", color: "#eee", height: "100vh" }}>
      <h1>🧙‍♂️ Gandalf Beat Sync</h1>
      <p>Live BPM: {bpm}</p>
      <video
        ref={videoRef}
        loop
        autoPlay
        muted
        width="100%"
        src="/gandalf.webm"
        style={{ marginTop: "2rem", borderRadius: "8px" }}
      />
    </div>
  );
};

createRoot(document.getElementById("app")).render(<App />);
