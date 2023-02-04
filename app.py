import os
import requests
import boto3
import aiohttp
import asyncio

from dotenv import load_dotenv, find_dotenv
from flask import Flask, url_for, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserSignupForm, UserLoginForm, NewScribForm, UserEditForm
from models import db, connect_db, User, Scrib, ConceptImage

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
    os.environ.get('DATABASE_URL', 'postgresql:///scribcraft-1'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
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


# 404 error
@app.errorhandler(404)
def not_found(error):
    """404 page"""

    if not g.user:
        return redirect(url_for('login'))

    return render_template("404.html"), 404

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

    all_scribs = [scrib.serialize_scrib() for scrib in Scrib.query.all()]
    return jsonify(scribs=all_scribs)


# USERS REST API ROUTES


@app.route('/api/users')
def retrieve_users():
    """GET route to fetch all users from db.
    Returns list of user objects serialzied to dictionaries
    """

    all_users = [user.serialize_user() for user in User.query.all()]
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
        title = form.title.data
        prompt = form.prompt.data

        try:
            [image_urls, scrib_content] = asyncio.run(
                fetch_images_and_scrib_bundle(prompt))

            scrib = Scrib(title=title, prompt=prompt,
                          scrib_text=scrib_content, user_id=g.user.id)

            db.session.add(scrib)
            db.session.commit()

            # upload image urls to s3 bucket bc urls from openai expire after 1 hour
            s3_bucket_urls = []
            for index, png_url in enumerate(image_urls, start=1):
                s3_url = upload_img_to_s3_bucket_from_url(
                    png_url, scrib.id, index)
                s3_bucket_urls.append(s3_url)

            # add the s3 urls to the db
            add_concept_art_to_db(s3_bucket_urls, scrib.id)

        except Exception as e:
            return render_template('user/error.html', error_message=e)

        flash("Scrib created!", "success")
        return redirect(url_for('show_scrib', scrib_id=scrib.id))

    return render_template('user/create-scrib.html', form=form)


@app.route('/scribs/delete/<int:scrib_id>', methods=["POST"])
def delete_scrib(scrib_id):
    """Post route to submit form and delete script"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect(url_for('login'))

    scrib = Scrib.query.get_or_404(scrib_id)

    db.session.delete(scrib)
    db.session.commit()

    flash("Scrib deleted!", "success")
    return redirect(url_for('root'))


# USER ROUTES


@app.route('/users')
def users_page():
    """Presents list of site users and allows filtering by username"""

    if not g.user:
        flash("You must be logged in to view this page", "danger")
        return redirect(url_for('login'))

    users = User.query.all()

    return render_template('user/users.html', users=users)


@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """Page to display a specific user profile including some of their info and their scribs"""

    if not g.user:
        flash("You must be logged in to view this page.", "danger")
        return redirect('login')

    user = User.query.get_or_404(user_id)

    return render_template('user/user.html', user=user)


@app.route('/users/edit/<int:user_id>', methods=["GET", "POST"])
def edit_user_profile(user_id):
    """Page that displays form with prefilled data to edit user"""

    if not g.user:
        flash("You must be logged in to view this page.", "danger")
        return redirect(url_for('login'))

    if g.user.id != user_id:
        flash("Unauthorized access attempt.", "danger")
        return redirect(url_for('root'))

    form = UserEditForm(obj=g.user)

    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data
        user.about_me = form.about_me.data

        db.session.add(user)
        db.session.commit()

        flash("Profile updated!", "success")
        return redirect(url_for("show_user_profile", user_id=user.id))

    return render_template("/user/edit-user.html", form=form, user=g.user)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Receives post request from form to permanenetly delete user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for('login'))

    user_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect(url_for('signup'))


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
async def fetch_images_and_scrib_bundle(prompt):
    """Call other two async api functions to run requests concurrently"""

    async with aiohttp.ClientSession() as session:

        tasks = []
        tasks.append(asyncio.ensure_future(
            post_generate_image_art_API(session, prompt)))
        tasks.append(asyncio.ensure_future(
            post_generate_scrib_content_API(session, prompt)))

        bundle = await asyncio.gather(*tasks)
        return bundle


async def post_generate_image_art_API(session, prompt):
    """async function to fetch concept art"""

    headers = {'Authorization': f"Bearer {API_KEY}",
               'Content-Type': 'application/json'}
    prompt_with_base = BASE_IMG_PROMPT + prompt
    async with session.post(f"{AI_API_BASE_URL}images/generations", headers=headers, json={
            'prompt': prompt_with_base,
            "n": 3,
            "size": "512x512"
    }) as res:
        concept_art_images = await res.json()
        if "error" in concept_art_images:
            raise Exception(
                f"Error message: {concept_art_images['error']['message']}. Error type: {concept_art_images['error']['type']}")
        return [item['url'] for item in concept_art_images['data']]


async def post_generate_scrib_content_API(session, prompt):
    """async function to fetch story generated"""

    headers = {'Authorization': f"Bearer {API_KEY}",
               'Content-Type': 'application/json'}
    prompt_with_base = STORY_GENERATION_BASE_PROMPT + prompt

    async with session.post(f"{AI_API_BASE_URL}completions", headers=headers, json={
        "model": "text-davinci-003",
        "prompt": prompt_with_base,
        "max_tokens": 750,
        "temperature": 0.3
    }) as res:
        generated_text = await res.json()

        if "error" in generated_text:
            raise Exception(
                "Error in generating your text. Your content may be inappropriate. Please try again. 😭")
        return generated_text["choices"][0]["text"]


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


def upload_img_to_s3_bucket_from_url(url: str, scrib_id, img_number):
    """Uploads an image from input url to s3 bucket and returns url to display it publically from s3"""

    r = requests.get(url, stream=True)

    session = boto3.Session(aws_access_key_id=os.environ.get('ACCESS_KEY'),
                            aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY_AWS'))
    s3 = session.resource('s3')

    bucket_name = "scribcraft.concept"
    key = f"scrib_{scrib_id}_{img_number}"

    bucket = s3.Bucket(bucket_name)
    bucket.upload_fileobj(r.raw, key, ExtraArgs={
                          'ContentType': "image/png"})

    return f"https://s3.amazonaws.com/{bucket_name}/{key}"


def get_img_url_from_s3_bucket():
    """Fetch a url to image stored in bucket"""

    s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'),
                      aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY_AWS'))

    url = s3.generate_presigned_url(
        'get_object', Params={'Bucket': 'scribcraft.concept', 'Key': 'scrib_1'}, ExpiresIn=3600)

    print(url)
