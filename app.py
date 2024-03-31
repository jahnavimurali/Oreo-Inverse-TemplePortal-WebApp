from flask import Flask, render_template, url_for, request, jsonify, send_from_directory, redirect,session

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

cred = credentials.Certificate(
    'oreoinverse-1c6b6-firebase-adminsdk-imbmo-dbd085f8bc.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('dashboard.html')

# Add other routes and functionalities as needed

if __name__ == '__main__':
    app.run(debug=True)
