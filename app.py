from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)
app.secret_key = 'hemlig-nyckel'

client = MongoClient("mongodb://localhost:27017")
db = client["switchdb"]
collection = db["switches"]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'lösen':
            session['logged_in'] = True
            return redirect(url_for('switches'))
        else:
            return render_template('login.html', error='Fel användarnamn eller lösenord')
    return render_template('login.html')

@app.route('/switches')
def switches():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('switch.html')

# Gemensam tabellhantering

@app.route("/stats")
def stats():
    switches = collection.find({}, {"name": 1, "used": 1, "free": 1, "used_percent": 1, "_id": 0})
    data = [
        {
            "name": sw["name"],
            "used": sw.get("used", 0),
            "free": sw.get("free", 0),
            "used_percent": f"{sw.get('used_percent', 0)}%"
        }
        for sw in switches
    ]
    columns = [
        {"title": "Namn", "data": "name", "type": "text"},
        {"title": "Använda", "data": "used", "type": "numeric"},
        {"title": "Lediga", "data": "free", "type": "numeric"},
        {"title": "Använda %", "data": "used_percent", "type": "numeric"},
    ]
    return render_template("table_view.html", title="Statistik", columns=columns, data=data)

@app.route("/users")
def users():
    data = [
        {"username": "alice", "email": "alice@example.com", "role": "admin"},
        {"username": "bob", "email": "bob@example.com", "role": "user"},
    ]
    columns = [
        {"title": "Användarnamn", "data": "username"},
        {"title": "E-post", "data": "email"},
        {"title": "Roll", "data": "role"},
    ]
    return render_template("table_view.html", title="Användare", columns=columns, data=data)


@app.route("/groups")
def groups():
    data = [
        {"name": "Nätverksadmin", "members": 5},
        {"name": "Gäster", "members": 12},
    ]
    columns = [
        {"title": "Gruppnamn", "data": "name"},
        {"title": "Antal medlemmar", "data": "members"},
    ]
    return render_template("table_view.html", title="Grupper", columns=columns, data=data)


@app.route("/permissions")
def permissions():
    data = [
        {"permission": "access_ports", "description": "Kan se portar"},
        {"permission": "edit_users", "description": "Kan ändra användare"},
    ]
    columns = [
        {"title": "Behörighet", "data": "permission"},
        {"title": "Beskrivning", "data": "description"},
    ]
    return render_template("table_view.html", title="Behörigheter", columns=columns, data=data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/save-settings", methods=["POST"])
def save_settings():
    data = request.json
    with open("config.json", "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
