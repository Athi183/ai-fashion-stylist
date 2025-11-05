import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [statusData, setStatusData] = useState(null);

  const onFileChange = (e) => setFile(e.target.files[0]);

  const onUpload = async () => {
    if (!file) {
      setStatus("Choose a file first");
      return;
    }
    setStatus("Uploading...");
    const fd = new FormData();
    fd.append("image", file);
    try {
      const res = await axios.post("http://127.0.0.1:5000/upload", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus("Uploaded!");
  setStatusData(res.data);
  setImageUrl(`http://127.0.0.1:5000${res.data.image_url}`);
    } catch (err) {
      console.error(err);
      setStatus("Upload failed");
    }
  };

  return (
    <div className="app">
      {/* Header / Hero Section */}
      <header className="hero">
        <h1>👗 AI Fashion Stylist</h1>
        <img src="assets/fashion_hero.jpg" alt="Fashion Hero" className="heroImage"/>
        <p>
          Welcome to <strong>AI Fashion Stylist</strong> — your personal fashion
          companion that analyzes outfit photos and suggests AI-powered style
          insights. Upload your photo below to get started!
        </p>
      </header>

      {/* Upload Box */}
      <div className="upload-box">
        <input type="file" accept="image/*" onChange={onFileChange} />
        <button onClick={onUpload}>Upload</button>
        <p className="status">{status}</p>
      </div>

      {/* Display Uploaded Image */}
      {imageUrl && (
  <div style={{marginTop:"20px"}}>
    <h4>Original:</h4>
    <img src={imageUrl} style={{maxWidth:"250px"}} />

    <h4>Mask:</h4>
    <img src={statusData?.mask_url && `http://127.0.0.1:5000${statusData.mask_url}`} style={{maxWidth:"250px"}} />

    <h4>Extracted Person:</h4>
    <img src={statusData?.person_url && `http://127.0.0.1:5000${statusData.person_url}`} style={{maxWidth:"250px"}} />
  </div>
)}


      {/* Footer */}
      <footer>
        Made with ❤️ by Athi183
      </footer>
    </div>
  );
}

export default App;
