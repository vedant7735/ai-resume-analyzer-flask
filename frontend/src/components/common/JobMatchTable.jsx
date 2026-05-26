import React, { useState } from 'react';
import './JobMatchTable.css';

const TargetIcon = ({ size = 18 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
    <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
    <circle cx="12" cy="12" r="2" fill="currentColor" />
  </svg>
);

const SearchIcon = ({ size = 16 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      cx="11"
      cy="11"
      r="6"
      stroke="currentColor"
      strokeWidth="2"
    />
    <path
      d="M20 20L16.65 16.65"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

const RemoteIcon = ({ size = 14 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      cx="12"
      cy="12"
      r="9"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M3 12H21"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M12 3C14.5 5.5 16 8.5 16 12C16 15.5 14.5 18.5 12 21"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M12 3C9.5 5.5 8 8.5 8 12C8 15.5 9.5 18.5 12 21"
      stroke="currentColor"
      strokeWidth="1.8"
    />
  </svg>
);

const OfficeIcon = ({ size = 14 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      x="5"
      y="3"
      width="14"
      height="18"
      rx="2"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M9 8H10"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M14 8H15"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M9 12H10"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M14 12H15"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M10 21V17H14V21"
      stroke="currentColor"
      strokeWidth="1.8"
    />
  </svg>
);

const JobMatchTable = ({ jobs, loading, error, analysisData }) => {
  const [sortConfig, setSortConfig] = useState({
    key: 'match_score',
    direction: 'desc'
  });

  const hasSalaryInfo = jobs.some(
    job => job.salary !== null && job.salary !== undefined && String(job.salary).trim() !== ''
  );

  const formatSalary = (job) => {
    const raw = job.salary;           // original string from posting
    const minLpa = job.salary_min;
    const maxLpa = job.salary_max;
    const currency = job.salary_currency; // e.g. 'USD', 'GBP', 'INR'

    // If we have no parsed bounds, just show the raw string
    if (minLpa == null && maxLpa == null) {
      return raw || 'Not specified';
    }

    const fmtLpa = (v) => {
      const r = Math.round(v * 10) / 10;
      return `${r} LPA`;
    };

    const lpaStr = minLpa === maxLpa
      ? fmtLpa(minLpa)
      : `${fmtLpa(minLpa)} – ${fmtLpa(maxLpa)}`;

    // For non-INR, show "$120k (~101 LPA)" style
    if (currency && currency !== 'INR' && raw) {
      return `${raw}  (~${lpaStr})`;
    }

    // For INR / bare LPA values just show the canonical form
    return lpaStr;
  };

  const handleSort = (key) => {
    let direction = 'desc';

    if (
      sortConfig.key === key &&
      sortConfig.direction === 'desc'
    ) {
      direction = 'asc';
    }

    setSortConfig({ key, direction });
  };

  const sortedJobs = [...jobs].sort((a, b) => {
    let valA = a[sortConfig.key];
    let valB = b[sortConfig.key];

    // Handle null/undefined values for salary sorting
    if (valA == null) valA = sortConfig.key === 'salary_min' ? 0 : '';
    if (valB == null) valB = sortConfig.key === 'salary_min' ? 0 : '';

    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (valA < valB) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }

    if (valA > valB) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }

    return 0;
  });

  const getScoreColor = (score) => {
    if (score >= 80) {
      return 'var(--success-color, #10b981)';
    }

    if (score >= 60) {
      return 'var(--accent-jd, #4A6070)';
    }

    return 'var(--error-color, #ef4444)';
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) {
      return '↕';
    }

    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  return (
    <div className="job-match-container">
      <div className="job-match-header">
        <h3
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            margin: 0
          }}
        >
          <TargetIcon />
          Job Opportunities
        </h3>
      </div>

      {jobs.length > 0 && !loading && (
        <div className="job-table-wrapper">
          <div className="job-table-controls">
            <span style={{ color: 'var(--text-secondary)' }}>
              Found: {jobs.length} jobs
            </span>
          </div>

          <table className="job-table">
            <thead>
              <tr>
                <th
                  onClick={() => handleSort('match_score')}
                  style={{
                    cursor: 'pointer',
                    width: '110px',
                    whiteSpace: 'nowrap'
                  }}
                >
                  MATCH {getSortIcon('match_score')}
                </th>

                <th>
                  JOB TITLE
                </th>

                <th
                  onClick={() => handleSort('company')}
                  style={{ cursor: 'pointer' }}
                >
                  COMPANY {getSortIcon('company')}
                </th>

                <th>
                  LOCATION
                </th>

                {hasSalaryInfo && (
                  <th
                    onClick={() => handleSort('salary_min')}
                    style={{ cursor: 'pointer' }}
                  >
                    SALARY {getSortIcon('salary_min')}
                  </th>
                )}

                <th style={{ textAlign: 'center', width: '120px' }}>APPLY</th>
              </tr>
            </thead>

            <tbody>
              {sortedJobs.map((job, idx) => (
                <tr key={idx}>
                  <td className="score-cell">
                    <div
                      style={{
                        color: getScoreColor(job.match_score),
                        fontWeight: 'bold',
                        fontSize: '1.2rem'
                      }}
                    >
                      {job.match_score}%
                    </div>

                    <div
                      className="progress-bar-bg"
                      title={(job.match_reasons || []).join('\n')}
                    >
                      <div
                        className="progress-bar-fill"
                        style={{
                          width: `${job.match_score}%`,
                          backgroundColor: getScoreColor(
                            job.match_score
                          )
                        }}
                      />
                    </div>
                  </td>

                  <td>
                    <div
                      style={{
                        fontWeight: 500,
                        color: 'var(--text-primary)'
                      }}
                    >
                      {job.title}
                    </div>

                    <div className="job-requirements">
                      {(job.requirements || [])
                        .slice(0, 5)
                        .join(' • ')}

                      {job.requirements?.length > 5 &&
                        ' ...'}
                    </div>
                  </td>

                  <td style={{ fontWeight: 500 }}>
                    {job.company}
                  </td>

                  <td>
                    <div>{job.location}</div>

                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        fontSize: '0.8rem',
                        color: 'var(--text-muted)',
                        marginTop: '0.2rem'
                      }}
                    >
                      {job.remote ? (
                        <>
                          <RemoteIcon />
                          Remote
                        </>
                      ) : (
                        <>
                          <OfficeIcon />
                          Onsite
                        </>
                      )}
                    </div>
                  </td>

                  {hasSalaryInfo && (
                    <td
                      style={{
                        color:
                          'var(--success-color, #10b981)'
                      }}
                    >
                      {formatSalary(job)}
                    </td>
                  )}

                  <td style={{ textAlign: 'center', verticalAlign: 'middle' }}>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        padding: '0.45rem 1rem',
                        backgroundColor: 'var(--accent-secondary)',
                        color: '#fff',
                        borderRadius: '6px',
                        textDecoration: 'none',
                        fontWeight: '600',
                        fontSize: '0.85rem',
                        border: '1px solid var(--accent-secondary-dark)',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                      }}
                    >
                      Apply
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
      }
    </div>
  );
};

export default JobMatchTable;