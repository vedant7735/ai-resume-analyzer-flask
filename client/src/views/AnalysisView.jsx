import { useState } from 'react';
import AccordionItem from '../components/common/AccordionItem.jsx';

/**
 * AnalysisView — full dashboard port of the original HTML/JS dashboard.
 * Sections: Score, Professional Summary, Strengths, Improvements,
 *           Recommended Roles, ATS Keywords, Tabbed Data (Projects/Experience/Education/Skills)
 */
export default function AnalysisView({ resume, analysis, onNavigate }) {
  const [activeMainTab, setActiveMainTab] = useState('resume');
  const [activeTab, setActiveTab] = useState('projects');

  const score     = analysis.score     ?? {};
  const breakdown = score.breakdown    ?? {};

  const tabs = ['projects', 'experience', 'education', 'skills'];

  return (
    <>
      <nav className="career-subnav" aria-label="Analysis sub-navigation">
        <button
          className={['subnav-item', activeMainTab === 'resume' ? 'subnav-item--active' : ''].join(' ').trim()}
          onClick={() => setActiveMainTab('resume')}
        >
          RESUME ANALYSIS
        </button>
        {resume.jd_match && (
          <button
            className={['subnav-item', activeMainTab === 'jd' ? 'subnav-item--active' : ''].join(' ').trim()}
            onClick={() => setActiveMainTab('jd')}
          >
            JOB DESCRIPTION ANALYSIS
          </button>
        )}
      </nav>

      <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <h1 className="dashboard-title">
            <span className="title-heavy">ANALYSIS</span>{' '}
            <span className="title-italic">Report</span>
          </h1>
          <p className="candidate-name" id="candidateName">
            {resume.identity?.name || 'Unknown Candidate'}
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn-download"
            id="openEditorBtn"
            onClick={() => onNavigate('editor')}
          >
            <span className="btn-text">✏ EDIT RESUME</span>
          </button>
          <button
            className="btn-secondary"
            id="uploadNewBtn"
            onClick={() => onNavigate('upload')}
          >
            <span className="btn-text">← UPLOAD NEW</span>
          </button>
        </div>
      </div>

      {/* JD Alignment Section */}
      {activeMainTab === 'jd' && resume.jd_match && (
        <>
          <div className="score-section">
            {/* JD Main score */}
            <div className="score-card score-main">
              <div className="score-label" style={{ color: '#4A6070' }}>JD MATCH SCORE</div>
              <div className="score-value" style={{ color: '#4A6070' }}>
                {resume.jd_match.overall_score ?? '--'}
              </div>
              <div className="score-bar">
                <div
                  className="score-bar-fill"
                  style={{ width: `${resume.jd_match.overall_score ?? 0}%`, background: 'linear-gradient(90deg, #4A6070, #738A9A)' }}
                />
              </div>
              <div className="score-explanation">
                <span style={{ fontWeight: '600', color: '#4A6070' }}>Target Role:</span> {resume.jd_match.role_title} {resume.jd_match.company ? `at ${resume.jd_match.company}` : ''}<br/><br/>
                {resume.jd_match.summary}
              </div>
            </div>

            {/* JD Breakdown */}
            <div className="score-breakdown">
              {[
                { label: 'SKILLS',      value: resume.jd_match.section_scores?.skills      },
                { label: 'EXPERIENCE',  value: resume.jd_match.section_scores?.experience  },
                { label: 'EDUCATION',   value: resume.jd_match.section_scores?.education   },
                { label: 'PROJECTS',    value: resume.jd_match.section_scores?.projects    },
                { 
                  label: 'KEYWORDS',    
                  value: ((resume.jd_match.matched_keywords?.length || 0) + (resume.jd_match.missing_keywords?.length || 0)) > 0 
                    ? Math.round((resume.jd_match.matched_keywords?.length || 0) / ((resume.jd_match.matched_keywords?.length || 0) + (resume.jd_match.missing_keywords?.length || 0)) * 100)
                    : '--'
                },
              ].map(({ label, value }, idx) => (
                <div className="breakdown-item" key={idx}>
                  <div className="breakdown-label">{label}</div>
                  <div className="breakdown-score">
                    {value ?? '--'}
                  </div>
                  <div className="breakdown-bar">
                    <div
                      className="breakdown-bar-fill"
                      style={{ width: `${value !== '--' ? value : 0}%`, background: '#4A6070' }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="two-column">
            <div className="section-card">
              <h3 style={{ fontSize: '0.85rem', letterSpacing: '0.1em', fontFamily: 'var(--font-mono)', color: '#4A6070', marginBottom: '15px' }}>MATCHED KEYWORDS</h3>
              <div className="keyword-cloud">
                {(resume.jd_match.matched_keywords ?? []).length > 0 ? (
                  (resume.jd_match.matched_keywords ?? []).map((kw, i) => (
                    <span className="keyword-tag" style={{ background: '#e8f5e9', color: '#2e7d32', border: '1px solid #c8e6c9' }} key={i}>{kw}</span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>None found</span>
                )}
              </div>
            </div>
            <div className="section-card">
              <h3 style={{ fontSize: '0.85rem', letterSpacing: '0.1em', fontFamily: 'var(--font-mono)', color: '#4A6070', marginBottom: '15px' }}>MISSING KEYWORDS</h3>
              <div className="keyword-cloud">
                {(resume.jd_match.missing_keywords ?? []).length > 0 ? (
                  (resume.jd_match.missing_keywords ?? []).map((kw, i) => (
                    <span className="keyword-tag" style={{ background: '#ffebee', color: '#c62828', border: '1px solid #ffcdd2' }} key={i}>{kw}</span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>None missing</span>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {activeMainTab === 'resume' && (
        <>
          {/* Score Overview */}
          <div className="score-section">
        {/* Main score */}
        <div className="score-card score-main">
          <div className="score-label">OVERALL SCORE</div>
          <div className="score-value" id="overallScore">
            {score.overall ?? '--'}
          </div>
          <div className="score-bar">
            <div
              className="score-bar-fill"
              id="overallScoreBar"
              style={{ width: `${score.overall ?? 0}%` }}
            />
          </div>
          <div className="score-explanation" id="scoreExplanation">
            {score.explanation ?? ''}
          </div>
        </div>

        {/* Breakdown */}
        <div className="score-breakdown">
          {[
            { label: 'CONTENT',      key: 'content_quality', id: 'contentScore'      },
            { label: 'STRUCTURE',    key: 'structure',        id: 'structureScore'    },
            { label: 'IMPACT',       key: 'impact',           id: 'impactScore'       },
            { label: 'COMPLETENESS', key: 'completeness',     id: 'completenessScore' },
            { label: 'FORMATTING',   key: 'formatting',       id: 'formattingScore'   },
          ].map(({ label, key, id }) => (
            <div className="breakdown-item" key={key}>
              <div className="breakdown-label">{label}</div>
              <div className="breakdown-score" id={id}>
                {breakdown[key] ?? '--'}
              </div>
              <div className="breakdown-bar">
                <div
                  className="breakdown-bar-fill"
                  style={{ width: `${breakdown[key] ?? 0}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Professional Summary */}
      <div className="section-card">
        <h2 className="section-title">
          <span className="section-number">01.</span>
          <span className="section-text">PROFESSIONAL SUMMARY</span>
        </h2>
        <p className="summary-text" id="summaryText">
          {analysis.professionalSummary || 'No summary available.'}
        </p>
      </div>

      {/* Strengths & Improvements */}
      <div className="two-column">
        {/* Strengths */}
        <div className="section-card">
          <h2 className="section-title">
            <span className="section-number">02.</span>
            <span className="section-text">STRENGTHS</span>
          </h2>
          <ul className="list-styled" id="strengthsList">
            {(analysis.strengths ?? []).map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>

        {/* Improvements — Accordion */}
        <div className="section-card">
          <h2 className="section-title">
            <span className="section-number">03.</span>
            <span className="section-text">IMPROVEMENTS</span>
          </h2>
          <div id="improvementsList">
            {(analysis.improvements ?? []).map((imp, i) => (
              <AccordionItem
                key={i}
                defaultOpen={i === 0}
                header={
                  <>
                    <span className="improvement-section">{imp.section}</span>
                    <div className="improvement-issue">{imp.issue}</div>
                  </>
                }
                priorityBadge={
                  <span
                    className={`priority-badge priority-${(imp.priority ?? '').toLowerCase()}`}
                  >
                    {imp.priority}
                  </span>
                }
              >
                <div className="improvement-suggestion">{imp.suggestion}</div>
              </AccordionItem>
            ))}
          </div>
        </div>
      </div>

      {/* Recommended Roles */}
      <div className="section-card">
        <h2 className="section-title">
          <span className="section-number">04.</span>
          <span className="section-text">RECOMMENDED ROLES</span>
        </h2>
        <div className="role-tags" id="roleTags">
          {(analysis.recommendedFor ?? []).map((role, i) => (
            <span className="role-tag" key={i}>{role}</span>
          ))}
        </div>
      </div>

      {/* ATS Keywords */}
      <div className="section-card">
        <h2 className="section-title">
          <span className="section-number">05.</span>
          <span className="section-text">ATS KEYWORDS</span>
        </h2>
        <div className="keyword-cloud" id="keywordCloud">
          {(analysis.atsKeywords ?? []).map((kw, i) => (
            <span className="keyword-tag" key={i}>{kw}</span>
          ))}
        </div>
      </div>

      {/* Detailed Data Tabs */}
      <div className="section-card">
        <h2 className="section-title">
          <span className="section-number">06.</span>
          <span className="section-text">DETAILED DATA</span>
        </h2>

        <div className="tabs">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={`tab-btn${activeTab === tab ? ' active' : ''}`}
              data-tab={tab}
              onClick={() => setActiveTab(tab)}
            >
              {tab.toUpperCase()}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {/* Projects */}
          <div
            id="tab-projects"
            className={`tab-pane${activeTab === 'projects' ? ' active' : ''}`}
          >
            {(resume.projects ?? []).map((p, i) => (
              <div className="data-item" key={i}>
                <div className="data-item-header">
                  <div className="data-title">{p.title}</div>
                  <div className="data-meta">{p.type} • {p.year}</div>
                </div>
                <div className="data-tags">
                  {(p.tech_stack ?? []).map((t, j) => (
                    <span className="data-tag" key={j}>{t}</span>
                  ))}
                </div>
                <ul className="data-details">
                  {(p.bullets ?? []).map((b, j) => <li key={j}>{b}</li>)}
                </ul>
              </div>
            ))}
          </div>

          {/* Experience */}
          <div
            id="tab-experience"
            className={`tab-pane${activeTab === 'experience' ? ' active' : ''}`}
          >
            {(resume.experience ?? []).map((exp, i) => (
              <div className="data-item" key={i}>
                <div className="data-item-header">
                  <div className="data-title">{exp.title}</div>
                  <div className="data-meta">{exp.company} • {exp.duration} • {exp.type}</div>
                </div>
                <ul className="data-details">
                  {(exp.bullets ?? []).map((b, j) => <li key={j}>{b}</li>)}
                </ul>
              </div>
            ))}
          </div>

          {/* Education */}
          <div
            id="tab-education"
            className={`tab-pane${activeTab === 'education' ? ' active' : ''}`}
          >
            {(resume.education ?? []).map((edu, i) => (
              <div className="data-item" key={i}>
                <div className="data-item-header">
                  <div className="data-title">{edu.degree} in {edu.major}</div>
                  <div className="data-meta">
                    {edu.institution} • {edu.graduation_year} • GPA: {edu.gpa}
                  </div>
                </div>
                {(edu.relevant_coursework?.length > 0) && (
                  <div className="data-tags">
                    {edu.relevant_coursework.map((c, j) => (
                      <span className="data-tag" key={j}>{c}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Skills */}
          <div
            id="tab-skills"
            className={`tab-pane${activeTab === 'skills' ? ' active' : ''}`}
          >
            {[
              { title: 'Languages',  data: resume.skills?.languages  ?? [] },
              { title: 'Frameworks', data: resume.skills?.frameworks ?? [] },
              { title: 'Tools',      data: resume.skills?.tools      ?? [] },
              { title: 'Domains',    data: resume.skills?.domains    ?? [] },
            ].filter(c => c.data.length > 0).map((cat, i) => (
              <div className="data-item" key={i}>
                <div className="data-title">{cat.title}</div>
                <div className="data-tags">
                  {cat.data.map((item, j) => (
                    <span className="data-tag" key={j}>{item}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      </>
      )}
    </div>
    </>
  );
}
