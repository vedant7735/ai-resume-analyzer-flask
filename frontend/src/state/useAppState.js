import { useReducer } from 'react';

// ─── Initial State ─────────────────────────────────────────────────────────────

const initialState = {
  /** "idle" | "processing" | "ready" */
  stage: 'idle',

  /** Which top-level view is shown */
  activeView: 'upload',

  /** Which career sub-view is shown */
  activeCareerSubView: 'paths',

  upload: {
    filename: '',
    fileHash: '',
  },

  extraction: {
    rawText: '',
    baseLatex: '',
  },

  resume: {
    identity: {},
    experience: [],
    projects: [],
    education: [],
    skills: {},
    workshops: [],
    jd_match: null,
  },

  analysis: {
    professionalSummary: '',
    strengths: [],
    improvements: [],
    score: {},
    atsKeywords: [],
    recommendedFor: [],
  },

  career: {
    paths: [],
    competitiveAnalysis: {},
    graphData: {},
  },

  editor: {
    latexCode: '',
    compiledPdfUrl: '',
    hasUnsavedChanges: false,
    fileId: null,
    downloadBasename: 'candidate_resume_ai_pack',
    isPdfAvailable: false,
  },
  
  market: {
    jobs: [],
    loading: false,
    error: null,
  }
};

// ─── Reducer ───────────────────────────────────────────────────────────────────

function appReducer(state, action) {
  switch (action.type) {

    case 'SET_PROCESSING':
      return {
        ...state,
        stage: 'processing',
        upload: {
          filename: action.payload.filename,
          fileHash: '',
        },
      };

    case 'SET_READY': {
      const data = action.payload;

      // Career paths — support both nested (data.career.paths) and
      // top-level (data.career_paths) shapes from the LLM
      const paths = data.career?.paths
                 ?? data.career_paths
                 ?? [];

      // Competitive analysis — same dual-location fallback
      const competitiveAnalysis = data.career?.competitive_analysis
                               ?? data.competitive_analysis
                               ?? {};

      const graphData = buildGraphData(paths);

      // Analysis fields — support both nested and top-level
      const analysisBlock = data.analysis ?? {};

      return {
        ...state,
        stage: 'ready',
        activeView: 'analysis',

        upload: {
          filename: state.upload.filename,
          fileHash: data.file_hash ?? '',
        },

        resume: {
          identity:   data.identity   ?? {},
          experience: data.experience ?? [],
          projects:   data.projects   ?? [],
          education:  data.education  ?? [],
          skills:     data.skills     ?? {},
          workshops:  data.workshops  ?? [],
          jd_match:   data.jd_match   ?? null,
        },

        analysis: {
          professionalSummary: analysisBlock.professional_summary ?? data.professional_summary ?? '',
          strengths:           analysisBlock.strengths            ?? data.strengths            ?? [],
          improvements:        analysisBlock.improvements         ?? data.improvements         ?? [],
          score:               analysisBlock.score                ?? data.score                ?? {},
          atsKeywords:         analysisBlock.ats_keywords         ?? data.ats_keywords         ?? [],
          recommendedFor:      analysisBlock.recommended_for      ?? data.recommended_for      ?? [],
        },

        career: {
          paths,
          competitiveAnalysis,
          graphData,
        },
      };
    }

    case 'SET_ACTIVE_VIEW':
      return {
        ...state,
        activeView: action.payload,
      };

    case 'SET_ACTIVE_CAREER_SUB_VIEW':
      return {
        ...state,
        activeCareerSubView: action.payload,
      };

    case 'SET_EDITOR':
      return {
        ...state,
        editor: {
          ...state.editor,
          ...action.payload,
        },
      };

    case 'SET_MARKET_STATE':
      return {
        ...state,
        market: {
          ...state.market,
          ...action.payload,
        },
      };

    case 'RESET':
      return { ...initialState };

    default:
      return state;
  }
}

// ─── Helper: Build graph data from career paths ────────────────────────────────

/**
 * Converts a flat list of career paths into a simple graph structure
 * grouped by time_to_ready buckets: "current", "1yr", "3yr".
 */
function buildGraphData(paths) {
  const current   = [];
  const oneYear   = [];
  const threeYear = [];

  paths.forEach((p) => {
    const t = (p.time_to_ready ?? '').toLowerCase();
    if (t.includes('now') || t.includes('ready') || t.includes('immediate') || t.includes('0') || t === '') {
      current.push(p);
    } else if (t.includes('1') || t.includes('one') || t.includes('6 month')) {
      oneYear.push(p);
    } else {
      threeYear.push(p);
    }
  });

  return { current, oneYear, threeYear };
}

// ─── Hook ──────────────────────────────────────────────────────────────────────

export function useAppState() {
  const [state, dispatch] = useReducer(appReducer, initialState);
  return { state, dispatch };
}
