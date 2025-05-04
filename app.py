from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from utils.update_idle_time import update_idle_times
from pymongo import MongoClient
import json

app = Flask(__name__)
app.secret_key = 'hemlig-nyckel'

client = MongoClient("mongodb://localhost:27017")
db = client["network"]
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

@app.route("/api/fetch-portinfo", methods=["POST"])
def fetch_portinfo():
    data = request.json
    name = data.get("name")

    switch = collection.find_one({"name": name})

    if not switch or "ip" not in switch:
        return {"error": "Switch not found or missing IP"}, 404

    update_idle_times(switch["ip"], switch["name"])
    return {"status": "ok"}

@app.route("/api/get_switch", methods=["GET"])
def get_switch():
    name = request.args.get("name")
    switch = collection.find_one({"name": name}, {"_id": 0})
    if not switch:
        return {"error": "Not found"}, 404
    return switch

@app.route("/api/switch-names")
def get_switch_names():
    names = collection.distinct("name")
    return jsonify(names)

@app.route('/switches')
def switches():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('switch.html')

@app.route("/stats")
def stats():
    switches = collection.find({}, {"name": 1, "ip": 1,  "used": 1, "free": 1, "used_percent": 1, "_id": 0})
    data = [
        {
            "name": sw["name"],
            "ip": sw["ip"],
            "used": sw.get("used", 0),
            "free": sw.get("free", 0),
            "used_percent": f"{sw.get('used_percent', 0)}%"
        }
        for sw in switches
    ]
    columns = [
        {"title": "Namn", "data": "name", "type": "text"},
        {"title": "IP-adress", "data": "ip", "type": "text"},
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
