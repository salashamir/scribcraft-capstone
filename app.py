import os

from flask import Flask, url_for, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import CommentForm, UserSignupForm, UserLoginForm
from models import db, connect_db, User, Scrib, Comment


CURRENT_USER_KEY = "current_user"

# instantiate app
app = Flask(__name__)

# set up config properties
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///scribcraft'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', "super_secret_key_763728")
toolbar = DebugToolbarExtension(app)

connect_db(app)


# USER SIGNUP/LOGIN/LOGOUT


@app.before_request
def add_user_to_g():
    """add current user to Flask global if logged in"""

    if CURRENT_USER_KEY in session:
        g.user = User.query.get(session[CURRENT_USER_KEY])
    else:
        g.user = None


def user_login(user):
    """Log in user"""

    session[CURRENT_USER_KEY] = user.id


def user_logout():
    """Logout the user"""

    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]


@app.route('/')
def root():
    if not g.user:
        flash("Login or register to view/create scribs", "danger")
        return redirect(url_for('login'))
    return render_template('home.html')


# AUTH ROUTES


@app.route('/login')
def login():
    """Login form page for registered users. Should redirect to dashboard if user is already logged in"""

    if g.user:
        return redirect('/')

    form = UserLoginForm()
    return render_template('auth/login.html', form=form)


@app.route('/signup')
def signup():
    """Signup form page for registered users. Should redirect to dashboard if user is already logged in"""

    if g.user:
        return redirect('/')

    form = UserSignupForm()

    return render_template('auth/signup.html', form=form)


@app.route('/logout')
def logout():
    pass


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
