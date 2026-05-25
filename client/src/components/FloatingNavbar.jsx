/**
 * FloatingNavbar — fixed pill-shaped island at top-center.
 * Disabled items (Analysis, Career, Editor) are greyed out
 * and non-interactive until a resume has been processed.
 */
export default function FloatingNavbar({ activeView, stage, onNavigate }) {
  const isReady = stage === 'ready';

  const items = [
    { id: 'upload',   label: 'UPLOAD',   alwaysEnabled: true  },
    { id: 'analysis', label: 'ANALYSIS', alwaysEnabled: false },
    { id: 'career',   label: 'CAREER',   alwaysEnabled: false },
    { id: 'editor',   label: 'EDITOR',   alwaysEnabled: false },
  ];

  return (
    <nav className="floating-navbar" aria-label="Primary navigation">
      {items.map(({ id, label, alwaysEnabled }) => {
        const enabled = alwaysEnabled || isReady;
        const active  = activeView === id;

        return (
          <button
            key={id}
            id={`nav-${id}`}
            className={[
              'nav-item',
              active   ? 'nav-item--active'   : '',
              !enabled ? 'nav-item--disabled' : '',
            ].join(' ').trim()}
            onClick={() => enabled && onNavigate(id)}
            aria-current={active ? 'page' : undefined}
            disabled={!enabled}
            title={!enabled ? 'Upload a resume first' : undefined}
          >
            {label}
          </button>
        );
      })}
    </nav>
  );
}
