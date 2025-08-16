import React, { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import TerminalModal from "./Terminal";
import { 
  Activity, 
  Server, 
  Cpu, 
  HardDrive, 
  MemoryStick,
  Network,
  Play,
  Square,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  XCircle,
  Loader2,
  Terminal
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Loading Component
const LoadingScreen = () => {
  const [dots, setDots] = useState('');
  
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-16 h-16 text-blue-400 animate-spin mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Connecting to Nanobox DevStack API{dots}</h2>
        <p className="text-gray-400">Initializing system monitoring...</p>
      </div>
    </div>
  );
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const getStatusConfig = (status) => {
    switch (status) {
      case 'running':
      case 'online':
      case 'healthy':
        return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-400/20' };
      case 'warning':
        return { icon: AlertCircle, color: 'text-yellow-400', bg: 'bg-yellow-400/20' };
      case 'stopped':
      case 'error':
        return { icon: XCircle, color: 'text-red-400', bg: 'bg-red-400/20' };
      default:
        return { icon: AlertCircle, color: 'text-gray-400', bg: 'bg-gray-400/20' };
    }
  };

  const { icon: Icon, color, bg } = getStatusConfig(status);

  return (
    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${color} ${bg}`}>
      <Icon className="w-3 h-3 mr-1" />
      {status}
    </div>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, icon: Icon, unit, status }) => {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <Icon className="w-5 h-5 text-blue-400 mr-2" />
          <h3 className="text-sm font-medium text-gray-300">{title}</h3>
        </div>
        {status && <StatusBadge status={status} />}
      </div>
      <div className="text-2xl font-bold text-white">
        {value !== undefined ? `${value}${unit || ''}` : '--'}
      </div>
    </div>
  );
};

// Container Row Component
const ContainerRow = ({ container, onAction, onTerminal }) => {
  const [loading, setLoading] = useState(false);
  
  const handleAction = async (action) => {
    setLoading(true);
    try {
      await onAction(container.id, action);
    } finally {
      setLoading(false);
    }
  };

  return (
    <tr className="border-b border-gray-700">
      <td className="py-3 px-4">
        <div className="flex items-center">
          <Server className="w-4 h-4 text-blue-400 mr-2" />
          <span className="text-white font-medium">{container.name}</span>
        </div>
      </td>
      <td className="py-3 px-4">
        <StatusBadge status={container.status} />
      </td>
      <td className="py-3 px-4 text-gray-300">{container.image}</td>
      <td className="py-3 px-4 text-gray-300">{container.ports.join(', ')}</td>
      <td className="py-3 px-4">
        <div className="text-sm text-gray-300">
          <div>CPU: {container.cpu_usage}%</div>
          <div>RAM: {container.memory_usage}%</div>
        </div>
      </td>
      <td className="py-3 px-4">
        <div className="flex space-x-2">
          {/* Terminal access button - only for running containers */}
          {container.status === 'running' && (
            <button
              onClick={() => onTerminal(container)}
              className="p-1 rounded text-purple-400 hover:bg-purple-400/20"
              title="Terminal Access"
            >
              <Terminal className="w-4 h-4" />
            </button>
          )}
          
          {/* Container control buttons */}
          {container.status !== 'running' && (
            <button
              onClick={() => handleAction('start')}
              disabled={loading}
              className="p-1 rounded text-green-400 hover:bg-green-400/20 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            </button>
          )}
          {container.status === 'running' && (
            <>
              <button
                onClick={() => handleAction('stop')}
                disabled={loading}
                className="p-1 rounded text-red-400 hover:bg-red-400/20 disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Square className="w-4 h-4" />}
              </button>
              <button
                onClick={() => handleAction('restart')}
                disabled={loading}
                className="p-1 rounded text-blue-400 hover:bg-blue-400/20 disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RotateCcw className="w-4 h-4" />}
              </button>
            </>
          )}
        </div>
      </td>
    </tr>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState(null);
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [containers, setContainers] = useState([]);
  const [error, setError] = useState(null);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [showTerminal, setShowTerminal] = useState(false);

  const fetchData = async () => {
    try {
      setError(null);
      
      const [healthRes, statusRes, metricsRes, containersRes] = await Promise.all([
        axios.get(`${API}/nanobox/health`),
        axios.get(`${API}/nanobox/status`),
        axios.get(`${API}/nanobox/metrics`),
        axios.get(`${API}/nanobox/containers`)
      ]);

      setHealth(healthRes.data);
      setStatus(statusRes.data);
      setMetrics(metricsRes.data);
      setContainers(containersRes.data);
    } catch (err) {
      console.error('API Error:', err);
      setError('Failed to connect to Nanobox DevStack API');
    } finally {
      setLoading(false);
    }
  };

  const handleContainerAction = async (containerId, action) => {
    try {
      console.log(`Performing ${action} on container: ${containerId}`);
      const response = await axios.post(`${API}/nanobox/containers/${containerId}/${action}`);
      console.log(`${action} response:`, response.data);
      
      // Refresh container data
      console.log('Refreshing container data...');
      const containersRes = await axios.get(`${API}/nanobox/containers`);
      setContainers(containersRes.data);
      console.log('Container data refreshed');
    } catch (err) {
      console.error(`Container ${action} error:`, err);
      console.error('Error details:', err.response?.data || err.message);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Connection Failed</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Nanobox DevStack</h1>
              <p className="text-gray-400">System monitoring and container management</p>
            </div>
            <div className="flex items-center space-x-4">
              {health && <StatusBadge status={health.status} />}
              <div className="text-sm text-gray-400">
                Last updated: {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="System Status"
            value={status?.status || 'unknown'}
            icon={Activity}
            status={status?.status}
          />
          <MetricCard
            title="CPU Usage"
            value={status?.cpu_usage}
            icon={Cpu}
            unit="%"
          />
          <MetricCard
            title="Memory Usage"
            value={status?.memory_usage}
            icon={MemoryStick}
            unit="%"
          />
          <MetricCard
            title="Disk Usage"
            value={status?.disk_usage}
            icon={HardDrive}
            unit="%"
          />
        </div>

        {/* Detailed Metrics */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">System Resources</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">CPU Cores</span>
                  <span className="text-white">{metrics.cpu_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Total Memory</span>
                  <span className="text-white">{metrics.memory_total} GB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Available Memory</span>
                  <span className="text-white">{metrics.memory_available} GB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Total Disk</span>
                  <span className="text-white">{metrics.disk_total} GB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Free Disk</span>
                  <span className="text-white">{metrics.disk_free} GB</span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Network Activity</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Data Sent</span>
                  <span className="text-white">{metrics.network_sent} MB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Data Received</span>
                  <span className="text-white">{metrics.network_recv} MB</span>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">System Info</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Uptime</span>
                  <span className="text-white">{status?.uptime || 'unknown'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Service</span>
                  <span className="text-white">{health?.service || 'nanobox-devstack'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Version</span>
                  <span className="text-white">{health?.version || '1.0.0'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Container Management */}
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg">
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Container Management</h3>
            <p className="text-gray-400 text-sm mt-1">Monitor and control your containers</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700 text-left text-gray-400 text-sm">
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Image</th>
                  <th className="py-3 px-4">Ports</th>
                  <th className="py-3 px-4">Usage</th>
                  <th className="py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {containers.map((container) => (
                  <ContainerRow
                    key={container.id}
                    container={container}
                    onAction={handleContainerAction}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;