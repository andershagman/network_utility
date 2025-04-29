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
