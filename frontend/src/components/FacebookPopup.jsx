import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export const FacebookPopup = () => {
  const [isVisible, setIsVisible] = useState(false);
  const STORAGE_KEY = 'facebookPopupClosed';
  const DAYS_TO_HIDE = 7; // Dni przez które popup nie będzie się pokazywał po zamknięciu

  useEffect(() => {
    // Sprawdź czy popup został zamknięty
    const closedTimestamp = localStorage.getItem(STORAGE_KEY);
    
    if (closedTimestamp) {
      const daysSinceClosed = (Date.now() - parseInt(closedTimestamp)) / (1000 * 60 * 60 * 24);
      if (daysSinceClosed < DAYS_TO_HIDE) {
        return; // Nie pokazuj jeszcze
      }
    }

    // Pokaż popup po 3 sekundach
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    localStorage.setItem(STORAGE_KEY, Date.now().toString());
  };

  const handleFacebookClick = () => {
    window.open('https://www.facebook.com/profile.php?id=61578689111557', '_blank', 'noopener,noreferrer');
    handleClose();
  };

  if (!isVisible) return null;

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-50 transition-opacity"
        onClick={handleClose}
      />
      
      {/* Popup */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 animate-fadeIn">
        <div className="bg-white rounded-lg shadow-2xl p-6 max-w-md w-full mx-4 relative">
          {/* Close button */}
          <button
            onClick={handleClose}
            className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Zamknij"
          >
            <X className="h-6 w-6" />
          </button>

          {/* Content */}
          <div className="text-center">
            {/* Facebook Logo */}
            <div className="mb-4 flex justify-center">
              <svg 
                className="w-20 h-20 cursor-pointer hover:scale-110 transition-transform"
                onClick={handleFacebookClick}
                viewBox="0 0 48 48" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="24" cy="24" r="24" fill="#1877F2"/>
                <path 
                  d="M26.5016 25.5L27.1059 21.8156H23.5764V19.4969C23.5764 18.4812 24.0763 17.4906 25.7247 17.4906H27.2506V14.4094C27.2506 14.4094 25.7247 14.1562 24.2684 14.1562C21.2339 14.1562 19.2588 15.9937 19.2588 19.0781V21.8156H16V25.5H19.2588V34.8438C19.9201 34.9469 20.5982 35 21.2882 35C21.9782 35 22.6563 34.9469 23.3176 34.8438V25.5H26.5016Z" 
                  fill="white"
                />
              </svg>
            </div>

            {/* Text */}
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Zaobserwuj nas na Facebooku!
            </h2>
            <p className="text-gray-600 mb-6">
              Bądź na bieżąco z naszymi najnowszymi ogłoszeniami i promocjami
            </p>

            {/* Button */}
            <button
              onClick={handleFacebookClick}
              className="w-full bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Obserwuj nas
            </button>

            {/* Skip text */}
            <button
              onClick={handleClose}
              className="mt-4 text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              Może później
            </button>
          </div>
        </div>
      </div>

      {/* Animation styles */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translate(-50%, -45%);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -50%);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </>
  );
};
