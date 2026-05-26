/**
 * ScoreTag — alignment badge: HIGH | MODERATE | LOW
 * Used in Career paths and Competitive table.
 */
export default function ScoreTag({ value }) {
  const normalised = (value ?? '').toUpperCase();

  const modifier =
    normalised === 'HIGH'     ? 'high'     :
    normalised === 'MODERATE' ? 'moderate' :
    normalised === 'LOW'      ? 'low'      : 'moderate';

  return (
    <span className={`score-tag score-tag--${modifier}`}>
      {normalised || '—'}
    </span>
  );
}
