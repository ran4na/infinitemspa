from flask import *
from models import *
from markupsafe import Markup
from bbcode_custom import parser as bbcode

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return redirect('/page/1')

@views.route('/pages/<int:page_number>')
def go_to_page(page_number):
    return redirect(f'/page/{page_number}')

@views.route('/page/<int:page_number>')
def show_page(page_number):
    newest_page: Page = Page.get_newest_page()

    if newest_page is None:
        return render_template('new_page.html', page_num=1)

    # Check if page exists. If not, show new_page.html
    if page_number > newest_page.page_num + 1:
        # Too far ahead.
        return redirect(f'/page/{newest_page.page_num}')

    page: Page = Page.query.filter_by(page_num=page_number).first()
    if page is None:
        # Show page creator
        return render_template('new_page.html', page_num=page_number)

    # Handle deleted pages
    if page.deleted is True:
        if page.page_num == newest_page.page_num:
            return render_template('new_page.html', page_num=page.page_num + 1)
        if page.next_undeleted_page() is None:
            return redirect("/page/1")
        return redirect(f"/page/{page.next_undeleted_page()}")

    # Fetch next and previous pages
    next_page: Page = Page.query.get(page_number + 1)
    prev_page: Page = Page.query.get(page_number - 1)

    # Handle next page
    if next_page is not None and next_page.deleted is True:
        next_page = Page.query.get(next_page.next_undeleted_page())
    next_page_title = "Next page..." if next_page is None else next_page.page_title
    next_page_url = f"/page/{next_page.page_num}" if next_page is not None else f"/page/{page_number + 1}"

    # Handle previous page
    if prev_page is not None and prev_page.deleted is True:
        prev_page = Page.query.filter_by(deleted=False).order_by(Page.page_num.asc()).first()
    prev_page_url = None if prev_page is None else f"/page/{prev_page.page_num}"

    # Render the page
    title = page.page_title
    text = Markup(bbcode.format(page.page_text))
    image_path = current_app.config["IMG_URL"] + page.panel_image.image_filename

    return render_template(
        'rendered_comic.html',
        p_title=title,
        p_text=text,
        p_imgpath=image_path,
        next_title=next_page_title,
        next_url=next_page_url,
        prev_url=prev_page_url,
        latest_url = f"/page/{newest_page.page_num}",
    )
