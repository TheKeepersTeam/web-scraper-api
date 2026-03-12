"""
Usage Routes - Usage statistics
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime
import hashlib

usage_bp = Blueprint('usage', __name__, url_prefix='/api')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@usage_bp.route('/usage', methods=['GET'])
def get_usage():
    """Get usage statistics for an API key"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    conn = get_db()
    
    # Get key info
    key_info = conn.execute(
        'SELECT name, plan, requests_limit, requests_used, created_at, last_used_at FROM api_keys WHERE key_hash = ?',
        (key_hash,)
    ).fetchone()
    
    if not key_info:
        conn.close()
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get recent requests
    recent = conn.execute(
        'SELECT url, status, response_time_ms, timestamp FROM requests WHERE key_hash = ? ORDER BY timestamp DESC LIMIT 50',
        (key_hash,)
    ).fetchall()
    
    # Get stats
    stats = conn.execute(
        'SELECT COUNT(*) as total, AVG(response_time_ms) as avg_time FROM requests WHERE key_hash = ?',
        (key_hash,)
    ).fetchone()
    
    conn.close()
    
    return jsonify({
        'key': {
            'name': key_info['name'],
            'plan': key_info['plan'],
            'requests_limit': key_info['requests_limit'],
            'requests_used': key_info['requests_used'],
            'requests_remaining': key_info['requests_limit'] - key_info['requests_used'],
            'created_at': key_info['created_at'],
            'last_used_at': key_info['last_used_at']
        },
        'stats': {
            'total_requests': stats['total'],
            'avg_response_time_ms': round(stats['avg_time'] or 0, 2)
        },
        'recent_requests': [dict(r) for r in recent]
    })


@usage_bp.route('/stats', methods=['GET'])
def global_stats():
    """Get global API statistics (admin only in production)"""
    conn = get_db()
    
    total_keys = conn.execute('SELECT COUNT(*) as count FROM api_keys').fetchone()['count']
    total_requests = conn.execute('SELECT COUNT(*) as count FROM requests').fetchone()['count']
    avg_time = conn.execute('SELECT AVG(response_time_ms) as avg FROM requests').fetchone()['avg']
    
    # Requests by status
    by_status = conn.execute(
        'SELECT status, COUNT(*) as count FROM requests GROUP BY status'
    ).fetchall()
    
    # Requests by plan
    by_plan = conn.execute('''
        SELECT k.plan, COUNT(r.id) as count 
        FROM api_keys k 
        LEFT JOIN requests r ON k.key_hash = r.key_hash 
        GROUP BY k.plan
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'total_keys': total_keys,
        'total_requests': total_requests,
        'avg_response_time_ms': round(avg_time or 0, 2),
        'by_status': {r['status']: r['count'] for r in by_status},
        'by_plan': {r['plan']: r['count'] for r in by_plan}
    })