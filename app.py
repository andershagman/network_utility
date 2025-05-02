from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json

app = Flask(__name__)
app.secret_key = 'hemlig-nyckel'

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
    data = [
        {"name": "Switch 1", "ports": 48, "active": 42},
        {"name": "Switch 2", "ports": 24, "active": 18},
    ]
    columns = [
        {"title": "Namn", "data": "name"},
        {"title": "Totalt antal portar", "data": "ports"},
        {"title": "Aktiva portar", "data": "active"},
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
