import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export const FacebookPopup = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const STORAGE_KEY = 'facebookPopupClosed';
  const DAYS_TO_HIDE = 7;

  useEffect(() => {
    // Sprawdź czy popup został zamknięty
    const closedTimestamp = localStorage.getItem(STORAGE_KEY);
    
    if (closedTimestamp) {
      const daysSinceClosed = (Date.now() - parseInt(closedTimestamp)) / (1000 * 60 * 60 * 24);
      if (daysSinceClosed < DAYS_TO_HIDE) {
        return;
      }
    }

    // Pokaż popup po 3 sekundach
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsVisible(false);
      localStorage.setItem(STORAGE_KEY, Date.now().toString());
    }, 300);
  };

  const handleFacebookClick = () => {
    window.open('https://www.facebook.com/profile.php?id=61578689111557', '_blank', 'noopener,noreferrer');
  };

  if (!isVisible) return null;

  return (
    <div 
      className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${
        isClosing ? 'opacity-0 translate-y-4' : 'opacity-100 translate-y-0'
      }`}
      style={{
        animation: isClosing ? 'none' : 'slideInUp 0.4s ease-out'
      }}
    >
      <div className="bg-white rounded-lg shadow-2xl p-4 max-w-xs relative border border-gray-200">
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Zamknij"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Content */}
        <div 
          onClick={handleFacebookClick}
          className="cursor-pointer flex items-center gap-3 pr-4"
        >
          {/* Facebook Logo - Square with centered 'f' */}
          <div className="flex-shrink-0">
            <svg 
              className="w-14 h-14 hover:scale-105 transition-transform"
              viewBox="0 0 48 48" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect x="0" y="0" width="48" height="48" rx="8" fill="#1877F2"/>
              <path 
                d="M30 24.5L30.8 19.5H26V16.2C26 14.7 26.7 13.3 29 13.3H31V9C31 9 29 8.7 27.1 8.7C23 8.7 20.3 11.2 20.3 15.5V19.5H16V24.5H20.3V38.5C21.2 38.6 22.1 38.7 23 38.7C23.9 38.7 24.8 38.6 25.7 38.5V24.5H30Z" 
                fill="white"
              />
            </svg>
          </div>

          {/* Text */}
          <div className="flex-1">
            <h3 className="text-sm font-bold text-gray-800 leading-tight">
              Obserwuj nas na Facebooku!
            </h3>
            <p className="text-xs text-gray-600 mt-1">
              Dołącz do naszej społeczności
            </p>
          </div>
        </div>
      </div>

      {/* Animation styles */}
      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};
