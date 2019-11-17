# Python standard libraries
import json
import os
import sqlite3
from datetime import datetime, timedelta
'''
#imports for webview
import sys
import threading
import webview
'''
# Third party libraries
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command, get_db
from user import User

# Configuration
GOOGLE_CLIENT_ID = "685992959593-9pukd1atbt6a7eoce1btivel9ihkb5fs.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "WWl12m4EZ5e7whMxijNUgV4y"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

PERMS = ["wee.jiawei.kevan@dhs.sg", "khoo.phaikchoo.carina@dhs.sg", "xun.shengdi@dhs.sg", "mathew.rithu.ann@dhs.sg", "liu.yixuan@dhs.sg", "tee.renwey@dhs.sg", "lim.valerie@dhs.sg"]

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", admin=current_user.admin)
    else:
        return render_template("login2.html")

#tobedeletedlater
@app.route("/notifs")
def notifs():
    return render_template("test.html")

@app.route("/about")
@login_required
def about():
    return render_template("about.html", admin=current_user.admin)

@app.route("/competition")
@login_required
def competition():
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM competition")
    competitions = cursor.fetchall()
    now = datetime.now()
    i = 0
    while i < len(competitions):
        eventdate = datetime.strptime(competitions[i][1], "%Y-%m-%d")
        if now > eventdate + timedelta(days=1):
            cursor.execute("DELETE FROM competition WHERE id={}".format(competitions[i][0]))
            competitions.pop(i)
        else:
            i += 1
    connection.commit()
    connection.close()
    return render_template("competition.html", admin=current_user.admin, competitions=competitions)

@app.route("/announcements")
@login_required
def announcements():
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM announcement")
    announcements = cursor.fetchall()
    now = datetime.now()
    i = 0
    while i < len(announcements):
        eventdate = datetime.strptime(announcements[i][1], "%Y-%m-%d")
        if now > eventdate + timedelta(days=1):
            cursor.execute("DELETE FROM announcement WHERE id={}".format(announcements[i][0]))
            announcements.pop(i)
        else:
            i += 1
    connection.commit()
    connection.close()

    return render_template("announcements.html", admin=current_user.admin, announcements=announcements)

@app.route("/morning")
@login_required
def morning():
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM flagraising")
    venues = cursor.fetchall()
    connection.close()
    return render_template("morning.html", admin=current_user.admin, venues=venues[0])

@app.route("/submit")
@login_required
def submit():
    if current_user.admin == 1:
        return render_template("submit.html", admin=current_user.admin)
    else:
        return "Unauthorized user"

@app.route("/submit2", methods=["POST"])
@login_required
def submit2():
    group = request.form.get("group")
    if current_user.admin == 1:
        return render_template("submit2.html", admin=current_user.admin, group=group)
    else:
        return "Unauthorized user"

@app.route("/delete")
@login_required
def delete():
    if current_user.admin == 1:
        return render_template("delete.html", admin=current_user.admin)
    else:
        return "Unauthorized user"

@app.route("/delete2", methods=["POST"])
@login_required
def delete2():
    group = request.form.get("group")
    connection = sqlite3.connect("sqlite_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM {}".format(group))
    details = cursor.fetchall()
    connection.close()
    if current_user.admin == 1:
        return render_template("delete2.html", admin=current_user.admin, group=group, details = details)
    else:
        return "Unauthorized user"

@app.route("/deletion", methods=["POST"])
@login_required
def deletion():
    value = request.form.get("value")
    #delete code goes here
    return value

@app.route("/submission", methods=["POST"])
@login_required
def submission():
    if current_user.admin == 1:
        group = request.form.get("group")
        if group == "announcements" or group == "competition":
            eventdate = request.form.get("eventdate")
            people_list = request.form.getlist("people")
            people = ""
            for a in people_list:
                people = people + a + " "
            details = request.form.get("details")
            op = current_user.email

            if group == "announcements":
                db = get_db()
                db.execute(
                    "INSERT INTO announcement (eventdate, people, details, op) "
                    "VALUES (?, ?, ?, ?)",
                    (eventdate, people, details, op)
                )
                db.commit()
            elif group == "competition":
                db = get_db()
                db.execute(
                    "INSERT INTO competition (eventdate, people, details, op) "
                    "VALUES (?, ?, ?, ?)",
                    (eventdate, people, details, op)
                )
                db.commit()
        else:
            paradesq = ''
            classroom = ''
            hall = ''
            pac = ''
            paradesq_list = request.form.getlist("paradesq")
            for a in paradesq_list:
                paradesq = paradesq + a + ' '
            classroom_list = request.form.getlist("classroom")
            for a in classroom_list:
                classroom = classroom + a + ' '
            hall_list = request.form.getlist("hall")
            for a in hall_list:
                hall = hall + a + ' '
            pac_list = request.form.getlist("pac")
            for a in pac_list:
                pac = pac + a + ' '
            db = get_db()
            db.execute("""
                UPDATE flagraising
                SET paradesq=?, classroom=?, hall=?, pac=?
            """, (paradesq, classroom, hall, pac))
            db.commit()

        return render_template("success.html")
    else:
        return "Unauthorized user"


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        if users_email[-7:] == "@dhs.sg":
            users_classid = userinfo_response.json()["given_name"]
            if users_classid[:3] == "19Y" or users_classid[:5].lower() == "staff":
                unique_id = userinfo_response.json()["sub"]
                picture = userinfo_response.json()["picture"]
                users_name = userinfo_response.json()["family_name"]
            else:
                return "You are no longer from DHS!"
        else:
            return "You are not from DHS!"
    else:
        return "User email not available or not verified by Google.", 400

    # Doesn't exist? Add to database
    if not User.get(unique_id):
        if users_classid[:5].lower() == "staff" or users_email in PERMS:
            User.create(unique_id, users_classid, users_name, users_email, picture, 1)
        else:
            User.create(unique_id, users_classid, users_name, users_email, picture, 0)

    user = User.get(unique_id)

    # Begin user session by logging the user in
    login_user(user)
    
    
    #for debugging
    userinfo_response = requests.get(uri, headers=headers, data=body)
    users_email = userinfo_response.json()["email"]
    print("Success!", users_email, '1')
    
    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    
    
    print(current_user)
    
    
    if current_user.is_authenticated:
        logout_user()
        
        
        print("Logout")
    userinfo_endpoint = requests.get(GOOGLE_DISCOVERY_URL).json()["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    users_email = userinfo_response.json()["email"]
    print("Logout!", users_email, '1')
    print(current_user)
    
    
    return redirect(url_for("index"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/cdn')
def bootstrap():
    return render_template('testbootstrap.html')

#normal flask cmd run
'''
if __name__ == "__main__":
    app.run(ssl_context="adhoc", debug=True)

'''
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#run for webview

import webview
import click
import os
import threading
import sys

#@click.command()
#@click.option('--port', default=5000, help='Port number')
#@click.option('--host', default='localhost', help='Host name')
def start_server(port, host):
    # Architected this way because my console_scripts entry point is at
    # start_server.

    kwargs = {'host': host, 'port': port}
    t = threading.Thread(target=app.run, daemon=True, kwargs=kwargs)
    t.start()

    webview.create_window("Dunmanapp",
                          "http://127.0.0.1:{0}".format(port))
    webview.start(debug=True)
    sys.exit()

if __name__ == "__main__":
    start_server(5000, '127.0.0.1')