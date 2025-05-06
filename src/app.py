from flask import *
import os
from views import *
from models import *
from api import *
from admin import *
import secrets
from configparser import ConfigParser


app = Flask(__name__)
bcrypt = Bcrypt(app)

config = ConfigParser()
config.read(os.path.join(app.root_path, 'config.cfg'))


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "data/database.db")
app.config['UPLOAD_FOLDER'] = "static/upload/"
app.config['MAX_CONTENT_LENGTH'] = config.getint('config', 'MAX_SIZE') * 1024 * 1024 # 5MB
secret = secrets.token_urlsafe(16)
app.config['SECRET_KEY'] = secret
app.config["UPLOAD_LOCK"] = config.getboolean('config', 'UPLOAD_LOCK')

app.register_blueprint(views)
app.register_blueprint(models)
app.register_blueprint(api)
app.register_blueprint(admin)

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": f"Couldn't upload image. \
            Max filesize: {current_app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)}MB, \
                Valid file types: {', '.join(ALLOWED_EXTENSIONS)}"}), 413

db.init_app(app)

create_db(app)

# Initialize bcrypt
bcrypt.init_app(app)

# Flask login setup
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
login_manager.init_app(app)

# if no admin user, create one.
with app.app_context():
    if(User.query.count() == 0):
        finished = False
        print("Create a new admin user.")
        while(finished == False):
            username = input("Enter username: ")
            password = input("Enter password: ")
            confirmPass = input("Confirm password: ")
            if(confirmPass == password):
                finished = True
                admin_user = User(username, password)
                db.session.add(admin_user)
                db.session.commit()
            else:
                print("Passwords don't match. Starting over...")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('403.html'), 403

# Run server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
    