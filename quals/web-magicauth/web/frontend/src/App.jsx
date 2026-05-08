import React, { useState, useEffect, useRef } from 'react';
import { QRCodeSVG } from 'qrcode.react';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [status, setStatus] = useState('');
  const [mailtoLink, setMailtoLink] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [flag, setFlag] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const wsRef = useRef(null);

  useEffect(() => {
    // Check if token exists in localStorage
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
      setToken(savedToken);
      fetchUserInfo(savedToken);
    }
  }, []);

  const fetchUserInfo = async (authToken) => {
    try {
      const response = await fetch('/api/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);

        // If admin, try to fetch flag
        if (userData.is_admin) {
          fetchFlag(authToken);
        }
      } else {
        // Token is invalid
        localStorage.removeItem('authToken');
        setToken(null);
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('authToken');
      setToken(null);
    }
  };

  const fetchFlag = async (authToken) => {
    try {
      const response = await fetch('/api/flag', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFlag(data.flag);
      }
    } catch (error) {
      console.error('Failed to fetch flag:', error);
    }
  };

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/auth`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setError('');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received:', data);

      if (data.status === 'pending') {
        setStatus(data.message);
        setMailtoLink(data.mailto_link);
        setAuthEmail(data.auth_email);
        setSubject(data.subject);
        setLoading(false);
      } else if (data.status === 'success') {
        setStatus(data.message);
        setToken(data.token);
        setUser({
          sub: data.email,
          email: data.email,
          role: data.role,
          is_admin: data.is_admin
        });
        setIsAuthenticated(true);
        localStorage.setItem('authToken', data.token);
        setLoading(false);

        // Fetch flag if admin
        if (data.is_admin) {
          fetchFlag(data.token);
        }

        // Close WebSocket
        ws.close();
      } else if (data.status === 'error') {
        setError(data.message);
        setStatus('');
        setMailtoLink('');
        setLoading(false);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection failed');
      setLoading(false);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    wsRef.current = ws;
  };

  const handleAuth = (authMode) => {
    setError('');
    setStatus('Connecting...');
    setLoading(true);

    // Connect WebSocket
    connectWebSocket();

    // Wait for connection to open
    setTimeout(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          action: authMode
        }));
      }
    }, 500);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    setUser(null);
    setToken(null);
    setFlag(null);
    setStatus('');
    setMailtoLink('');
    setAuthEmail('');
    setSubject('');
    setError('');
    setLoading(false);
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-center mb-6 text-blue-600">
            MagicAuth™
          </h1>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Welcome!</h2>
            <p className="text-gray-600">Email: {user.email}</p>
            <p className="text-gray-600">
              Role: {user.is_admin ? (
                <span className="text-green-600 font-semibold">Admin</span>
              ) : (
                <span>User</span>
              )}
            </p>
          </div>

          {user.is_admin && flag && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded">
              <h3 className="font-semibold text-green-800 mb-2">Flag:</h3>
              <code className="text-sm text-green-900 break-all">{flag}</code>
            </div>
          )}

          {user.is_admin && !flag && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-yellow-800">Loading flag...</p>
            </div>
          )}

          <button
            onClick={handleLogout}
            className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition"
          >
            Logout
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-6 text-blue-600">
          MagicAuth™
        </h1>

        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
          <p className="text-sm text-blue-800">
            No passwords or validation codes needed! Authenticate via email with our revolutionary MagicAuth™ system.
          </p>
        </div>

        {!mailtoLink && !loading && (
          <>
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded mb-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div className="flex space-x-4">
              <button
                onClick={() => handleAuth('login')}
                className="flex-1 bg-blue-500 text-white py-3 px-4 rounded hover:bg-blue-600 transition font-semibold text-lg"
              >
                Login
              </button>
              <button
                onClick={() => handleAuth('register')}
                className="flex-1 bg-green-500 text-white py-3 px-4 rounded hover:bg-green-600 transition font-semibold text-lg"
              >
                Register
              </button>
            </div>
          </>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600">{status || 'Connecting...'}</p>
          </div>
        )}

        {mailtoLink && !loading && (
          <div className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              {/* Left column: Automatic */}
              <div className="p-4 bg-green-50 border border-green-200 rounded">
                <h3 className="font-semibold text-green-800 mb-3 text-center">
                  Automatic
                </h3>
                <a
                  href={mailtoLink}
                  className="block w-full text-center bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 transition font-semibold mb-4"
                >
                  Compose Email
                </a>
                <div className="flex justify-center">
                  <div className="bg-white p-3 rounded border-2 border-green-300">
                    <QRCodeSVG value={mailtoLink} size={150} />
                  </div>
                </div>
                <p className="text-xs text-green-700 text-center mt-2">
                  Scan with your phone
                </p>
              </div>

              {/* Right column: Manual */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                <h3 className="font-semibold text-blue-800 mb-3 text-center">
                  Manual
                </h3>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs font-semibold text-blue-900 mb-1">
                      To:
                    </label>
                    <div className="flex items-center space-x-1">
                      <input
                        type="text"
                        value={authEmail}
                        readOnly
                        className="flex-1 px-2 py-1.5 bg-white border border-blue-300 rounded font-mono text-xs"
                        onClick={(e) => e.target.select()}
                      />
                      <button
                        onClick={() => copyToClipboard(authEmail)}
                        className="px-2 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-xs"
                      >
                        Copy
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-blue-900 mb-1">
                      Subject:
                    </label>
                    <div className="flex items-center space-x-1">
                      <input
                        type="text"
                        value={subject}
                        readOnly
                        className="flex-1 px-2 py-1.5 bg-white border border-blue-300 rounded font-mono text-xs"
                        onClick={(e) => e.target.select()}
                      />
                      <button
                        onClick={() => copyToClipboard(subject)}
                        className="px-2 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-xs"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-blue-600 mt-3">
                  Email body can be empty
                </p>
              </div>
            </div>

            {/* Waiting spinner below both columns */}
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
                <p className="text-sm text-yellow-800">
                  Waiting for email verification...
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
