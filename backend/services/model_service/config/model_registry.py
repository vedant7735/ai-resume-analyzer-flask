# services/model_service/model_registry.py

MODEL_REGISTRY = {


    # # =============================
    # # Single LLM Call
    # # =============================

    "resume_analyzer_and_enhancer": {
        "provider": "openai",
        "model": "gpt-4o-mini",

        "capabilities": {
            "vision": False,
            "json_mode": True,
            "streaming": True
        },

        "temperature": 0.1,
        "max_tokens": 4000
    }
}

# job search model

MODEL_REGISTRY_JOB_SEARCH = {
    "job_search": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b",

        "capabilities": {
            "vision": False,
            "json_mode": True,
            "streaming": True
        },

        "temperature": 0.1,
        "max_tokens": 4000
    }
}

    # # ==============================
    # # Resume Analysis
    # # ==============================

    # "resume_analysis": {
    #     "provider": "openai",
    #     "model": "gpt-4.1-mini",

    #     "capabilities": {
    #         "vision": False,
    #         "json_mode": True,
    #         "streaming": True
    #     },

    #     "temperature": 0.1,
    #     "max_tokens": 4000
    # },

    # # ==============================
    # # Resume Enhancement
    # # ==============================

    # "resume_enhancement": {
    #     "provider": "openai",
    #     "model": "gpt-4.1-mini",

    #     "capabilities": {
    #         "vision": False,
    #         "json_mode": True,
    #         "streaming": True
    #     },

    #     "temperature": 0.3,
    #     "max_tokens": 4000
    # },

    # # ==============================
    # # Multimodal Extraction
    # # ==============================

    # "multimodal_extraction": {
    #     "provider": "openai",
    #     "model": "gpt-4o-mini",

    #     "capabilities": {
    #         "vision": True,
    #         "json_mode": True,
    #         "streaming": False
    #     },

    #     "temperature": 0.0,
    #     "max_tokens": 3000
    # },

    # # ==============================
    # # ATS Classification
    # # ==============================

    # "ats_classifier": {
    #     "provider": "openai",
    #     "model": "gpt-4.1-nano",

    #     "capabilities": {
    #         "vision": False,
    #         "json_mode": True,
    #         "streaming": False
    #     },

    #     "temperature": 0.0,
    #     "max_tokens": 1200
    # }
