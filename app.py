from flask import Flask, session, render_template, request, g, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from helpers import login_required, formate_list_of_groups, date_now
import random

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
        cursor.execute("SELECT * FROM groups")
        groups = cursor.fetchall()
        cursor.execute("SELECT * FROM groups_users")
        participants_all = cursor.fetchall()
        list_of_groups = formate_list_of_groups(groups, participants_all, id)

        print("LISTA DE GRUPOS GET", list_of_groups)

        return render_template("home.html", nav=True, user=user, groups=list_of_groups)
    
    else:
        search = request.form.get("search")
        groups = []
        print("search", search)
        if not search:
            cursor.execute("SELECT * FROM groups")
            groups = cursor.fetchall()
        elif search == 'groups_i_own':
            cursor.execute("SELECT * FROM groups WHERE owner_id = ?", (id,))
            groups = cursor.fetchall()
        elif search == 'groups_iam_in':
            cursor.execute("SELECT a.* FROM groups a LEFT JOIN groups_users b ON a.id = b.group_id WHERE b.user_id = ?", (id,))
            groups = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM groups WHERE name LIKE ?", ('%' + search + '%',))
            groups = cursor.fetchall()
        
        cursor.execute("SELECT * FROM groups_users")
        participants_all = cursor.fetchall()
        list_of_groups = formate_list_of_groups(groups, participants_all, id)

        print("LISTA DE GRUPOS POST", list_of_groups)

        return render_template("home.html", nav=True, user=user, groups=list_of_groups)



@app.route('/new_group', methods=["GET", "POST"])
def new_group():
    db = get_db()
    cursor = db.cursor()
    # id = session["user_id"]
    id = 1
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    date = date_now()

    if request.method == 'POST':

        for input, value in request.form.items():
            if not value:
                text = f"Error: {input} must me provided"
                return render_template("home.html", erro=True, text=text, nav=True, user=user)
        name = request.form.get("name")
        description = request.form.get("description")
        image_url = request.form.get("image_url")
        event_date = request.form.get("event_date")
        draw_date = request.form.get("draw_date")

        cursor.execute("INSERT INTO groups (name, description, image_url, event_date, draw_date, creation_date, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, description, image_url, event_date, draw_date, date, id))
        db.commit()
        group_id = cursor.lastrowid

        cursor.execute("INSERT INTO groups_users (group_id, user_id, addtion_date) VALUES (?, ?, ?)", (group_id, id, date))
        db.commit()
        return redirect("/home")
    
    else:
        return redirect("/home")


@app.route('/modal_group/<group_id>', methods=["GET"])
def modal_group(group_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT a.id, a.name, a.draw_date, b.user_id, c.name as fullname, c.email FROM groups a LEFT JOIN groups_users b ON a.id = b.group_id LEFT JOIN users c ON b.user_id = c.id WHERE a.id = ?", (group_id, ))
    group_users = cursor.fetchall()

    if group_users:
        participants = [{'name': row['fullname'], 'email': row['email']} for row in group_users if row['user_id']]

        group_data = {
            'participants': participants,
            'name': group_users[0]['name'],
            'draw_date': group_users[0]['draw_date']
        }
        return jsonify(group_data)
    else:
        return jsonify({'error': 'Grupo não encontrado'})


@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
    db = get_db()
    cursor = db.cursor()
    # id = session["user_id"]
    id = 1
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    date = date_now()

    if request.method == 'POST':
        group_id = request.form.get("group_id")
        cursor.execute("INSERT INTO groups_users (user_id, group_id, addtion_date) VALUES (?, ?, ?)", (id, group_id, date))
        db.commit()
        return redirect("/home")
    
    else:
        return redirect("/home")

@app.route('/group/<group_id>', methods=['GET', 'POST'])
def group(group_id):
    db = get_db()
    cursor = db.cursor()
    # id = session["user_id"]
    id = 1
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM groups_users a JOIN users b ON a.user_id = b.id WHERE a.group_id = ?", (group_id, ))
        participants = cursor.fetchall()

        cursor.execute("SELECT id FROM groups_users WHERE group_id = ? AND user_id = ?", (group_id, id,))
        group_user_id = cursor.fetchone()
        
        group_user_id = group_user_id['id']

        cursor.execute("SELECT c.* FROM groups_users a JOIN group_user_option b ON a.id = b.group_user_id JOIN gift_option c ON c.id = b.gift_option_id WHERE a.id = ?", (group_user_id, ))
        gift_options = cursor.fetchall()

        cursor.execute("SELECT a.*, b.name as creator, b.email FROM groups a LEFT JOIN users b ON a.owner_id = b.id WHERE a.id = ?", (group_id, ))
        group = cursor.fetchone()

        # I am the "took" one and the person I retrieved is the "taken" one
        cursor.execute("SELECT a.date, b.name, b.email, b.gender, b.birth FROM draw a JOIN users b ON a.taken_id = b.id WHERE a.took_id = ? AND a.group_id = ?", (id, group_id,))
        draw = cursor.fetchone()

        owner = group['owner_id'] == id

        return render_template("group.html", nav=True, user=user, owner=owner, participants=participants, gift_options=gift_options, draw=draw, group=group)


@app.route('/draw', methods=['GET', 'POST'])
def draw():
    db = get_db()
    cursor = db.cursor()
    date = date_now()

    if request.method == 'POST':
        print("ENTROU NO DRAW")
        group_id = request.form.get("group_id")
        cursor.execute("SELECT b.name, b.id FROM groups_users a JOIN users b ON a.user_id = b.id WHERE a.group_id = ?", (group_id, ))
        part_all = cursor.fetchall()

        if len(part_all) < 2:
            return redirect(f"/group/{group_id}")
        else:

            part_list = [part for part in part_all]
            random.shuffle(part_list)

            print('LISTA EMBARALHADA', part_list)

            for pessoa_atual, pessoa_seguinte in zip(part_list, part_list[1:]):
                print("Pessoa Atual:", pessoa_atual["name"], pessoa_atual["id"])
                print("Pessoa Seguinte:", pessoa_seguinte["name"], pessoa_seguinte["id"])
                # Lógica para atribuir a pessoa seguinte à pessoa atual no amigo secreto
                cursor.execute("INSERT INTO draw (group_id, took_id, taken_id, date) VALUES (?, ?, ?, ?)", (group_id, pessoa_atual["id"], pessoa_seguinte["id"], date, ))

            # Lógica para atribuir o primeiro da lista ao último da lista no amigo secreto
            last = part_list[-1]
            first = part_list[0]
            cursor.execute("INSERT INTO draw (group_id, took_id, taken_id, date) VALUES (?, ?, ?, ?)", (group_id, last["id"], first["id"], date, ))

            db.commit()

            return redirect(f"/group/{group_id}")
    else:
        return redirect(f"/group/{group_id}")


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