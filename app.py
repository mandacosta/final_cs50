from flask import Flask, session, render_template, request, g, redirect
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_aqui'

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/register', methods=["GET", "POST"])
def register():
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":      
        for input, value in request.form.items():
            if not value:
                text = f"Error: {input} must me provided"
                return render_template("register.html", erro=True, text=text)
        email = request.form.get("email")
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_exists = cursor.fetchone()
        if user_exists:
            text = f"Error: Email already being used."
            return render_template("register.html", erro=True, text=text)
        else:
            name = request.form.get("name")
            email = request.form.get("email")
            birth = request.form.get("birthdate")
            gender = request.form.get("gender")
            hash = generate_password_hash(request.form.get("password"))
            cursor.execute("INSERT INTO users (name, email, birth, gender, password_hash) VALUES (?, ?, ?, ?, ?)", (name, email, birth, gender, hash))
            db.commit()
            user_id = cursor.lastrowid
            session["user_id"] = user_id
            return redirect("/home")

    else:
        return render_template("register.html")
    

@app.route('/')
def login():
    db = get_db()
    cursor = db.cursor()
    # users = cursor.execute("select * from users").fetchall()
    # users = cursor.execute("select * from users").fetchall()
    # users = cursor.execute("select * from users").fetchall()
    return render_template("login.html")


@app.route('/home')
def home():
    db = get_db()
    cursor = db.cursor()
    return render_template("home.html")



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    print("Closing...")
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run()