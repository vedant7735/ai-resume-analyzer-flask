/**
 * FloatingNavbar — fixed pill-shaped island at top-center.
 * Disabled items (Analysis, Career, Editor) are greyed out
 * and non-interactive until a resume has been processed.
 */
export default function FloatingNavbar({ activeView, stage, onNavigate }) {
  const isReady = stage === 'ready';

  const items = [
    { id: 'upload', label: 'UPLOAD', alwaysEnabled: true },
    { id: 'analysis', label: 'ANALYSIS', alwaysEnabled: false },
    { id: 'career', label: 'CAREER', alwaysEnabled: false },
    { id: 'editor', label: 'EDITOR', alwaysEnabled: false },
    { id: 'jobs', label: 'FIND JOBS', alwaysEnabled: false },
  ];

  return (
    <nav className="floating-navbar" aria-label="Primary navigation">
      {items.map(({ id, label, alwaysEnabled }) => {
        const enabled = alwaysEnabled || isReady;
        const active = activeView === id;

        const isJobsBtn = id === 'jobs';

        return (
          <button
            key={id}
            id={`nav-${id}`}
            className={[
              'nav-item',
              active ? 'nav-item--active' : '',
              !enabled ? 'nav-item--disabled' : '',
            ].join(' ').trim()}
            style={isJobsBtn ? {
              background: active ? 'var(--gradient-jobs)' : (enabled ? 'var(--gradient-jobs)' : 'transparent'),
              color: enabled ? 'white' : 'inherit',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            } : {}}
            onClick={() => enabled && onNavigate(id)}
            aria-current={active ? 'page' : undefined}
            disabled={!enabled}
            title={!enabled ? 'Upload a resume first' : undefined}
          >
            {isJobsBtn && (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            )}
            {label}
          </button>
        );
      })}
    </nav>
  );
}
