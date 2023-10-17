from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            print("USER ID", session.get("user_id"))
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def formate_list_of_groups(list, participants, id):
    list_of_groups = [dict(row) for row in list]

    for group in list_of_groups:
        group['participants'] = []
        group['owner'] = False
        group['member'] = False
        if group['owner_id'] == id:
            group['owner'] = True
        for participant in participants:
            if participant['group_id'] == group['id']:
                group['participants'].append(participant['user_id'])
            if participant['user_id'] == id:
                group['member'] = True
    
    return list_of_groups


def date_now():
    data_atual = datetime.now()
    data_formatada = data_atual.strftime("%Y-%m-%d")

    return data_formatada

