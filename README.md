# InfiniteMSPFA

MSPFA, but the user creates the pages!

## Installation
Install dependencies w/ ``pip install -e .``

Run the development server w/ ``python src/app.py``

You can use a WSGI server like Gunicorn to deploy publicly. However, there may be file permission issues preventing uploads and DB creation.

To remedy them, chown the upload/db files to the server user, and ``chmod -R 777 /src/static/upload/`` and ``chmod -R 777 /src/data/``.

## Administration

On first run, the program will ask you to create an admin user. Be sure to use a strong password.

The admin portal is accessible at ``host-url/admin_portal`` and requires logging in as the admin user.

From here, you can soft-delete panels (deleting all their info and skipping over it in the reader), delete images (while retaining their hash), and ban users based on their hashed IP. You can also just lock uploads entirely.

You can also set the max upload size/lock in ``src/config.cfg``

It's probably ideal to make the first page yourself.
