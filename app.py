from flask import Flask, session, render_template, request, g, redirect
import sqlite3


app = Flask(__name__)


@app.route('/register', methods=["GET", "POST"])
def register():
    db = get_db()
    cursor = db.cursor()
    # users = cursor.execute("select * from users").fetchall()

    if request.method == "POST":      
        for input, value in request.form.items():
            if not value:
                text = f"Error: {input} must me provided"
                return render_template("register.html", erro=True, text=text)

    else:
        return render_template("register.html")

    return render_template("register.html")


@app.route('/')
def login():
    db = get_db()
    cursor = db.cursor()
    # users = cursor.execute("select * from users").fetchall()
    # users = cursor.execute("select * from users").fetchall()
    # users = cursor.execute("select * from users").fetchall()
    return render_template("login.html")


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