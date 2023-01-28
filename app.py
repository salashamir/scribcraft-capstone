import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask, url_for, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import CommentForm, UserSignupForm, UserLoginForm
from models import db, connect_db, User, Scrib, Comment

load_dotenv(find_dotenv())

CURRENT_USER_KEY = "current_user"

# instantiate app
app = Flask(__name__)

# set up config properties
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///scribcraft'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
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

    scribs = Scrib.query.all()
    return render_template('user/dashboard.html', scribs=scribs)


# AUTH ROUTES


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login form page for registered users. Should redirect to dashboard if user is already logged in"""

    if g.user:
        return redirect('/')

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            user_login(user)
            flash(f'Welcome, {user.username}!', 'success')
            return redirect('/')

    return render_template('auth/login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Signup form page for registered users. Should redirect to dashboard if user is already logged in"""

    if g.user:
        return redirect('/')

    form = UserSignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data
            )
            db.session.commit()

        except IntegrityError:
            flash('Username already taken.', 'danger')
            return render_template('auth/signup.html', form=form)

        user_login(user)

        return redirect(url_for('root'))

    return render_template('auth/signup.html', form=form)


@app.route('/logout')
def logout():
    """Log user out of application by removing their id from the session"""

    user_logout()
    flash("User logged out!", "success")
    return redirect(url_for('login'))


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
