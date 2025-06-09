import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const App = () => {
  const webcamRef = useRef(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    const interval = setInterval(() => {
      captureAndSendFrame();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const captureAndSendFrame = async () => {
    if (!webcamRef.current) return;
    const imageSrc = webcamRef.current.getScreenshot();

    if (imageSrc) {
      try {
        const response = await axios.post("https://deep-detect-app.onrender.com", {
          image: imageSrc,
        });

        setResult(response.data); // store result in state
      } catch (error) {
        console.error("Error sending image to backend:", error);
      }
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "20px" }}>
      <h1>Deep Sea Mission NIOT</h1>

      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={400}
        videoConstraints={{
          width: 400,
          height: 300,
          facingMode: "user",
        }}
      />

      <div style={{ marginTop: "20px", color: "lime" }}>
        {result ? (
          <pre>{JSON.stringify(result, null, 2)}</pre>
        ) : (
          "Waiting for response..."
        )}
      </div>
    </div>
  );
};

export default App;
