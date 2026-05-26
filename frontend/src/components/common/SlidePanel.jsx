import { useEffect } from 'react';

/**
 * SlidePanel — right-side drawer.
 * Animates in from the right via CSS keyframe.
 * Closes on overlay click or × button.
 *
 * Props:
 *  - title    {string}
 *  - onClose  {() => void}
 *  - children {ReactNode}
 */
export default function SlidePanel({ title, onClose, children }) {
  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <>
      {/* Backdrop */}
      <div
        className="slide-panel-overlay"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <aside className="slide-panel" role="dialog" aria-modal="true" aria-label={title}>
        <div className="slide-panel-header">
          <h2 className="slide-panel-title">{title}</h2>
          <button
            className="slide-panel-close"
            onClick={onClose}
            aria-label="Close panel"
          >
            ×
          </button>
        </div>
        <div className="slide-panel-body">
          {children}
        </div>
      </aside>
    </>
  );
}
