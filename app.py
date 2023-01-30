import os
import requests

from dotenv import load_dotenv, find_dotenv
from flask import Flask, url_for, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import CommentForm, UserSignupForm, UserLoginForm, NewScribForm
from models import db, connect_db, User, Scrib, Comment, ConceptImage

load_dotenv(find_dotenv())

CURRENT_USER_KEY = "current_user"
API_KEY = os.environ.get('OPEN_AI_API_KEY')
AI_API_BASE_URL = "https://api.openai.com/v1/"
BASE_IMG_PROMPT = "Photorealistic detailed high quality 4k concept art for a story about: "
STORY_GENERATION_BASE_PROMPT = "From the following prompt below create a brief, original literary plot outline including: a brief description of the main character and his or her motivation, brief character sketches for different characters that fit within the story, brief sketch of an antagonist that fits the tone of the story and the antagonist's motives, a brief beginning with an inciting incident, rising action, and a fitting conclusion to the story. Prompt: "

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
                image_url=form.image_url.data or User.image_url.default.arg
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


# SCRIB REST API ROUTES


@app.route('/api/scribs')
def retrieve_scribs():
    """GET route to fetch all scribs from db.
    Returns list of scrib objects serialzied to dictionaries
    """

    all_scribs = [scrib.serialize() for scrib in Scrib.query.all()]
    return jsonify(scribs=all_scribs)


# USERS REST API ROUTES


@app.route('/api/users')
def retrieve_users():
    """GET route to fetch all users from db.
    Returns list of user objects serialzied to dictionaries
    """

    all_users = [user.serialize() for user in User.query.all()]
    return jsonify(users=all_users)


# GET SINGLE, CREATE, UPDATE, DELETE SCRIB ROUTES
@app.route('/scribs/<int:scrib_id>')
def show_scrib(scrib_id):
    """Displays a single scrib on page"""

    if not g.user:
        flash("You must be logged in to view this page.", "danger")
        return redirect(url_for('login'))

    scrib = Scrib.query.get_or_404(scrib_id)

    return render_template('user/scrib.html', scrib=scrib)


@app.route('/create-scrib', methods=["GET", "POST"])
def create_scrib():
    """Presents form to create a new scrib and handles submission"""

    if not g.user:
        flash("You must be logged in to view this page.", "danger")
        return redirect(url_for('login'))

    form = NewScribForm()

    if form.validate_on_submit():
        pass

    return render_template('user/create-scrib.html', form=form)


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


# DEFINITIONS for AI api requests


def generate_concept_art_list_API(prompt):
    """Function that sends qrequest to image generation endpoint and returns an array of the urls for five images to be stored
    Params: 
        prompt:string, should be the same prompt submitted as user input from create scrib form, will get attached to base image search string for a better concept art result.
        scrib_id: id of scrib images will belong to 
    Return: shoudl return a list containing 5 urls for generated images
    """

    headers = {'Authorization': f"Bearer {API_KEY}",
               'Content-Type': 'application/json'}
    prompt_with_base = BASE_IMG_PROMPT + prompt

    res = requests.post(f"{AI_API_BASE_URL}images/generations", headers=headers, json={
        'prompt': prompt_with_base,
        "n": 5,
        "size": "512x512"
    })
    return [item['url'] for item in res.json()['data']]


def add_concept_art_to_db(concept_art, scrib_id):
    """Stores concept art to relevant table in database
    Params: 
        concept_art: list, should be a list of urls pointing to the images generated
        scrib_id: id for scrib that all images will belong to or will be associated with
    Returns None
    """

    concept_image_objects = [ConceptImage(
        concept_image_url=concept_image_url, scrib_id=scrib_id) for concept_image_url in concept_art]

    db.session.add_all(concept_image_objects)
    db.session.commit()


def generate_scrib_content_API(prompt):
    """Passed in a string prompt will make  request to completion endpoint to generate the sttory plot outline
    Returns string of scrib content with line breaks 
    """

    headers = {'Authorization': f"Bearer {API_KEY}",
               'Content-Type': 'application/json'}
    prompt_with_base = STORY_GENERATION_BASE_PROMPT + prompt

    res = requests.post(f"{AI_API_BASE_URL}completions", headers=headers, json={
        "model": "text-davinci-003",
        "prompt": prompt_with_base,
        "max_tokens": 750,
        "temperature": 0.3
    })

    return res.json()["choices"][0]["text"]
