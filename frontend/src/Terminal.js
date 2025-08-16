import React, { useState, useEffect, useRef } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import '@xterm/xterm/css/xterm.css';
import { X, User, Lock, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TerminalModal = ({ container, onClose }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authError, setAuthError] = useState('');
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [sessionId, setSessionId] = useState(null);
  const [availableUsers, setAvailableUsers] = useState([]);
  
  const terminalRef = useRef(null);
  const xtermRef = useRef(null);
  const wsRef = useRef(null);
  const fitAddonRef = useRef(null);

  useEffect(() => {
    // Load available users
    loadAvailableUsers();
    
    return () => {
      // Cleanup
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (xtermRef.current) {
        xtermRef.current.dispose();
      }
    };
  }, []);

  const loadAvailableUsers = async () => {
    try {
      const response = await axios.get(`${API}/nanobox/containers/${container.id}/terminal/users`);
      setAvailableUsers(response.data.available_users || []);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const handleAuthentication = async (e) => {
    e.preventDefault();
    setIsAuthenticating(true);
    setAuthError('');

    try {
      const response = await axios.post(`${API}/nanobox/containers/${container.id}/terminal/auth`, {
        username: credentials.username,
        password: credentials.password,
        container_id: container.id
      });

      setSessionId(response.data.session_id);
      setIsAuthenticated(true);
      
      // Initialize terminal after successful auth
      setTimeout(initializeTerminal, 100);
      
    } catch (error) {
      setAuthError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const initializeTerminal = () => {
    if (!terminalRef.current) return;

    // Create terminal instance
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1a1a1a',
        foreground: '#ffffff',
        cursor: '#ffffff',
        selection: '#3A3A3A'
      },
      rows: 24,
      cols: 80
    });

    // Add addons
    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);
    
    // Open terminal
    terminal.open(terminalRef.current);
    fitAddon.fit();
    
    // Store references
    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;
    
    // Connect WebSocket
    connectWebSocket(terminal);
    
    // Handle terminal input
    terminal.onData((data) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'input',
          data: data
        }));
      }
    });

    // Handle window resize
    const handleResize = () => fitAddon.fit();
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  };

  const connectWebSocket = (terminal) => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${BACKEND_URL.replace(/^https?:\/\//, '')}/api/nanobox/containers/${container.id}/terminal/${sessionId}`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    
    ws.onopen = () => {
      terminal.writeln('Terminal connected...');
    };
    
    ws.onmessage = (event) => {
      terminal.write(event.data);
    };
    
    ws.onclose = () => {
      terminal.writeln('\r\n\r\nConnection closed.');
    };
    
    ws.onerror = (error) => {
      terminal.writeln(`\r\nConnection error: ${error.message || 'Unknown error'}`);
    };
  };

  const getTestCredentials = (username) => {
    const testPasswords = {
      'testuser': 'testpass123',
      'admin': 'admin123',
      'developer': 'dev123',
      'nanobox': 'nanobox123'
    };
    return testPasswords[username] || '';
  };

  const fillCredentials = (username) => {
    setCredentials({
      username: username,
      password: getTestCredentials(username)
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-6 w-96 max-w-full mx-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              Terminal Access - {container.name}
            </h3>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <form onSubmit={handleAuthentication} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={credentials.username}
                  onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                  className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                  placeholder="Enter username"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:border-blue-500"
                  placeholder="Enter password"
                  required
                />
              </div>
            </div>

            {authError && (
              <div className="text-red-400 text-sm bg-red-400/10 p-2 rounded">
                {authError}
              </div>
            )}

            <button
              type="submit"
              disabled={isAuthenticating}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
            >
              {isAuthenticating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Authenticating...
                </>
              ) : (
                'Connect Terminal'
              )}
            </button>
          </form>

          {availableUsers.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Test Users:</h4>
              <div className="grid grid-cols-2 gap-2">
                {availableUsers.map((user) => (
                  <button
                    key={user.username}
                    onClick={() => fillCredentials(user.username)}
                    className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded text-left"
                    title={user.description}
                  >
                    {user.username}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Click on a username to auto-fill credentials
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg w-full max-w-4xl mx-4 h-3/4 flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <h3 className="text-lg font-semibold text-white">
              Terminal - {container.name}
            </h3>
            <span className="text-sm text-gray-400">
              User: {credentials.username}
            </span>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex-1 p-4">
          <div 
            ref={terminalRef} 
            className="w-full h-full rounded border border-gray-700"
            style={{ backgroundColor: '#1a1a1a' }}
          />
        </div>
      </div>
    </div>
  );
};

export default TerminalModal;