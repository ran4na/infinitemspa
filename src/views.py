from flask import *

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('rendered_comic.html')

@views.route('/new')
def create_new_comic():
    return render_template('new_page.html')