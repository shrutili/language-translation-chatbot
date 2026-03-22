from flask import Flask, render_template, request, redirect, session
import sqlite3
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS chats(username TEXT, message TEXT, response TEXT)")
    db.commit()
    db.close()

init_db()

# 🌐 Languages
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "ar": "Arabic",
    "zh": "Chinese",
    "pt": "Portuguese",
    "tr": "Turkish",
    "nl": "Dutch"
}

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        ).fetchone()

        if user:
            session["user"] = u
            return redirect("/dashboard")

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        db = get_db()
        db.execute("INSERT INTO users VALUES (?,?)", (u, p))
        db.commit()

        return redirect("/")

    return render_template("register.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = get_db()

    if request.method == "POST":
        text = request.form.get("text", "")
        lang = request.form.get("lang")

        if text.strip() != "":
            try:
                translated = GoogleTranslator(source='auto', target=lang).translate(text)
            except:
                try:
                    translated = GoogleTranslator(source='auto', target='en').translate(text)
                except:
                    translated = "Translation not available"

            response = f"Translated ({LANGUAGES.get(lang, 'Unknown')}): {translated}"

            db.execute(
                "INSERT INTO chats VALUES (?,?,?)",
                (session["user"], text, response)
            )
            db.commit()

    chats = db.execute(
        "SELECT message, response FROM chats WHERE username=?",
        (session["user"],)
    ).fetchall()

    return render_template("dashboard.html", chats=chats, languages=LANGUAGES)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)