import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [dbStatus, setDbStatus] = useState("Checking...");

  const checkBackendHealth = async () => {
    try {
      const response = await axios.get(`${API}/`);
      setBackendStatus(`✅ ${response.data.message}`);
      console.log("Backend health:", response.data.message);
    } catch (e) {
      setBackendStatus(`❌ Backend connection failed`);
      console.error("Backend health check failed:", e);
    }
  };

  const checkDatabaseHealth = async () => {
    try {
      const response = await axios.get(`${API}/health`);
      setDbStatus(`✅ ${response.data.message}`);
      console.log("Database health:", response.data.message);
    } catch (e) {
      setDbStatus(`❌ Database connection failed`);
      console.error("Database health check failed:", e);
    }
  };

  useEffect(() => {
    checkBackendHealth();
    checkDatabaseHealth();
  }, []);

  return (
    <div>
      <header className="App-header">
        <a
          className="App-link"
          href="https://emergent.sh"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" />
        </a>
        <div className="mt-5 space-y-4">
          <h1 className="text-2xl font-bold text-green-400">🚀 FastAPI Backend Ready for Railway!</h1>
          <div className="bg-gray-800 p-4 rounded-lg text-left max-w-md">
            <p className="text-sm font-semibold text-blue-300">Backend Status:</p>
            <p className="text-sm">{backendStatus}</p>
            <p className="text-sm font-semibold text-blue-300 mt-2">Database Status:</p>
            <p className="text-sm">{dbStatus}</p>
          </div>
          <div className="bg-yellow-900 p-4 rounded-lg text-left max-w-md">
            <p className="text-sm font-semibold text-yellow-300">🎯 Next Step:</p>
            <p className="text-sm">Deploy to Railway.app with root directory: <code>/backend</code></p>
          </div>
        </div>
      </header>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
