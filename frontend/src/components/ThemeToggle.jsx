import React from 'react';

/**
 * ThemeToggle component that floats in the top-right.
 * Uses inline-styled transforms + CSS transitions to rotate and scale the Sun and Moon SVG icons.
 */
export default function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark';

  return (
    <button
      className="theme-toggle-btn"
      onClick={onToggle}
      aria-label="Toggle dark mode"
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <div style={{ position: 'relative', width: '20px', height: '20px' }}>
        {/* Sun Icon */}
        <svg
          className="theme-toggle-icon"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            transform: isDark ? 'rotate(90deg) scale(0)' : 'rotate(0) scale(1)',
            opacity: isDark ? 0 : 1,
            color: 'var(--accent-secondary)'
          }}
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>

        {/* Moon Icon */}
        <svg
          className="theme-toggle-icon"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            transform: isDark ? 'rotate(0) scale(1)' : 'rotate(-90deg) scale(0)',
            opacity: isDark ? 1 : 0,
            color: 'var(--accent-secondary)'
          }}
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
      </div>
    </button>
  );
}
