# Caching Service
# This service will handle caching and loading analysis results to save on API usage.
import os
import json
import hashlib


def get_file_hash(filepath):
    """Generate SHA256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def get_cached_analysis(file_hash, cache_folder='cache'):
    """Get cached analysis if exists"""
    
    os.makedirs(cache_folder, exist_ok=True)
    cache_file = os.path.join(cache_folder, f"{file_hash}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None


def save_to_cache(file_hash, data, cache_folder='cache'):
    """Save analysis to cache"""
    
    os.makedirs(cache_folder, exist_ok=True)
    cache_file = os.path.join(cache_folder, f"{file_hash}.json")
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)