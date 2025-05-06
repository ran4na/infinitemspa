from flask import *
from models import *
from flask_login import *

admin = Blueprint('admin', __name__)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    # get username/password
    
    user = User.test_login(request.form.get("username"), request.form.get("password"))
      # User was found with matching credentials
    if user is not None:
        login_user(user)
        return redirect(url_for("admin.admin_portal"))
    return render_template('login.html')



@admin.route('/admin_portal')
@login_required
def admin_portal():
    return render_template('admin_portal.html')

