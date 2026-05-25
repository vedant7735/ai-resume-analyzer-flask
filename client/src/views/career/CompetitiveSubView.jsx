import ScoreTag from '../../components/common/ScoreTag.jsx';

/**
 * CompetitiveSubView — benchmark table.
 *
 * competitive_analysis shape expected from backend:
 * {
 *   roles: [
 *     {
 *       role: "...",
 *       categories: [
 *         { category: "Years Experience", your_level: "3 years", ideal_level: "5 years", gap: "MODERATE" },
 *         ...
 *       ]
 *     }
 *   ]
 * }
 *
 * Fallback: if backend returns a flat array or different shape, we adapt gracefully.
 */
export default function CompetitiveSubView({ competitiveAnalysis }) {
  // Normalise to array of role-groups
  const groups = normalise(competitiveAnalysis);

  if (!groups.length) {
    return (
      <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.9rem' }}>
        No competitive analysis available.
      </p>
    );
  }

  return (
    <div className="competitive-view">
      {groups.map((group, gi) => (
        <div className="section-card" key={gi} style={{ marginBottom: 'var(--spacing-lg)' }}>
          {group.role && (
            <h3 style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.8rem',
              letterSpacing: '0.1em',
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              marginBottom: 'var(--spacing-md)',
            }}>
              {group.role}
            </h3>
          )}

          <div style={{ overflowX: 'auto' }}>
            <table className="benchmark-table">
              <thead>
                <tr>
                  <th>CATEGORY</th>
                  <th>YOURS</th>
                  <th>IDEAL</th>
                  <th>GAP</th>
                </tr>
              </thead>
              <tbody>
                {group.categories.map((row, ri) => (
                  <tr key={ri}>
                    <td className="benchmark-category">{row.category}</td>
                    <td className="benchmark-level">{row.your_level ?? '—'}</td>
                    <td className="benchmark-level">{row.ideal_level ?? '—'}</td>
                    <td><ScoreTag value={row.gap} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Normalise various shapes the backend might return into:
 * [{ role, categories: [ { category, your_level, ideal_level, gap } ] }]
 */
function normalise(data) {
  if (!data) return [];

  // 1. The NEW strict schema from your updated prompt:
  // Array of { role_title, benchmarks: { category_key: { candidate, ideal, gap } }, overall_benchmark }
  if (Array.isArray(data) && data.length > 0 && data[0].benchmarks) {
    return data.map(item => {
      const categories = Object.entries(item.benchmarks).map(([key, val]) => ({
        category: key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        your_level: val.candidate ?? val.your_level,
        ideal_level: val.ideal ?? val.ideal_level,
        gap: val.gap
      }));
      return { role: item.role_title, categories };
    });
  }

  // 2. Already the expected array of role groups (old schema)
  if (Array.isArray(data?.roles)) {
    return data.roles.filter(r => r?.categories?.length > 0);
  }

  // 3. Backend returned a flat array of category rows (no role grouping)
  if (Array.isArray(data)) {
    return data.length && !data[0].role_title ? [{ role: null, categories: data }] : [];
  }

  // 4. Backend returned { categories: [...] } flat object
  if (Array.isArray(data?.categories)) {
    return [{ role: null, categories: data.categories }];
  }

  // 5. Try to use object keys as role names
  const entries = Object.entries(data);
  if (entries.length > 0 && Array.isArray(entries[0][1])) {
    return entries.map(([role, categories]) => ({ role, categories }));
  }

  return [];
}
