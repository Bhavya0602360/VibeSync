from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models.face_model import get_mood_from_webcam
from models.voice_model import recognize_speech
from models.text_model import detect_emotion
from flask_cors import CORS
import json
import os
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

USER_FILE = "users.json"

# Ensure users file exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def get_songs_for_mood(mood):
    mood_songs = {
        "happy": [
            {"title": "Happy - Pharrell Williams", "url": "/static/songs/rey.wav"},
            {"title": "Good Life - OneRepublic", "url": "/static/songs/hey.wav"},
            {"title": "Fake It - Bastille", "url": "/static/songs/a.wav"},
            {"title": "Electric Feel - MGMT", "url": "/static/songs/aa.wav"},
            {"title": "Tongue Tied - Grouplove", "url": "/static/songs/ab.wav"},
            {"title": "Pumped Up Kicks - Foster the People", "url": "/static/songs/ad.wav"},
            {"title": "Safe and Sound - Capital Cities", "url": "/static/songs/av.wav"},
            {"title": "Walking on a Dream - Empire of the Sun", "url": "/static/songs/av.wav"},
            {"title": "Shark Attack - Grouplove", "url": "/static/songs/as.wav"},
            {"title": "Dog Days Are Over - The Machine", "url": "/static/songs/an.wav"},
            {"title": "Young Folks - Peter Bjorn and John", "url": "/static/songs/am.wav"}
        ],
        "sad": [
            {"title": "Someone Like You - Adele", "url": "/static/songs/key.wav"},
            {"title": "Fix You - Coldplay", "url": "/static/songs/jey.wav"},
            {"title": "Take a Walk - Passion Pit", "url": "/static/songs/b.wav"},
            {"title": "Sweet Disposition - The Temper Trap", "url": "/static/songs/bl.wav"},
            {"title": "Anna Sun - Walk the Moon", "url": "/static/songs/blue.wav"},
            {"title": "Dreaming - Smallpools", "url": "/static/songs/c.wav"},
            {"title": "Helena Beat - Foster the People", "url": "/static/songs/cc.wav"},
            {"title": "Kids - MGMT", "url": "/static/songs/csk.wav"},
            {"title": "Midnight City - M83", "url": "/static/songs/dc.wav"},
            {"title": "Electric Love - Børns", "url": "/static/songs/rcb.wav"}
        ],
        "neutral": [
            {"title": "Stronger - Kanye West", "url": "/static/songs/pey.wav"},
            {"title": "Colors - Grouplove", "url": "/static/songs/d.wav"},
            {"title": "Cough Syrup - Young the Giant", "url": "/static/songs/e.wav"},
            {"title": "Float On - Modest Mouse", "url": "/static/songs/f.wav"},
            {"title": "Out of My League - Fitz and The Tantrums", "url": "/static/songs/ff.wav"},
            {"title": "Lisztomania - Phoenix", "url": "/static/songs/g.wav"},
            {"title": "Some Nights - fun", "url": "/static/songs/gry.wav"},
            {"title": "Shut Up and Dance - Walk the Moon", "url": "/static/songs/gt.wav"},
            {"title": "On Top of the World - Imagine Dragons", "url": "/static/songs/hh.wav"},
            {"title": "Fireflies - Owl City", "url": "/static/songs/k.wav"},
        ],
        "angry": [
            {"title": "Somewhere I Belong - Linkin Park", "url": "/static/songs/kkl.wav"},
            {"title": "Safe and Sound - Capital Cities", "url": "/static/songs/kkr.wav"},
            {"title": "Midnight City - M83", "url": "/static/songs/l.wav"},
            {"title": "Pumped Up Kicks - Foster the People", "url": "/static/songs/ll.wav"},
            {"title": "Tongue Tied - Grouplove", "url": "/static/songs/m.wav"},
            {"title": "Lights - Ellie Goulding", "url": "/static/songs/mi.wav"},
            {"title": "Call Me Maybe - Carly Rae Jepsen", "url": "/static/songs/mn.wav"},
            {"title": "Good Time - Owl City & Carly Rae Jepsen", "url": "/static/songs/w.wav"},
            {"title": "Tongue Tied - Grouplove", "url": "/static/songs/x.wav"},
            {"title": "Young Blood - The Naked and Famous", "url": "/static/songs/xx.wav"}
        ]
    }
    return mood_songs.get(mood.lower(), [])

@app.route("/")
def index():
    if "username" in session:
        users = load_users()
        user = users.get(session["username"], {})
        return render_template("index.html", username=session["username"], email=user.get("email", "not_set@example.com"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")
        users = load_users()

        if username in users:
            stored_password = users[username]["password"].encode("utf-8")
            if bcrypt.checkpw(password, stored_password):
                session["username"] = username
                session["email"] = users[username].get("email", "not_set@example.com")
                return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]
        users = load_users()

        if username in users:
            return render_template("register.html", error="Username already exists.")
        if password != confirm:
            return render_template("register.html", error="Passwords do not match.")

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        users[username] = {"email": email, "password": hashed_pw.decode("utf-8")}
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("email", None)
    return redirect(url_for("login"))

@app.route("/face", methods=["POST"])
def face_recognition():
    mood = get_mood_from_webcam()
    return jsonify({"mood": mood, "songs": get_songs_for_mood(mood)})

@app.route("/voice", methods=["POST"])
def voice_recognition():
    mood = recognize_speech()
    return jsonify({"mood": mood, "songs": get_songs_for_mood(mood)})

@app.route("/text", methods=["POST"])
def text_analysis():
    data = request.json
    text = data.get("text")
    mood = detect_emotion(text)
    return jsonify({"mood": mood, "songs": get_songs_for_mood(mood)})

if __name__ == "__main__":
    app.run(debug=True)
