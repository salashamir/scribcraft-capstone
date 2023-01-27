from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

# form classes


class CommentForm(FlaskForm):
    """Form for adding/editing comments"""

    text = TextAreaField('Comment', validators=[DataRequired(
        message="Comment must contain content body to be submitted.")])


class UserSignupForm(FlaskForm):
    """Form for adding a user to db on signup submission"""

    username = StringField('Username', validators=[DataRequired(
        message="Username cannot be blank."), Length(min=4, max=20, message="Username must be between 4 and 20 characters.")])
    email = StringField('Email', validators=[DataRequired(
        message="Email field cannot be blank."), Email(message="Please type a valid email.")])
    image_url = StringField(
        "(Optional )URL for avatar image", validators=[Optional()])
    password = PasswordField('Password', validators=[Length(
        min=8, message="Password must be longer than 7 characters."), DataRequired(message="Password field cannot be blank.")])
    password_confirm = PasswordField('Confirm password', validators=[Length(
        min=8, message="Password must be longer than 7 characters."), DataRequired(message="Password field cannot be blank.")])


class UserLoginForm(FlaskForm):
    """Form for logging in a user"""

    username = StringField('Username', validators=[DataRequired(
        message="Username cannot be blank."), Length(min=4, max=20, message="Username must be between 4 and 20 characters.")])
    password = PasswordField('Password', validators=[Length(
        min=8, message="Password must be longer than 7 characters."), DataRequired(message="Password field cannot be blank.")])
