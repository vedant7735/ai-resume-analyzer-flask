import CareerSubNav from '../components/CareerSubNav.jsx';
import PathsSubView       from './career/PathsSubView.jsx';
import GraphSubView       from './career/GraphSubView.jsx';
import CompetitiveSubView from './career/CompetitiveSubView.jsx';

/**
 * CareerView — wrapper that renders CareerSubNav + the active sub-view.
 * Sub-nav is also rendered here (not in App) so it stays tied to this view.
 */
export default function CareerView({
  career,
  resume,
  activeCareerSubView,
  dispatch,
}) {
  function handleSubNav(id) {
    dispatch({ type: 'SET_ACTIVE_CAREER_SUB_VIEW', payload: id });
  }

  const candidateName = resume?.identity?.name ?? 'You';

  return (
    <>
      <CareerSubNav
        activeSubView={activeCareerSubView}
        onNavigate={handleSubNav}
      />

      <div className="career-view">
        {activeCareerSubView !== 'graph' && (
          <div className="career-view-header">
            <h1 className="dashboard-title">
              <span className="title-heavy">CAREER</span>{' '}
              <span className="title-italic">Intelligence</span>
            </h1>
            <p className="candidate-name">{candidateName}</p>
          </div>
        )}

        {activeCareerSubView === 'paths' && (
          <PathsSubView paths={career.paths} />
        )}

        {activeCareerSubView === 'graph' && (
          <GraphSubView
            graphData={career.graphData}
            candidateName={candidateName}
          />
        )}

        {activeCareerSubView === 'competitive' && (
          <CompetitiveSubView competitiveAnalysis={career.competitiveAnalysis} />
        )}
      </div>
    </>
  );
}
