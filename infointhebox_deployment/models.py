from datetime import datetime
from app import db
from flask_login import UserMixin
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash
import re

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationship with articles
    articles = db.relationship('Article', backref='author', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a secure reset token"""
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        # Token expires in 24 hours
        from datetime import timedelta
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify if reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with articles
    articles = db.relationship('Article', backref='category', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(200))
    video_url = db.Column(db.String(500))
    video_thumbnail = db.Column(db.String(200))
    is_video = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    read_time = db.Column(db.Integer, default=1)  # minutes
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        self.slug = slugify(self.title)
        
        # Ensure uniqueness
        counter = 1
        original_slug = self.slug
        while Article.query.filter_by(slug=self.slug).filter(Article.id != self.id).first():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
    
    def calculate_read_time(self):
        """Calculate estimated read time based on content"""
        if self.content:
            word_count = len(re.findall(r'\w+', self.content))
            self.read_time = max(1, round(word_count / 200))  # 200 words per minute
    
    def get_video_embed_url(self):
        """Convert video URL or embed code to embeddable format"""
        if not self.video_url:
            return None
        
        # Import here to avoid circular imports
        from utils import extract_video_id_from_embed
        
        # Extract video info from URL or embed code
        video_info = extract_video_id_from_embed(self.video_url)
        
        if video_info:
            if video_info['platform'] == 'youtube':
                return f"https://www.youtube.com/embed/{video_info['video_id']}"
            elif video_info['platform'] == 'vimeo':
                return f"https://player.vimeo.com/video/{video_info['video_id']}"
        
        # If already a proper embed URL, return as-is
        if 'youtube.com/embed/' in self.video_url or 'player.vimeo.com/video/' in self.video_url:
            return self.video_url
        
        return self.video_url
    
    def get_video_id(self):
        """Extract just the video ID for thumbnail generation"""
        from utils import extract_video_id_from_embed
        
        video_info = extract_video_id_from_embed(self.video_url)
        return video_info['video_id'] if video_info else None

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slot_position = db.Column(db.String(50), nullable=False)  # 'sidebar-1', 'sidebar-2', 'sidebar-3', 'banner-top'
    adrotate_url = db.Column(db.Text, nullable=False)  # The full adrotate iframe URL
    fallback_image = db.Column(db.String(200))  # Optional fallback image
    fallback_link = db.Column(db.String(500))  # Optional fallback link
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# New models for SharedAdvertising.ca
class SharedAdvertiser(UserMixin, db.Model):
    """User accounts for SharedAdvertising.ca"""
    __tablename__ = 'shared_advertisers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=True)  # Changed from is_active to avoid conflict
    reset_token = db.Column(db.String(100), nullable=True)  # For password reset
    reset_token_expires = db.Column(db.DateTime, nullable=True)  # Token expiration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shared_ads = db.relationship('SharedAd', backref='advertiser', lazy=True)
    company_profiles = db.relationship('CompanyProfile', backref='advertiser', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a secure reset token"""
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        # Token expires in 24 hours
        from datetime import datetime, timedelta
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify if reset token is valid and not expired"""
        from datetime import datetime
        if not self.reset_token or not self.reset_token_expires:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None

class SharedAd(db.Model):
    """User-created ads for display on lovethenorth.ca"""
    __tablename__ = 'shared_ads'
    id = db.Column(db.Integer, primary_key=True)
    ad_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)  # Internal notes for the advertiser
    image_filename = db.Column(db.String(200), nullable=False)  # 320x180px image
    image_path = db.Column(db.String(500), nullable=False)
    active = db.Column(db.Boolean, default=True)
    clicks = db.Column(db.Integer, default=0)  # Track clicks
    impressions = db.Column(db.Integer, default=0)  # Track views
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    advertiser_id = db.Column(db.Integer, db.ForeignKey('shared_advertisers.id'), nullable=False)
    company_profile_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=True)

class CompanyProfile(db.Model):
    """Company profiles for infointhebox.ca"""
    __tablename__ = 'company_profiles'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)  # URL-friendly version
    description = db.Column(db.Text, nullable=False)
    web_url = db.Column(db.String(500))
    facebook_url = db.Column(db.String(500))
    instagram_url = db.Column(db.String(500))
    pinterest_url = db.Column(db.String(500))
    active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)  # Track profile views
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    advertiser_id = db.Column(db.Integer, db.ForeignKey('shared_advertisers.id'), nullable=False)
    
    # Relationships
    shared_ads = db.relationship('SharedAd', backref='company_profile', lazy=True)
    
    def generate_slug(self):
        """Generate URL-friendly slug from company name"""
        self.slug = slugify(self.company_name)
        
        # Ensure uniqueness
        counter = 1
        original_slug = self.slug
        while CompanyProfile.query.filter_by(slug=self.slug).filter(CompanyProfile.id != self.id).first():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
