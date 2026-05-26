import React, { useState } from 'react';
import JobMatchTable from '../components/common/JobMatchTable.jsx';
import JobFilters from '../components/common/JobFilters.jsx';
import * as api from '../services/api.js';

export default function FindJobsView({ resume, analysis, market, dispatch }) {
  const [searchFilters, setSearchFilters] = useState({
    locations: [],
    workModes: [],
    salaryMin: '',
    salaryMax: ''
  });
  const [searchMeta, setSearchMeta] = useState({ relaxedFilters: false, appliedFilters: {} });
  
  // Collapse filters automatically if jobs are already loaded (e.g. from cache or prev search)
  const [isCollapsed, setIsCollapsed] = useState(market.jobs?.length > 0);

  const handleFindJobs = async () => {
    dispatch({ type: 'SET_MARKET_STATE', payload: { loading: true, error: null, searched: true } });
    try {
      const result = await api.findJobs(resume, searchFilters);
      if (result.success) {
        dispatch({ type: 'SET_MARKET_STATE', payload: { jobs: result.jobs || [] } });
        setSearchMeta({
          relaxedFilters: result.relaxed_filters ?? false,
          appliedFilters: result.applied_filters ?? {}
        });
        setIsCollapsed(true); // Collapse on successful search
      } else {
        dispatch({ type: 'SET_MARKET_STATE', payload: { error: result.error || 'Failed to fetch jobs' } });
      }
    } catch (err) {
      dispatch({ type: 'SET_MARKET_STATE', payload: { error: err.message } });
    } finally {
      dispatch({ type: 'SET_MARKET_STATE', payload: { loading: false } });
    }
  };

  return (
    <div className="dashboard-container" style={{ maxWidth: '95%', width: '100%', padding: '2rem' }}>
      <div className="dashboard-header" style={{ marginBottom: '2rem' }}>
        <div className="header-left">
          <h1 className="dashboard-title">
            <span className="title-heavy">LIVE</span>{' '}
            <span className="title-italic">Market</span>
          </h1>
          <p className="candidate-name">
            Real-time job matching for {resume.identity?.name || 'Candidate'}
          </p>
        </div>
      </div>

      <JobFilters 
        filters={searchFilters} 
        setFilters={setSearchFilters} 
        onSearch={handleFindJobs}
        loading={market.loading}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        analysisData={analysis}
      />

      {market.error && (
        <div className="job-error-banner" style={{ margin: '1.5rem 0', padding: '1rem', border: '1px solid var(--error-color, #ef4444)', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.08)', color: 'var(--error-color, #ef4444)' }}>
          <strong style={{ fontWeight: '600' }}>Search Error:</strong> {market.error}
        </div>
      )}

      {market.loading && (!market.jobs || market.jobs.length === 0) && (
        <div className="job-loading-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', gap: '1.2rem', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '12px', marginTop: '1.5rem' }}>
          <div className="job-loading-spinner" style={{ width: '40px', height: '40px', border: '3px solid rgba(255,255,255,0.08)', borderTop: '3px solid var(--accent-secondary, #4A6070)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}></div>
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
          <div style={{ color: 'var(--text-secondary)', fontWeight: '500', fontSize: '0.95rem' }}>Scanning the job market for active listings...</div>
        </div>
      )}

      {!market.loading && !market.error && market.searched && (!market.jobs || market.jobs.length === 0) && (
        <div className="job-empty-state" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', border: '1px dashed var(--border-color)', borderRadius: '12px', textAlign: 'center', gap: '1.2rem', marginTop: '1.5rem', background: 'var(--bg-surface)' }}>
          <div style={{ fontSize: '3rem', filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.15))' }}>🔍</div>
          <h3 style={{ margin: 0, color: 'var(--text-primary)', fontWeight: '600' }}>No Matching Jobs Found</h3>
          <p style={{ color: 'var(--text-muted)', maxWidth: '400px', margin: 0, fontSize: '0.9rem', lineHeight: '1.5' }}>
            We scanned the active boards but couldn't find listings matching your specific filters and profile keywords. Try expanding your search location or work modes.
          </p>
          <button 
            onClick={() => {
              setSearchFilters({ locations: [], workModes: [], salaryMin: '', salaryMax: '' });
              setIsCollapsed(false);
            }}
            style={{ padding: '0.55rem 1.2rem', background: 'var(--accent-secondary)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '600', fontSize: '0.85rem', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', transition: 'all 0.2s' }}
            onMouseOver={(e) => e.currentTarget.style.filter = 'brightness(1.15)'}
            onMouseOut={(e) => e.currentTarget.style.filter = 'none'}
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Relaxed-filter notice */}
      {!market.loading && !market.error && searchMeta.relaxedFilters && market.jobs?.length > 0 && (
        <div style={{
          margin: '1.5rem 0 0.5rem',
          padding: '0.9rem 1.2rem',
          border: '1px solid #ca8a04',
          borderRadius: '8px',
          background: 'rgba(202,138,4,0.08)',
          color: '#ca8a04',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.7rem',
          fontSize: '0.88rem',
          lineHeight: '1.5'
        }}>
          <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>⚠️</span>
          <span>
            <strong>Filters partially applied.</strong>{' '}
            No jobs matched{' '}
            {searchMeta.appliedFilters.locations?.length > 0 && (
              <strong>{searchMeta.appliedFilters.locations.join(', ')}</strong>
            )}
            {searchMeta.appliedFilters.workModes?.length > 0 && (
              <>{' '}+{' '}<strong>{searchMeta.appliedFilters.workModes.join('/')}</strong></>
            )}
            {' '}in our current data sources (which are primarily remote job boards).
            Showing the <strong>best available matches</strong> from a broader search instead.
            For India onsite roles, try <a href="https://naukri.com" target="_blank" rel="noopener noreferrer" style={{ color: '#eab308', textDecoration: 'underline' }}>Naukri</a> or{' '}
            <a href="https://internshala.com" target="_blank" rel="noopener noreferrer" style={{ color: '#eab308', textDecoration: 'underline' }}>Internshala</a>.
          </span>
        </div>
      )}

      {market.jobs?.length > 0 && (
        <JobMatchTable 
          jobs={market.jobs} 
          loading={market.loading} 
          error={market.error} 
          analysisData={analysis}
        />
      )}
    </div>
  );
}
