import React, { useRef, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";

const App = () => {
  const webcamRef = useRef(null);

  // Capture and send every second
  useEffect(() => {
    const interval = setInterval(() => {
      captureAndSendFrame();
    }, 1000); // 1000 ms = 1 second

    return () => clearInterval(interval); // cleanup on unmount
  }, []);

  const captureAndSendFrame = async () => {
    if (!webcamRef.current) return;
    const imageSrc = webcamRef.current.getScreenshot();

    if (imageSrc) {
      try {
        const response = await axios.post("http://localhost:8000/detect/", {
          image: imageSrc,
        });

        console.log("Backend response:", response.data);
        // In next phase, use this to draw on canvas
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
    </div>
  );
};

export default App;
