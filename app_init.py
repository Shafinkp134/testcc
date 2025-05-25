from flask import Flask, session, request, send_from_directory, g, url_for
from abilities import flask_app_authenticator
import logging
import os
from flask import Flask, session, request, send_from_directory, g
from models import db, User
from abilities import apply_sqlite_migrations
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db.init_app(app)

# Configure static folder
app.static_folder = 'static'
app.static_url_path = '/static'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with app.app_context():
    apply_sqlite_migrations(db.engine, db.Model, 'migrations')

def get_logo_url():
    custom_logo_path = os.path.join(app.root_path, 'static', 'logo.png')
    if os.path.exists(custom_logo_path):
        # Check if file is not empty
        if os.stat(custom_logo_path).st_size > 0:
            return '/static/logo.png'
    return 'https://placehold.co/300x300?text=logo'

app.config['LOGO_URL'] = get_logo_url()

# Set default theme
app.config['THEME'] = 'lofi'
# PICK FROM ANY DAISY UI THEME ALL YOU HAVE TO DO IS CHANGE THIS VARIABLE!

# Set default app title
app.config['APP_TITLE'] = '365 Days of Web Development'

# Context processor to inject theme and app title into all templates
@app.context_processor
def inject_theme_and_title():
    return dict(theme=app.config['THEME'], app_title=app.config['APP_TITLE'])


def auth_required(protected_routes=[]):
    def decorator():
        def decorated_view():
            if request.endpoint not in protected_routes or request.endpoint == 'static':
                return None
            return flask_app_authenticator(
                allowed_domains=None,
                allowed_users=None,
                logo_path = app.config['LOGO_URL'] if app.config['LOGO_URL'].startswith('http') else url_for('static', filename=app.config['LOGO_URL'].replace('/static/', ''), _external=True),
                app_title="Login to "+ app.config['APP_TITLE'],
                custom_styles={
                    "theme":app.config['THEME']
                },
                session_expiry=None
            )()
        return decorated_view
    return decorator

#Set up authentication only for protected routes
app.before_request(auth_required(['home_route'])())



@app.after_request
def create_or_update_user(response):
    if 'user' in session and 'user_email' in session['user']:
        email = session['user']['user_email']
        profile_picture = session['user'].get('photo_url')
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                new_user = User(email=email, profile_picture=profile_picture)
                db.session.add(new_user)
                db.session.commit()
                logging.info(f"Created new user: {email}")
            elif user.profile_picture != profile_picture:
                user.profile_picture = profile_picture
                db.session.commit()
                logging.info(f"Updated profile picture for user: {email}")
            
    return response