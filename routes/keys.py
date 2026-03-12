"""
API Keys Routes - Key management
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime
import hashlib
import secrets

keys_bp = Blueprint('keys', __name__, url_prefix='/api')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_api_key():
    """Generate a secure API key"""
    return f"wsa_{secrets.token_hex(16)}"


@keys_bp.route('/keys', methods=['GET'])
def list_keys():
    """List all API keys (admin endpoint - protect in production!)"""
    # In production, require admin auth
    admin_key = request.headers.get('X-Admin-Key')
    
    conn = get_db()
    keys = conn.execute(
        'SELECT name, email, plan, requests_limit, requests_used, created_at, last_used_at FROM api_keys'
    ).fetchall()
    conn.close()
    
    return jsonify({
        'keys': [dict(k) for k in keys]
    })


@keys_bp.route('/keys', methods=['POST'])
def create_key():
    """Create a new API key"""
    data = request.get_json()
    
    name = data.get('name', 'Unnamed')
    email = data.get('email', '')
    plan = data.get('plan', 'free')
    
    # Plan limits
    plan_limits = {
        'free': 100,
        'starter': 5000,
        'pro': 50000,
        'enterprise': 1000000
    }
    
    # Generate key
    api_key = generate_api_key()
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO api_keys (key_hash, name, email, plan, requests_limit, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (key_hash, name, email, plan, plan_limits.get(plan, 100), datetime.utcnow().isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Key already exists'}), 409
    finally:
        conn.close()
    
    return jsonify({
        'message': 'API key created',
        'api_key': api_key,  # Only shown once!
        'name': name,
        'plan': plan,
        'requests_limit': plan_limits.get(plan, 100)
    }), 201


@keys_bp.route('/keys/<key_hash>', methods=['DELETE'])
def delete_key(key_hash):
    """Delete an API key"""
    conn = get_db()
    conn.execute('DELETE FROM api_keys WHERE key_hash = ?', (key_hash,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Key deleted'})