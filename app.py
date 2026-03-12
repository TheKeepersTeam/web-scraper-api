"""
Web Scraper API - Turn websites into structured JSON
Main Flask Application
"""
import os
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'scraper.db')
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Register routes
    from routes.scrape import scrape_bp
    from routes.keys import keys_bp
    from routes.usage import usage_bp
    
    app.register_blueprint(scrape_bp)
    app.register_blueprint(keys_bp)
    app.register_blueprint(usage_bp)
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'Web Scraper API'})
    
    # Home page
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Web Scraper API',
            'version': '1.0.0',
            'endpoints': {
                'scrape': 'POST /api/scrape',
                'keys': 'GET/POST /api/keys',
                'usage': 'GET /api/usage',
                'health': 'GET /health'
            }
        })
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5556))
    app.run(host='0.0.0.0', port=port, debug=True)