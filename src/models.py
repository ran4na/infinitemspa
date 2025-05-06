from flask import Flask, current_app, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt

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
    page_num : int = db.Column(db.Integer, primary_key=True)
    page_title : str = db.Column(db.String, nullable=False)
    panel_file : int = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False) # points to upload ID
    page_text : str = db.Column(db.String)
    page_redir : int = db.Column(db.Integer, db.ForeignKey('page.page_num'), default=None) # to handle page deletions
    uploader_ip_hash : str = db.Column(db.String, nullable=False) # uploader ident
    
    def to_dict(self):
        return {
            "page_num": self.page_num,
            "page_title": self.page_title,
            "panel_path": self.panel_file,
            "page_text": self.page_text,
            "page_redir": self.page_redir
        }

# Holds image filenames and hashes
class Image(db.Model):
    id : int = db.Column(db.Integer, primary_key=True)
    image_filename : str = db.Column(db.String, nullable=False) # only filename, so path is portable.
    image_hash : str = db.Column(db.String, unique=True) # to check for duplicate files
    
    
# List of banned user IP hashes
class IpBan(db.Model):
    id : int = db.Column(db.Integer, primary_key=True)
    ip_hash : str = db.Column(db.String, unique=True)