import os
import json
import hashlib
import shutil


def get_file_hash(filepath):
    """Generate SHA256 hash of file content"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def get_object_hash(obj):
    """Generate hash from JSON object (for v2/v3 caching)"""
    json_str = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


# ===== LEVEL 1: ANALYZED RESUME CACHE (v2) =====

def get_cached_analysis(file_hash, cache_folder='cache'):
    """Get cached v2 (analyzed resume) by PDF hash"""
    
    os.makedirs(cache_folder, exist_ok=True)
    cache_file = os.path.join(cache_folder, f"v2_{file_hash}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None


def save_to_cache(file_hash, data, cache_folder='cache'):
    """Save v2 (analyzed resume) to cache"""
    
    os.makedirs(cache_folder, exist_ok=True)
    cache_file = os.path.join(cache_folder, f"v2_{file_hash}.json")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


# ===== LEVEL 2: ENHANCED RESUME CACHE (v3) =====

def get_cached_enhancement(v2_object, cache_folder='cache'):
    """Get cached v3 (enhanced resume) by v2 hash"""
    
    os.makedirs(cache_folder, exist_ok=True)
    v2_hash = get_object_hash(v2_object)
    cache_file = os.path.join(cache_folder, f"v3_{v2_hash}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached = json.load(f)
            print(f"[Cache] [OK] v3 cache hit: {v2_hash[:8]}")
            return cached
    
    return None


def save_enhancement_to_cache(v2_object, v3_object, cache_folder='cache'):
    """Save v3 (enhanced resume) to cache"""
    
    os.makedirs(cache_folder, exist_ok=True)
    v2_hash = get_object_hash(v2_object)
    cache_file = os.path.join(cache_folder, f"v3_{v2_hash}.json")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(v3_object, f, indent=2)
    
    print(f"[Cache] [OK] v3 saved: {v2_hash[:8]}")


# ===== LEVEL 3: RENDERED FILES CACHE (.tex/.pdf) =====

def get_cached_render(v3_object, cache_folder='cache'):
    """
    Get cached .tex/.pdf files by v3 hash.
    Returns dict with tex_path, pdf_path, file_id or None.
    """
    
    os.makedirs(cache_folder, exist_ok=True)
    v3_hash = get_object_hash(v3_object)
    metadata_file = os.path.join(cache_folder, f"render_{v3_hash}.json")
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
            # Verify files still exist
            tex_path = metadata.get('tex_path')
            pdf_path = metadata.get('pdf_path')
            file_id = metadata.get('file_id')

            if not pdf_path and file_id and tex_path:
                inferred_pdf_path = os.path.join(
                    os.path.dirname(tex_path),
                    f"resume_{file_id}.pdf"
                )
                if os.path.exists(inferred_pdf_path):
                    pdf_path = inferred_pdf_path
            
            if tex_path and os.path.exists(tex_path):
                print(f"[Cache] [OK] Render cache hit: {v3_hash[:8]}")
                return {
                    'tex_path': tex_path,
                    'pdf_path': pdf_path if pdf_path and os.path.exists(pdf_path) else None,
                    'file_id': file_id,
                    'tex_filename': os.path.basename(tex_path),
                    'pdf_filename': os.path.basename(pdf_path) if pdf_path and os.path.exists(pdf_path) else None
                }
    
    return None


def save_render_to_cache(v3_object, tex_path, pdf_path, file_id, cache_folder='cache'):
    """Save .tex/.pdf file metadata to cache"""
    
    os.makedirs(cache_folder, exist_ok=True)
    v3_hash = get_object_hash(v3_object)
    metadata_file = os.path.join(cache_folder, f"render_{v3_hash}.json")
    
    metadata = {
        'v3_hash': v3_hash,
        'file_id': file_id,
        'tex_path': tex_path,
        'pdf_path': pdf_path
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[Cache] [OK] Render saved: {v3_hash[:8]}")


def clear_cache(cache_folder='cache'):
    """Clear all cached files (admin/maintenance)"""
    
    if not os.path.exists(cache_folder):
        return
    
    for filename in os.listdir(cache_folder):
        filepath = os.path.join(cache_folder, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
    
    print("[Cache] [OK] All cache cleared")

# ===== LEVEL 4: JOB SEARCH CACHE =====

def get_cached_jobs(analysis_data, filters, cache_folder='cache'):
    """Get cached jobs by analysis data and filters hash.
    
    Returns a dict with keys: jobs, relaxed_filters, applied_filters.
    Old cache files that stored a raw list are transparently normalised.
    """
    os.makedirs(cache_folder, exist_ok=True)
    combined = {"analysis": analysis_data, "filters": filters}
    analysis_hash = get_object_hash(combined)
    cache_file = os.path.join(cache_folder, f"jobs_{analysis_hash}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached = json.load(f)
            print(f"[Cache] [OK] Jobs cache hit: {analysis_hash[:8]}")
            # Normalise legacy list-shaped cache to new dict shape
            if isinstance(cached, list):
                cached = {'jobs': cached, 'relaxed_filters': False, 'applied_filters': {}}
            return cached
            
    return None

def save_jobs_to_cache(analysis_data, filters, jobs, cache_folder='cache'):
    """Save jobs to cache"""
    os.makedirs(cache_folder, exist_ok=True)
    combined = {"analysis": analysis_data, "filters": filters}
    analysis_hash = get_object_hash(combined)
    cache_file = os.path.join(cache_folder, f"jobs_{analysis_hash}.json")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2)
        
    print(f"[Cache] [OK] Jobs saved: {analysis_hash[:8]}")
