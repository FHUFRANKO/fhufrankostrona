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
          {/* Facebook Logo - Square */}
          <div className="flex-shrink-0">
            <svg 
              className="w-14 h-14 hover:scale-105 transition-transform"
              viewBox="0 0 48 48" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect x="0" y="0" width="48" height="48" rx="8" fill="#1877F2"/>
              <path 
                d="M26.5016 25.5L27.1059 21.8156H23.5764V19.4969C23.5764 18.4812 24.0763 17.4906 25.7247 17.4906H27.2506V14.4094C27.2506 14.4094 25.7247 14.1562 24.2684 14.1562C21.2339 14.1562 19.2588 15.9937 19.2588 19.0781V21.8156H16V25.5H19.2588V34.8438C19.9201 34.9469 20.5982 35 21.2882 35C21.9782 35 22.6563 34.9469 23.3176 34.8438V25.5H26.5016Z" 
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
              Nowe ogłoszenia na FB
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
