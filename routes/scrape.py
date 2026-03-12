"""
Scrape Routes - Main scraping endpoint
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, jsonify, request
from utils.scraper import scraper
import sqlite3
from datetime import datetime
import hashlib

scrape_bp = Blueprint('scrape', __name__, url_prefix='/api')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            plan TEXT DEFAULT 'free',
            requests_limit INTEGER DEFAULT 100,
            requests_used INTEGER DEFAULT 0,
            created_at TEXT,
            last_used_at TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT,
            url TEXT,
            status TEXT,
            response_time_ms INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Initialize DB on import
init_db()


def validate_api_key(api_key):
    """Validate API key and return key info"""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM api_keys WHERE key_hash = ?', (key_hash,)
    ).fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def check_rate_limit(key_info):
    """Check if key has requests remaining"""
    return key_info['requests_used'] < key_info['requests_limit']


def increment_usage(key_hash):
    """Increment usage counter for key"""
    conn = get_db()
    conn.execute(
        'UPDATE api_keys SET requests_used = requests_used + 1, last_used_at = ? WHERE key_hash = ?',
        (datetime.utcnow().isoformat(), key_hash)
    )
    conn.commit()
    conn.close()


def log_request(key_hash, url, status, response_time_ms):
    """Log request for analytics"""
    conn = get_db()
    conn.execute(
        'INSERT INTO requests (key_hash, url, status, response_time_ms, timestamp) VALUES (?, ?, ?, ?, ?)',
        (key_hash, url, status, response_time_ms, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


@scrape_bp.route('/scrape', methods=['POST'])
def scrape():
    """Main scraping endpoint"""
    import time
    
    # Get API key from header
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required. Include X-API-Key header.'}), 401
    
    # Validate key
    key_info = validate_api_key(api_key)
    if not key_info:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Check rate limit
    if not check_rate_limit(key_info):
        return jsonify({
            'error': 'Rate limit exceeded',
            'limit': key_info['requests_limit'],
            'used': key_info['requests_used']
        }), 429
    
    # Get URL and options
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL. Must start with http:// or https://'}), 400
    
    # Options
    options = {
        'include_links': data.get('include_links', False),
        'include_images': data.get('include_images', False),
        'text_selector': data.get('text_selector'),
        'selectors': data.get('selectors')
    }
    
    # Scrape
    start_time = time.time()
    try:
        result = scraper.smart_extract(url, options)
        status = 'success'
    except Exception as e:
        status = 'error'
        result = {'error': str(e)}
    
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Log and increment usage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    increment_usage(key_hash)
    log_request(key_hash, url, status, response_time_ms)
    
    # Add usage info to response
    result['_meta'] = {
        'requests_remaining': key_info['requests_limit'] - key_info['requests_used'] - 1,
        'response_time_ms': response_time_ms
    }
    
    if status == 'error':
        return jsonify(result), 500
    
    return jsonify(result)