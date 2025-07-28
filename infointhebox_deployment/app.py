import os
from flask import Flask, render_template, abort, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask app for InfoInTheBox
infointhebox_app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')

infointhebox_app.secret_key = os.environ.get("SESSION_SECRET")
infointhebox_app.wsgi_app = ProxyFix(infointhebox_app.wsgi_app, x_proto=1, x_host=1)

# Database configuration - use same database as main app
infointhebox_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
infointhebox_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
infointhebox_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Initialize database
db = SQLAlchemy(infointhebox_app, model_class=Base)

# Import models to ensure tables exist
with infointhebox_app.app_context():
    # Import shared models
    import models  # noqa: F401
    db.create_all()
    logging.info("InfoInTheBox database tables ready")

# Import routes after app is configured
from models import SharedAdvertiser, CompanyProfile

@infointhebox_app.route('/')
def index():
    """Homepage showing all active company profiles"""
    # Get all company profiles with active status
    profiles = CompanyProfile.query.filter_by(active=True).order_by(CompanyProfile.company_name).all()
    
    return render_template('index.html', profiles=profiles)

@infointhebox_app.route('/profile/<slug>')
def company_profile(slug):
    """Individual company profile page"""
    profile = CompanyProfile.query.filter_by(slug=slug, active=True).first()
    if not profile:
        abort(404)
    
    return render_template('profile.html', profile=profile)

@infointhebox_app.route('/search')
def search():
    """Search company profiles"""
    query = request.args.get('q', '').strip()
    profiles = []
    
    if query:
        profiles = CompanyProfile.query.filter(
            CompanyProfile.active == True,
            CompanyProfile.company_name.ilike(f'%{query}%') |
            CompanyProfile.description.ilike(f'%{query}%')
        ).order_by(CompanyProfile.company_name).all()
    
    return render_template('search.html', profiles=profiles, query=query)

@infointhebox_app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@infointhebox_app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == "__main__":
    infointhebox_app.run(host="0.0.0.0", port=5000, debug=True)