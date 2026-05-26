import ScoreTag from '../../components/common/ScoreTag.jsx';

/**
 * PathsSubView — grid of career path cards.
 * Each card shows: role title, alignment badge, strengths, gaps, next steps, time-to-ready.
 */
export default function PathsSubView({ paths }) {
  if (!paths?.length) {
    return (
      <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.9rem' }}>
        No career paths available.
      </p>
    );
  }

  return (
    <div className="career-paths-grid">
      {paths.map((path, i) => (
        <div className="career-path-card" key={i}>
          <div className="career-path-header">
            <div className="career-path-title">{path.role_title ?? path.role ?? path.title ?? 'Role'}</div>
            <ScoreTag value={path.alignment} />
          </div>

          <p className="career-path-meta">
            {path.time_to_ready ? `⏱ ${path.time_to_ready}` : ''}
          </p>

          {/* Strengths */}
          {(path.current_strengths?.length > 0 || path.strengths?.length > 0) && (
            <div>
              <div className="career-path-section-label">Strengths</div>
              <ul className="career-path-list">
                {(path.current_strengths ?? path.strengths).map((s, j) => <li key={j}>{s}</li>)}
              </ul>
            </div>
          )}

          {/* Gaps */}
          {path.gaps?.length > 0 && (
            <div>
              <div className="career-path-section-label">Gaps</div>
              <ul className="career-path-list">
                {path.gaps.map((g, j) => {
                  // Support both the old string format and the new object format
                  if (typeof g === 'string') return <li key={j}>{g}</li>;
                  return (
                    <li key={j}>
                      <strong>{g.category || g.description}</strong>
                      {g.category && g.description ? `: ${g.description}` : ''}
                      {g.severity && <ScoreTag value={g.severity} />}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {/* Next Steps */}
          {path.next_steps?.length > 0 && (
            <div>
              <div className="career-path-section-label">Next Steps</div>
              <ul className="career-path-list">
                {path.next_steps.map((s, j) => <li key={j}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
