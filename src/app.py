from flask import *
import os
from views import *
from models import *
from api import *

app = Flask(__name__)
bcrypt = Bcrypt(app)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "data/database.db")
app.config['UPLOAD_FOLDER'] = "static/upload/"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5MB

app.register_blueprint(views)
app.register_blueprint(models)
app.register_blueprint(api)

db.init_app(app)

create_db(app)

# Run server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)