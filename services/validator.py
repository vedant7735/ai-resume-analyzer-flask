import uuid
from jsonschema import validate, ValidationError

RESUME_SCHEMA = {
    "type": "object",
    "required": [
        "resume_id",
        "schema_version",
        "identity",
        "experience",
        "projects",
        "education",
        "skills"
    ],

    "properties": {

        "resume_id": {
            "type": "string"
        },

        "schema_version": {
            "type": "string"
        },

        "identity": {
            "type": "object",
            "required": ["name", "email"],

            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "linkedin": {"type": "string"},
                "github": {"type": "string"},
                "portfolio": {"type": "string"},
                "location": {"type": "string"}
            }
        },

        "experience": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "duration": {"type": "string"},
                    "type": {"type": "string"},

                    "bullets": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },

        "projects": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {
                    "title": {"type": "string"},
                    "type": {"type": "string"},
                    "year": {"type": ["string", "integer"]},

                    "tech_stack": {
                        "type": "array",
                        "items": {"type": "string"}
                    },

                    "bullets": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },

        "education": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {
                    "degree": {"type": "string"},
                    "major": {"type": "string"},
                    "institution": {"type": "string"},
                    "graduation_year": {"type": ["string", "integer"]},
                    "gpa": {"type": ["string", "number"]}
                }
            }
        },

        "skills": {
            "type": "object",

            "properties": {
                "languages": {
                    "type": "array",
                    "items": {"type": "string"}
                },

                "frameworks": {
                    "type": "array",
                    "items": {"type": "string"}
                },

                "tools": {
                    "type": "array",
                    "items": {"type": "string"}
                },

                "domains": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },

        "analysis": {
            "type": "object"
        }
    }
}

def validate_resume_object(resume, schema=RESUME_SCHEMA):
    """Validate resume against schema, attempt auto-repair"""
    try:
        validate(instance=resume, schema=schema)
        return resume, None
    except ValidationError as e:
        # Auto-repair common issues
        repaired = dict(resume)
        
        # Ensure required fields exist
        repaired.setdefault("resume_id", str(uuid.uuid4()))
        repaired.setdefault("schema_version", "1.0")
        repaired.setdefault("identity", {})
        repaired["identity"].setdefault("name", "")
        repaired["identity"].setdefault("email", "")
        
        # Validate again
        try:
            validate(instance=repaired, schema=schema)
            return repaired, f"Auto-repaired: {e.message}"
        except ValidationError:
            return resume, str(e)