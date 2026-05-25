import { useState } from 'react';
import SlidePanel from '../../components/common/SlidePanel.jsx';
import ScoreTag from '../../components/common/ScoreTag.jsx';

/**
 * GraphSubView — vertical career timeline.
 *
 * Uses a centered staggered timeline.
 * Click any node → SlidePanel slides in from the right with path detail.
 */
export default function GraphSubView({ graphData, candidateName }) {
  const [selectedPath, setSelectedPath] = useState(null);

  const { current = [], oneYear = [], threeYear = [] } = graphData ?? {};

  // Build a "current position" node from the candidate's name/identity
  const currentNode = {
    role: candidateName ?? 'You',
    label: 'CURRENT',
    isCurrent: true,
  };

  function NodeCard({ node }) {
    return (
      <div
        className="section-card"
        onClick={() => !node.isCurrent && setSelectedPath(node)}
        style={{
          cursor: node.isCurrent ? 'default' : 'pointer',
          padding: '1.5rem',
          marginBottom: 0,
          border: node.isCurrent ? '2px solid var(--accent-primary)' : '1px solid var(--border-color)',
          transition: 'all 0.3s ease',
          background: 'var(--surface-white)',
          boxShadow: 'var(--shadow-sm)',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          position: 'relative',
          zIndex: 3
        }}
        onMouseOver={(e) => {
          if (!node.isCurrent) {
            e.currentTarget.style.borderColor = 'var(--accent-primary)';
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = 'var(--shadow-md)';
          }
        }}
        onMouseOut={(e) => {
          if (!node.isCurrent) {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.transform = 'none';
            e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
          }
        }}
        role={node.isCurrent ? undefined : 'button'}
        tabIndex={node.isCurrent ? -1 : 0}
        onKeyDown={(e) => !node.isCurrent && e.key === 'Enter' && setSelectedPath(node)}
        aria-label={node.isCurrent ? undefined : `View details for ${node.role_title ?? node.role ?? node.title}`}
      >
        <div style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          {node.role_title ?? node.role ?? node.title ?? 'Role'}
        </div>
        {node.alignment && <ScoreTag value={node.alignment} />}
      </div>
    );
  }

  function TimelineRow({ nodes, label, index }) {
    if (!nodes || nodes.length === 0) return null;
    
    // Alternating sides: 0 = left, 1 = right, 2 = left
    const isLeft = index % 2 === 0;

    return (
      <div style={{ position: 'relative', width: '100%', display: 'flex', justifyContent: isLeft ? 'flex-start' : 'flex-end', marginBottom: '4rem' }}>
        {/* Connecting horizontal line to the center dot */}
        <div style={{
          position: 'absolute',
          left: isLeft ? '45%' : '50%',
          width: '5%',
          top: '32px',
          height: '2px',
          background: 'var(--border-color)',
          zIndex: 1
        }} />

        {/* The dot on the timeline */}
        <div style={{
          position: 'absolute',
          left: '50%',
          top: '32px',
          transform: 'translate(-50%, -50%)',
          width: '20px',
          height: '20px',
          borderRadius: '50%',
          background: 'var(--surface-white)',
          border: '4px solid var(--accent-primary)',
          zIndex: 2,
          boxShadow: '0 0 0 4px var(--bg-canvas)' // helps it stand out from the vertical line
        }} />

        {/* Content Box */}
        <div style={{ width: '45%', position: 'relative', zIndex: 3 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: isLeft ? 'flex-end' : 'flex-start', marginBottom: '1.5rem' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.1rem', letterSpacing: '0.15em', color: 'var(--accent-secondary)', fontWeight: '600' }}>
              {label}
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
             {nodes.map((n, i) => <NodeCard key={i} node={n} />)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="graph-view" style={{ padding: '2rem 1rem' }}>
      
      <div style={{ position: 'relative', maxWidth: '1000px', margin: '0 auto', padding: '2rem 0' }}>
        {/* Main vertical spine in the center */}
        <div style={{ 
           position: 'absolute', 
           left: '50%', 
           transform: 'translateX(-50%)',
           top: '2rem', 
           bottom: '2rem', 
           width: '2px', 
           background: 'var(--border-color)',
           zIndex: 1
        }} />

        {/* Current node */}
        <TimelineRow nodes={[currentNode]} label="CURRENT" index={0} />

        {/* 1-year nodes */}
        {oneYear.length > 0 && <TimelineRow nodes={oneYear} label="1 YEAR PLAN" index={1} />}

        {/* 3-year nodes */}
        {threeYear.length > 0 && <TimelineRow nodes={threeYear} label="3 YEAR PLAN" index={2} />}

        {/* Fallback */}
        {oneYear.length === 0 && threeYear.length === 0 && current.length > 0 && (
          <TimelineRow nodes={current} label="PATH" index={1} />
        )}
      </div>

      {/* Slide Panel */}
      {selectedPath && (
        <SlidePanel
          title={selectedPath.role_title ?? selectedPath.role ?? selectedPath.title ?? 'Path Detail'}
          onClose={() => setSelectedPath(null)}
        >
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <ScoreTag value={selectedPath.alignment} />
            {selectedPath.time_to_ready && (
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                ⏱ {selectedPath.time_to_ready}
              </span>
            )}
          </div>

          {(selectedPath.current_strengths?.length > 0 || selectedPath.strengths?.length > 0) && (
            <div>
              <div className="slide-panel-section-label">Strengths</div>
              <ul className="career-path-list">
                {(selectedPath.current_strengths ?? selectedPath.strengths).map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}

          {selectedPath.gaps?.length > 0 && (
            <div>
              <div className="slide-panel-section-label">Gaps</div>
              <ul className="career-path-list">
                {selectedPath.gaps.map((g, i) => {
                  if (typeof g === 'string') return <li key={i}>{g}</li>;
                  return (
                    <li key={i}>
                      <strong>{g.category || g.description}</strong>
                      {g.category && g.description ? `: ${g.description}` : ''}
                      {g.severity && <ScoreTag value={g.severity} />}
                      {g.how_to_close && <div style={{ marginTop: '4px', fontSize: '0.85em', color: 'var(--text-muted)' }}>↳ {g.how_to_close}</div>}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {selectedPath.next_steps?.length > 0 && (
            <div>
              <div className="slide-panel-section-label">Next Steps</div>
              <ul className="career-path-list">
                {selectedPath.next_steps.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </SlidePanel>
      )}
    </div>
  );
}
