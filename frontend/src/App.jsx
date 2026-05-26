import React, { useState, useEffect } from 'react';
import FloatingNavbar from './components/FloatingNavbar.jsx';
import ThemeToggle    from './components/ThemeToggle.jsx';
import UploadView     from './views/UploadView.jsx';
import AnalysisView   from './views/AnalysisView.jsx';
import CareerView     from './views/CareerView.jsx';
import EditorView     from './views/EditorView.jsx';
import FindJobsView   from './views/FindJobsView.jsx';
import { useAppState } from './state/useAppState.js';

export default function App() {
  const { state, dispatch } = useAppState();
  
  // Theme state: initialized from localStorage with fallback to light
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  // Apply theme class/attribute on root element when it changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }

  function navigate(view) {
    dispatch({ type: 'SET_ACTIVE_VIEW', payload: view });
  }

  return (
    <>
      {/* Theme Toggle Button in top-right */}
      <ThemeToggle theme={theme} onToggle={toggleTheme} />

      {/* Floating navbar — only visible after upload */}
      {state.stage === 'ready' && (
        <FloatingNavbar
          activeView={state.activeView}
          stage={state.stage}
          onNavigate={navigate}
        />
      )}

      {/* Main content — top padding keeps content below the navbar pill */}
      <main style={{ paddingTop: state.stage === 'ready' && state.activeView !== 'upload' ? '5rem' : 0 }}>
        {state.activeView === 'upload' && (
          <UploadView dispatch={dispatch} />
        )}

        {state.activeView === 'analysis' && (
          <AnalysisView
            resume={state.resume}
            analysis={state.analysis}
            onNavigate={navigate}
          />
        )}

        {state.activeView === 'career' && (
          <CareerView
            career={state.career}
            resume={state.resume}
            activeCareerSubView={state.activeCareerSubView}
            dispatch={dispatch}
          />
        )}

        {state.activeView === 'editor' && (
          <EditorView
            resume={state.resume}
            analysis={state.analysis}
            editor={state.editor}
            dispatch={dispatch}
          />
        )}

        {state.activeView === 'jobs' && (
          <FindJobsView
            resume={state.resume}
            analysis={state.analysis}
            market={state.market}
            dispatch={dispatch}
          />
        )}
      </main>
    </>
  );
}
