from flask import *
from models import *

api = Blueprint('api', __name__, url_prefix='/api')

@api.route("/create_page", methods="POST")
def create_page():
    # First, check if page is not the newest page + 1, or already exists.
    