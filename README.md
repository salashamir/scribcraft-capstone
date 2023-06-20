LINK to OpenAI API used for this project:
https://platform.openai.com/docs/introduction

Project title: Scribcraft
Full stack application using a Flask server and PostgreSQL db

Link to live site: https://scribcraft-flask.herokuapp.com/login

Scribcraft is a site where users can sign up and submit story outline prompts that will generate plots and characters for them that might serve as inspiration. The site will also generate some AI art to accompany the text and display them together, saved to the person's account and also visible on the dashboard when they log in.

Features implemented:
Authentication/authorization with bcrypt and Flask server session
Ability to save generated scribs to your account
Ability to peruse other people's scribs on the dashboard
Filter their scribs
Integration with S3 bucket to store AI-generated images

Standard user flow:

1. sign up
2. look at other people's generated scribs
3. go to the prompt form and create your own
4. edit yout account
5. delete a scrib (that you created)

Technology stack:
Flask - Jinja - PostgreSQL - JS - Deployed on Heroku
