/**
 * CareerSubNav — second floating pill island.
 * Appears below the main navbar ONLY when the Career view is active.
 * Slides down + fades in via CSS keyframe animation.
 */
export default function CareerSubNav({ activeSubView, onNavigate }) {
  const items = [
    { id: 'paths',       label: 'PATHS'        },
    { id: 'graph',       label: 'CAREER GRAPH' },
    { id: 'competitive', label: 'COMPETITIVE'  },
  ];

  return (
    <nav className="career-subnav" aria-label="Career sub-navigation">
      {items.map(({ id, label }) => (
        <button
          key={id}
          id={`subnav-${id}`}
          className={[
            'subnav-item',
            activeSubView === id ? 'subnav-item--active' : '',
          ].join(' ').trim()}
          onClick={() => onNavigate(id)}
          aria-current={activeSubView === id ? 'page' : undefined}
        >
          {label}
        </button>
      ))}
    </nav>
  );
}
