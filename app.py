from flask import Flask, render_template, url_for, request, jsonify, send_from_directory, redirect,session

import firebase_admin
from firebase_admin import credentials, firestore, auth

app = Flask(__name__)

cred = credentials.Certificate(
    'oreoinverse-1c6b6-firebase-adminsdk-imbmo-dbd085f8bc.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('login_signup.html')

# Add other routes and functionalities as needed

@app.route('/verifyToken', methods=['POST'])
def verify_token():
    global email
    data = request.get_json()
    id_token = data.get('idToken')
    email = data.get('email')
    print(data)
    try:
        decoded_token = auth.verify_id_token(id_token)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to verify token', 'details': str(e)}), 500

@app.route('/dashboard')
def dashboard():
        global email
        print(email)
        return render_template('dashboard.html', mail=email)


if __name__ == '__main__':
    app.run(debug=True)
