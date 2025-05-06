from flask import *
from models import *
from werkzeug.datastructures import FileStorage
from typing import Optional
import PIL
import filetype
import imagehash
import os
from flask_login import login_required
from flask import current_app

api = Blueprint('api', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}



# upload page thru page creation form @ new_page.html
@api.route("/create_page", methods=["POST"])
def create_page():
    # dont upload if locked
    if current_app.config["UPLOAD_LOCK"]:
        return jsonify({ "error" : "Uploads are currently locked." })
    
    # Get basic data
    page_number : int = int(request.form.get("page_num"))
    page_title : str = request.form.get("page_title")
    page_panel : Optional[FileStorage] = request.files["panel_img"]
    page_text: str = request.form.get("page_text")
    
    uploader_ip : str = request.remote_addr
    
    if(None in [page_number, page_title, page_panel, uploader_ip]):
        # Error
        return jsonify({ "error" : "Required values are missing." })
    
    # First, check if page is not the newest page + 1, or already exists.
    newest_page : Page = Page.get_newest_page()
    if newest_page is not None:
        if newest_page.page_num + 1 > page_number:
            return jsonify({ "error" : "This page has already been created." })
        elif newest_page.page_num + 1 < page_number:
            return jsonify({ "error" : "This page is too far after the newest page." })
    
    # Test if user is banned
    banned_users = IpBan.query.filter_by(ip_hash=hash(uploader_ip)).first()
    if banned_users is not None:
        return jsonify({ "error" : "You have been restricted from uploading pages." })
    
    # then, attempt to upload the panel
    uploaded_image : Image = upload_panel_file(page_panel)
    # Upload failed
    if uploaded_image is None:
        return jsonify({ "error" : f"Couldn't upload image. \
            Max filesize: {current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)}MB, \
                Valid file types: {', '.join(ALLOWED_EXTENSIONS)}" })

    created_page : Page = Page(
        page_num = page_number,
        page_title = page_title,
        panel_file_id = uploaded_image.id,
        page_text = page_text,
        uploader_ip_hash = hash(uploader_ip),
    )
    
    if created_page is None:
        return jsonify({ "error" : "Could not create page." })

    db.session.add(created_page)
    db.session.commit()
    
    return jsonify({ "success" : f"{page_number}" })

def validate_file(file : FileStorage):
    success: bool = True
    if ('.' not in file.filename) or (file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS):
        return False
    ## check if a valid image
    if not filetype.is_image(file):
        success = False
        
    return success


# Returns a new Image object (or none if the upload failed) for uploaded file
def upload_panel_file(file : FileStorage):
    # check if upload is valid.
    if (file is None) or (not validate_file(file)):
        return None
    
    # hash image to check for duplicates
    file.seek(0)
    image = PIL.Image.open(file)
    
    image_hash = str(imagehash.average_hash(image))
    colliding_img = Image.query.filter_by(image_hash = image_hash).first()
    # collision was found, return that instead
    if colliding_img is not None:
        return colliding_img
    
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    newest_page : Page = Page.get_newest_page()
    if(newest_page is not None):
        new_filename = f'{newest_page.page_num + 1}.{file_extension}'
    else:
        new_filename = f'1.{file_extension}'
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
    
    file.seek(0)
    file.save(output_path)
    
    new_image : Image = Image(
        image_filename=new_filename,
        image_hash = image_hash
    )
    
    db.session.add(new_image)
    db.session.commit()
    
    return new_image

# For admin user
@api.route("/soft_delete_page", methods=["POST"])
@login_required
def soft_delete_page():
    page_number : int = int(request.form.get("page_num"))
    
    if page_number is None:
        return jsonify({ "error" : "Page number is missing." })
    
    # get page
    page : Page = Page.query.filter_by(page_num=page_number).first()
    
    if page is None:
        return jsonify({ "error" : "Page not found." })
    
    # soft delete page
    page.soft_delete_page()
    
    db.session.commit()
    
    return jsonify({ "success" : f"{page_number}" })

@api.route("/get_page_list_admin", methods=["GET"])
@login_required
def get_page_list_admin():
    # get all pages
    pages = Page.query.all()
    
    if not pages:
        return jsonify({ "error" : "No pages found." })
    
    page_list = [page.to_admin_dict() for page in pages]
    
    return jsonify(page_list)

@api.route("/ban_user", methods=["POST"])
@login_required
def ban_user():
    user_ip : str = request.form.get("uploader_ip_hash")
    
    if user_ip is None:
        return jsonify({ "error" : "User IP is missing." })
    
    # check if user is already banned
    banned_user = IpBan.query.filter_by(ip_hash=user_ip).first()
    
    if banned_user is not None:
        return jsonify({ "error" : "User is already banned." })
    
    new_ban = IpBan(
        ip_hash = user_ip
    )
    
    db.session.add(new_ban)
    db.session.commit()
    
    return jsonify({ "success" : f"Banned user {user_ip}" })

@api.route("/get_banned_users", methods=["GET"])
@login_required
def get_banned_users():
    # get all banned users
    banned_users = IpBan.query.all()
    
    if not banned_users:
        return jsonify({ "error" : "No banned users found." })
    
    banned_user_list = [user.to_dict() for user in banned_users]
    
    return jsonify(banned_user_list)

@api.route("/unban_user", methods=["POST"])
@login_required
def unban_user():
    ban_id : str = request.form.get("ban_id")
    
    if ban_id is None:
        return jsonify({ "error" : "ban id is missing." })
    
    # check if user is banned
    banned_user = IpBan.query.filter_by(id=ban_id).first()
    
    if banned_user is None:
        return jsonify({ "error" : "User is not banned." })
    
    db.session.delete(banned_user)
    db.session.commit()
    
    return jsonify({ "success" : f"Unbanned ban {ban_id}" })

@api.route("/soft_delete_image", methods=["POST"])
@login_required
def soft_delete_image():
    image_id : int = int(request.form.get("image_id"))
    
    if image_id is None:
        return jsonify({ "error" : "Image ID is missing." })
    
    # get image
    image : Image = Image.query.filter_by(id=image_id).first()
    
    if image is None:
        return jsonify({ "error" : "Image not found." })
    
    if image.deleted:
        return jsonify({ "error" : "Image is already deleted." })
    
    # soft delete image
    image.soft_delete()
    
    db.session.commit()
    
    return jsonify({ "success" : f"Soft-deleted image {image_id}" })

@api.route("/get_image_list", methods=["GET"])
@login_required
def get_image_list():
    # get all banned users
    images = Image.query.all()
    
    if not images:
        return jsonify({ "error" : "No images found." })
    
    images = [image.to_dict() for image in images]
    
    return jsonify(images)

@api.route("/toggle_upload_lock", methods=["GET"])
@login_required
def toggle_upload_lock():
    # get all banned users
    if(current_app.config["UPLOAD_LOCK"]):
        current_app.config["UPLOAD_LOCK"] = False
    else:
        current_app.config["UPLOAD_LOCK"] = True
    return jsonify({ "locked" : f"{current_app.config['UPLOAD_LOCK']}" })

@api.route("/get_lock_status", methods=["GET"])
@login_required
def get_lock_status():
    return jsonify({ "locked" : f"{current_app.config['UPLOAD_LOCK']}" })

