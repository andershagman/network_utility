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

@app.route('/stats')
def stats():
    # Simulerad data – byt ut mot din egen logik
    switches = [
        {'name': 'Switch 1', 'free_ports': 12},
        {'name': 'Switch 2', 'free_ports': 5},
    ]
    return render_template('stats.html', switches=switches)

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/groups')
def groups():
    return render_template('groups.html')

@app.route('/permissions')
def permissions():
    return render_template('permissions.html')

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
