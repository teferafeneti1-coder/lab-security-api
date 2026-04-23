import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";

function App() {
  const webcamRef = useRef(null);
  const [result, setResult] = useState(null);
  const ws = useRef(null);

  const playAlarm = () => {
    const audio = new Audio("/alarm.mp3");
    audio.play();
  };

  useEffect(() => {
    ws.current = new WebSocket("wss://lab-security-api-1.onrender.com/ws");

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setResult(data);

      if (data.theft_alert || data.abandoned_alert) {
        playAlarm();
      }
    };

    return () => ws.current.close();
  }, []);

  // Send frames continuously
  useEffect(() => {
    const interval = setInterval(() => {
      if (ws.current && ws.current.readyState === 1) {
        const imageSrc = webcamRef.current?.getScreenshot();
        if (imageSrc) {
          ws.current.send(imageSrc);
        }
      }
    }, 500); // ⚡ faster than before

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ textAlign: "center" }}>
      <h1>⚡ Real-Time Lab Security System</h1>

      <div style={{ position: "relative", width: 640, margin: "auto" }}>
        <Webcam ref={webcamRef} screenshotFormat="image/jpeg" width={640} />

        {/* Draw boxes */}
        {result?.boxes?.map((det, index) => {
          const [x1, y1, x2, y2] = det.box;

          return (
            <div
              key={index}
              style={{
                position: "absolute",
                border: "3px solid red",
                left: x1,
                top: y1,
                width: x2 - x1,
                height: y2 - y1,
                color: "red",
                fontWeight: "bold"
              }}
            >
              {det.label}
            </div>
          );
        })}
      </div>

      {/* Alerts */}
      {result?.theft_alert && (
        <h2 style={{ color: "red" }}>🚨 EQUIPMENT REMOVED!</h2>
      )}

      {result?.abandoned_alert && (
        <h2 style={{ color: "orange" }}>🚨 ABANDONED ITEM!</h2>
      )}
    </div>
  );
}

export default App;