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
        try:
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
            
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("register.html", erro=True, text=text)      

    else:
        return render_template("register.html")
    

@app.route("/", methods=["GET", "POST"])
def login():
    db = get_db()
    cursor = db.cursor()
    session.clear()

    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            if not (email or password):
                text = f"Error: Must provide email and password"
                return render_template("login.html", erro=True, text=text)

            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if not user:
                text = f"Error: User does not exists or password is incorret"
                return render_template("login.html", erro=True, text=text)

            hash = user["password_hash"]

            if not check_password_hash(hash, password):
                text = f"Error: User does not exists or password is incorret"
                return render_template("login.html", erro=True, text=text)
            
            session["user_id"] = user["id"]

            return redirect("/home")
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("login.html", erro=True, text=text)
    else:
        return render_template("login.html")
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/home', methods=["GET", "POST"])
@login_required
def home():
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM groups")
            groups = cursor.fetchall()

            cursor.execute("SELECT * FROM groups_users")
            participants_all = cursor.fetchall()

            cursor.execute("SELECT DISTINCT group_id, date FROM draw")
            draws = cursor.fetchall()

            list_of_groups = formate_list_of_groups(groups, participants_all, id, draws)

            return render_template("home.html", nav=True, user=user, groups=list_of_groups)
        
        else:
            search = request.form.get("search")
            groups = []
            cursor.execute("SELECT DISTINCT group_id, date FROM draw")
            draws = cursor.fetchall()

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
            list_of_groups = formate_list_of_groups(groups, participants_all, id, draws)

            return render_template("home.html", nav=True, user=user, groups=list_of_groups)
    except Exception as e:
        session.clear()
        text = f"An error occurred: {str(e)}"
        return render_template("login.html", erro=True, text=text)


@app.route('/new_group', methods=["GET", "POST"])
@login_required
def new_group():
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    date = date_now()

    if request.method == 'POST':
        try:
            cursor.execute("SELECT * FROM groups")
            groups = cursor.fetchall()

            cursor.execute("SELECT * FROM groups_users")
            participants_all = cursor.fetchall()

            cursor.execute("SELECT DISTINCT group_id, date FROM draw")
            draws = cursor.fetchall()

            list_of_groups = formate_list_of_groups(groups, participants_all, id, draws)
            for input, value in request.form.items():
                if not value:
                    text = f"Error: {input} must me provided"
                    return render_template("home.html", erro=True, text=text, nav=True, user=user, groups=list_of_groups)
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
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("home.html", nav=True, erro=True, text=text, user=user)
    
    else:
        return redirect("/home")


@app.route('/modal_group/<group_id>', methods=["GET"])
@login_required
def modal_group(group_id):
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    try:
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
            return jsonify({'error': 'Grupo not found'})
    except Exception as e:
        text = f"An error occurred: {str(e)}"
        return render_template("home.html", nav=True, erro=True, text=text, user=user)


@app.route('/join_group', methods=['GET', 'POST'])
@login_required
def join_group():
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    date = date_now()

    try:
        if request.method == 'POST':
            group_id = request.form.get("group_id")
            cursor.execute("INSERT INTO groups_users (user_id, group_id, addtion_date) VALUES (?, ?, ?)", (id, group_id, date))
            db.commit()
            return redirect("/home")
        
        else:
            return redirect("/home")  
        
    except Exception as e:
        text = f"An error occurred: {str(e)}"
        return render_template("home.html", nav=True, erro=True, text=text, user=user)


@app.route('/leave_group/<group_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def leave_group(group_id=None, user_id=None):
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    try:
        if user_id != '0':
            # Owner deleting someone
            print("entrou no if")
            cursor.execute("DELETE FROM groups_users WHERE group_id = ? AND user_id = ?", (group_id, user_id,))
            db.commit()
            return redirect(f"/group/{group_id}")
        else:
            # Member deleting her/him self
            print("entrou no else")
            cursor.execute("DELETE FROM groups_users WHERE group_id = ? AND user_id = ?", (group_id, id,))
            db.commit()
            return redirect("/home")
    except Exception as e:
        text = f"An error occurred: {str(e)}"
        return render_template("home.html", nav=True, erro=True, text=text, user=user)


@app.route('/group/<group_id>', methods=['GET', 'POST'])
@login_required
def group(group_id):
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    release_santa = False

    if request.method == 'GET':
        try:
            santa_gift_options = None
            cursor.execute("SELECT b.* FROM groups_users a JOIN users b ON a.user_id = b.id WHERE a.group_id = ? AND a.user_id <> ?", (group_id, id))
            participants = cursor.fetchall()
            
            if len(participants) >= 2:
                release_santa = True

            cursor.execute("SELECT id FROM groups_users WHERE group_id = ? AND user_id = ?", (group_id, id,))
            group_user_id = cursor.fetchone()
            
            group_user_id = group_user_id['id']

            cursor.execute("SELECT c.* FROM groups_users a JOIN group_user_option b ON a.id = b.group_user_id JOIN gift_option c ON c.id = b.gift_option_id WHERE a.id = ?", (group_user_id, ))
            gift_options = cursor.fetchall()

            cursor.execute("SELECT a.*, b.name as creator, b.email FROM groups a LEFT JOIN users b ON a.owner_id = b.id WHERE a.id = ?", (group_id, ))
            group = cursor.fetchone()

            # I am the "took" one and the person I retrieved is the "taken" one
            cursor.execute("SELECT a.taken_id, a.date, b.name, b.email, b.gender, b.birth FROM draw a JOIN users b ON a.taken_id = b.id WHERE a.took_id = ? AND a.group_id = ?", (id, group_id,))
            draw = cursor.fetchone()

            if draw:
                if draw['taken_id']:
                    cursor.execute("SELECT id FROM groups_users WHERE group_id = ? AND user_id = ?", (group_id, draw['taken_id'],))
                    group_taken_id = cursor.fetchone()
                    group_taken_id = group_taken_id['id']

                    cursor.execute("SELECT c.* FROM groups_users a JOIN group_user_option b ON a.id = b.group_user_id JOIN gift_option c ON c.id = b.gift_option_id WHERE a.id = ?", (group_taken_id, ))
                    santa_gift_options = cursor.fetchall()

            owner = group['owner_id'] == id

            return render_template("group.html", nav=True, user=user, owner=owner, participants=participants, gift_options=gift_options, draw=draw, group=group, santa_gift_options=santa_gift_options, release_santa=release_santa)
        
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("home.html", nav=True, erro=True, text=text, user=user)


@app.route('/draw', methods=['GET', 'POST'])
@login_required
def draw():
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    date = date_now()

    if request.method == 'POST':
        try:
            group_id = request.form.get("group_id")
            cursor.execute("SELECT b.name, b.id FROM groups_users a JOIN users b ON a.user_id = b.id WHERE a.group_id = ?", (group_id, ))
            part_all = cursor.fetchall()

            if len(part_all) < 2:
                return redirect(f"/group/{group_id}")
            else:

                part_list = [part for part in part_all]
                random.shuffle(part_list)

                # print('LISTA EMBARALHADA', part_list)

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
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("home.html", nav=True, erro=True, text=text, user=user)
    else:
        return redirect(f"/group/{group_id}")


@app.route('/new_gift/<gift_id>', methods=['GET', 'POST', 'DELETE'])
@app.route('/new_gift/', methods=['GET', 'POST'])
@login_required
def new_gift(gift_id=None):
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    if request.method == 'POST':
        group_id = request.form.get("group_id")
        try:
            if gift_id:
                cursor.execute("DELETE FROM gift_option WHERE id = ?", (gift_id, ))
                db.commit()
                return redirect(f"/group/{group_id}")
            else:
                gift = request.form.get("gift")
                description = request.form.get("description")
                
                cursor.execute("INSERT INTO gift_option (gift, description) VALUES (?, ?)", (gift, description, ))
                db.commit()
                gift_option_id = cursor.lastrowid

                cursor.execute("SELECT * FROM groups_users WHERE group_id = ?  AND user_id = ?", (group_id, id, ))
                group_user_id = cursor.fetchone()
                group_user_id = group_user_id['id']

                cursor.execute("INSERT INTO group_user_option (group_user_id, gift_option_id) VALUES (?, ?)", (group_user_id, gift_option_id, ))
                db.commit()

                return redirect(f"/group/{group_id}")
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("home.html", nav=True, erro=True, text=text, user=user)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    if request.method == 'GET':
        return render_template('profile.html', nav=True, user=user)
    else:
        try:
            for input, value in request.form.items():
                if not value:
                    text = f"Error: {input} must me provided"
                    return render_template("profile.html", nav=True, erro=True, text=text, user=user)
            
            email = request.form.get("email")
            name = request.form.get("name")
            birth = request.form.get("birthdate")
            gender = request.form.get("gender")

            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user_exists = cursor.fetchone()
            email_exists = user_exists['id'] != id
            if email_exists:
                text = f"Error: Email already being used."
                return render_template("profile.html", nav=True, erro=True, text=text, user=user)

            cursor.execute("UPDATE users SET email = ?, name = ?, birth = ?, gender = ? WHERE id = ?", (email, name, birth, gender, id, ))
            db.commit()
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
            user = cursor.fetchone()

            return render_template('profile.html', nav=True, user=user, success=True, text='Profile data updated!')
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("profile.html", nav=True, erro=True, text=text, user=user)


@app.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    if request.method == 'GET':
        return render_template('profile.html', nav=True, user=user)
    else:
        try:
            for input, value in request.form.items():
                if not value:
                    text = f"Error: {input} must me provided"
                    return render_template("profile.html", nav=True, erro=True, text=text, user=user)
            
            oldPassword = request.form.get("oldPassword")
            newPassword = request.form.get("newPassword")

            if not check_password_hash(user['password_hash'], oldPassword):
                text = f"Error: The current password is incorect"
                return render_template("profile.html", nav=True, erro=True, text=text, user=user)
            
            hash = generate_password_hash(newPassword)
            
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash, id, ))
            db.commit()

            return render_template('profile.html', nav=True, user=user, success=True, text='Password was updated!')
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("profile.html", nav=True, erro=True, text=text, user=user)
   
        
@app.route('/delete_group/<group_id>', methods=['GET', 'POST'])
@login_required
def delete_group(group_id):
    db = get_db()
    cursor = db.cursor()
    id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()

    if request.method == 'GET':
        return render_template('profile.html', nav=True, user=user)
    else:
        try:
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id, ))
            db.commit()

            cursor.execute("DELETE FROM groups_users WHERE group_id = ?", (group_id, ))
            db.commit()

            cursor.execute("DELETE FROM draw WHERE group_id = ?", (group_id, ))
            db.commit()

            return redirect("/home")
        except Exception as e:
            text = f"An error occurred: {str(e)}"
            return render_template("home.html", nav=True, erro=True, text=text, user=user)


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