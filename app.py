from flask import Flask, session, render_template, request, g, redirect
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from helpers import login_required

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
            password = request.form.get("password")
            confirmPassword = request.form.get("confirmPassword")

            if not password == confirmPassword:
                text = f"Error: Password confirmation does not match."
                return render_template("register.html", erro=True, text=text)
            
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
    

@app.route("/", methods=["GET", "POST"])
def login():
    return redirect("/home")
    db = get_db()
    cursor = db.cursor()
    session.clear()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not (email or password):
            text = f"Error: Must provide email and password"
            return render_template("login.html", erro=True, text=text)

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            print("USUÁRIO NÃO EXISTE")
            text = f"Error: User does not exists or password is incorret"
            return render_template("login.html", erro=True, text=text)

        hash = user["password_hash"]
        print("HASH: ", hash)
        print("ENCONTRADO", user["email"])

        if not check_password_hash(hash, password):
            print("SENHA INCORRETA")
            text = f"Error: User does not exists or password is incorret"
            return render_template("login.html", erro=True, text=text)
        
        session["user_id"] = user["id"]

        return redirect("/home")
    else:
        return render_template("login.html")


@app.route('/home', methods=["GET", "POST"])
def home():
    db = get_db()
    cursor = db.cursor()
    # id = session["user_id"]
    id = 1
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    if request.method == 'GET':
        return render_template("home.html", nav=True, user=user)
    
    else:
        search = request.form.get("search")
        print("search", search)
        return render_template("home.html", nav=True, user=user)

        
        


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