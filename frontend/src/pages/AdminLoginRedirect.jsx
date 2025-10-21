import { useState } from 'react';

export const AdminLoginRedirect = () => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const adminPath = process.env.REACT_APP_ADMIN_PATH || 'moj-tajny-panel-82374';
    const backendUrl = (process.env.REACT_APP_BACKEND_URL || window.location.origin).replace(/\/api\/?$/, '');
    
    try {
      const response = await fetch(`${backendUrl}/api/admin-${adminPath}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
        credentials: 'include'
      });

      if (response.ok) {
        // Success - redirect to admin panel
        window.location.href = '/admin';
      } else {
        setError('Błędne hasło');
      }
    } catch (err) {
      setError('Błąd połączenia z serwerem');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 max-w-md w-full shadow-2xl">
        <h2 className="text-2xl font-bold text-blue-400 mb-6 flex items-center gap-3">
          🔒 Panel Administratora
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Wprowadź hasło dostępu"
              required
              autoFocus
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm">
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white font-semibold rounded-lg transition transform active:scale-95 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Logowanie...
              </span>
            ) : (
              'Zaloguj się'
            )}
          </button>
        </form>

        <p className="text-gray-500 text-xs text-center mt-6">
          ⚠️ Tylko dla upoważnionych użytkowników
        </p>
      </div>
    </div>
  );
};
