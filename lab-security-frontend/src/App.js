import React, { useRef, useState } from "react";
import Webcam from "react-webcam";

function App() {
  const webcamRef = useRef(null);
  const [result, setResult] = useState(null);

 const captureAndSend = async () => {
  console.log("Button clicked");

  const imageSrc = webcamRef.current.getScreenshot();
  console.log("Image captured:", imageSrc);

  const blob = await fetch(imageSrc).then(res => res.blob());

  const formData = new FormData();
  formData.append("file", blob, "image.jpg");

  try {
    const response = await fetch("https://lab-security-api-1.onrender.com/detect", {
      method: "POST",
      body: formData,
    });

    console.log("Response status:", response.status);

    const data = await response.json();
    console.log("Response data:", data);

    setResult(data);
  } catch (error) {
    console.error("Error:", error);
  }
};

  return (
    <div style={{ textAlign: "center" }}>
      <h1>Lab Security System</h1>

      <Webcam
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={400}
      />

      <br /><br />

      <button onClick={captureAndSend}>
        Detect
      </button>

      {result && (
        <div>
          <h2>Result:</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;