import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const ProtectedRoute = ({ children }) => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const backendUrl = (process.env.REACT_APP_BACKEND_URL || window.location.origin).replace(/\/api\/?$/, '');
    
    try {
      const response = await fetch(`${backendUrl}/api/admin/check-auth`, {
        method: 'GET',
        credentials: 'include'
      });

      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
        // Redirect to login page
        const adminPath = process.env.REACT_APP_ADMIN_PATH || 'moj-tajny-panel-82374';
        navigate(`/admin-${adminPath}`);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      setIsAuthenticated(false);
      const adminPath = process.env.REACT_APP_ADMIN_PATH || 'moj-tajny-panel-82374';
      navigate(`/admin-${adminPath}`);
    } finally {
      setIsChecking(false);
    }
  };

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Sprawdzanie autoryzacji...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Navigation already handled
  }

  return children;
};
