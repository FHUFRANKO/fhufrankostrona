import { useEffect } from 'react';

export const AdminLoginRedirect = () => {
  useEffect(() => {
    // Redirect to backend admin login page
    const adminPath = process.env.REACT_APP_ADMIN_PATH || 'moj-tajny-panel-82374';
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    const loginUrl = `${backendUrl}/admin-${adminPath}`;
    
    // Full page redirect to backend
    window.location.replace(loginUrl);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
      <div className="text-center text-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p>Przekierowywanie do panelu administracyjnego...</p>
      </div>
    </div>
  );
};
