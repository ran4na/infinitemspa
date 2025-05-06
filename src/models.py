from flask import Flask, current_app, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

models = Blueprint('models', __name__)

def create_db(app : Flask):
    with app.app_context():
        db.create_all()

# Enable FKs just in case
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
    
# PAGES
class Page(db.Model):
    page_num : int = db.Column(db.Integer, primary_key=True, index=True)
    page_title : str = db.Column(db.String, nullable=False)
    panel_file_id : int = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False) # points to upload ID
    page_text : str = db.Column(db.String)
    uploader_ip_hash : str = db.Column(db.String, nullable=False) # uploader ident
    deleted : bool = db.Column(db.Boolean, default=False, index=True)
    panel_image = db.relationship("Image")
    
    
    def to_dict(self):
        return {
            "page_num": self.page_num,
            "page_title": self.page_title,
            "panel_filename": self.panel_image.image_filename,
            "page_text": self.page_text
        }
        
    def to_admin_dict(self):
        return {
            "page_num": self.page_num,
            "page_title": self.page_title,
            "panel_file_id": self.panel_file_id,
            "panel_filename": self.panel_image.image_filename,
            "page_text": self.page_text,
            "page_uploader": self.uploader_ip_hash,
            "deleted": self.deleted
        }
        
    def soft_delete_page(self):
        self.page_title = ""
        self.panel_image.soft_delete()
        self.page_text = ""
        self.deleted = True
    
    def next_undeleted_page(self):
        next_undeleted = Page.query.filter(Page.deleted == False, Page.page_num > self.page_num).order_by(Page.page_num.asc()).first()
        if next_undeleted is not None:
            return next_undeleted.page_num
        return None
    
    # returns latest page
    def get_newest_page():
        pages = Page.query.order_by(Page.page_num.desc()).all()
        
        if not pages:
            return None
        
        return pages[0]
    

# Holds image filenames and hashes
class Image(db.Model):
    id : int = db.Column(db.Integer, primary_key=True)
    image_filename : str = db.Column(db.String, nullable=False) # only filename, so path is portable.
    image_hash : str = db.Column(db.String, unique=True) # to check for duplicate files
    deleted : bool = db.Column(db.Boolean, default=False, index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "image_filename": self.image_filename,
            "image_hash": self.image_hash,
            "deleted": self.deleted
        }
    
    # remove image, but keep hash.
    def soft_delete(self):
        # delete image from uploads
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], self.image_filename))
        self.image_filename = "[DELETED]"
        self.deleted = True
        db.session.commit()
    
# List of banned user IP hashes
class IpBan(db.Model):
    id : int = db.Column(db.Integer, primary_key=True)
    ip_hash : str = db.Column(db.String, unique=True, index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "ip_hash": self.ip_hash
        }
    
# reserved for admin
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable = False)
    
    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        
    def test_login(uname, pwd):
        if User.query.filter_by(username=uname).count() > 0:
            user = User.query.filter_by(username=uname).first()
            if bcrypt.check_password_hash(user.password, pwd):
                return user
            else:
                return None
    def get_id(self):
        return self.user_id