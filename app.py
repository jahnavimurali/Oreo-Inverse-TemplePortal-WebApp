from flask import Flask, render_template, url_for, request, jsonify, send_from_directory, redirect,session

import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore import ArrayUnion
from datetime import datetime 


app = Flask(__name__)

cred = credentials.Certificate(
    'oreoinverse-1c6b6-firebase-adminsdk-imbmo-dbd085f8bc.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('login_signup.html')


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
    
@app.route('/signup')
def signup():
    global email
    email = request.form.get('email')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
        global email
        query = db.collection('Temples').where(filter=FieldFilter('adminEmail', '==', email)).stream()
        templeData = [doc.to_dict() for doc in query]    
        print(email)
        return render_template('dashboard.html', mail=email)

@app.route('/alerts')
def alerts():
    global email
    print(email)
    alerts_query = db.collection('Temples').where(filter=FieldFilter('adminEmail', '==', email)).stream()
    alerts = [doc.to_dict() for doc in alerts_query]
    return render_template('alerts.html', alerts=alerts[0].get('alerts'))

@app.route('/view_services')
def view_services():
    global email
    print(email)
    templeData = db.collection('Temples').where(filter=FieldFilter('adminEmail', '==', email)).stream()
    Data = [doc.to_dict() for doc in templeData]
    print(Data)
    return render_template('view_services.html', pujas=Data[0].get('Puja'), darshans=Data[0].get('Darshan'),)  

@app.route('/editServices')
def editServices():
    return render_template('editServices.html')

@app.route('/edit_details')
def edit_details():
    return render_template('edit_details.html')

@app.route('/logout')
def logout():
    return redirect(url_for('index'))


@app.route('/add_alert', methods=['POST'])
def add_alert():
    global email
    new_alert = request.form.get('alert_message')
    try:
        docs =  db.collection('Temples').where(filter=FieldFilter('adminEmail', '==', email)).get()
        for doc in docs:
            doc_ref = db.collection('Temples').document(doc.id)
            doc_ref.update({"alerts": ArrayUnion([new_alert])})
    except Exception as e:
        print(f"Error adding alert: {e}")
    return redirect(url_for('alerts'))

@app.route('/add_darshan', methods=['POST'])
def add_darshan():
    darshan_name = request.form.get('darshanName')
    darshan_desc = request.form.get('darshanDesc')
    darshan_fee = request.form.get('darshanFee')
    slots_data = []
    
    for key in request.form.keys():
        if key.startswith('slots['):
            slot_index, slot_key = key.split('[')[1].split(']')[0], key.split('[')[2].split(']')[0]
            if len(slots_data) <= int(slot_index):
                slots_data.append({'dateTime': None, 'maxBookings': 0, 'currentBookings': 0})
            if slot_key == 'dateTime':
                slots_data[int(slot_index)][slot_key] = datetime.strptime(request.form[key], '%Y-%m-%dT%H:%M')
            else:
                slots_data[int(slot_index)][slot_key] = int(request.form[key])
    
    docs =  db.collection('Temples').where(filter=FieldFilter('adminEmail', '==', email)).get()
    for doc in docs:
        temple_doc_ref = db.collection('Temples').document(doc.id)
        temple_doc_ref.update({
            'Darshan': firestore.ArrayUnion([{
                'darshanName': darshan_name,
                'darshanDesc': darshan_desc,
                'darshanFee': darshan_fee,
                'Slots': slots_data
            }])
        })

    return redirect(url_for('editServices'))

@app.route('/add_puja', methods=['POST'])
def add_puja():
    puja_name = request.form.get('pujaName')
    puja_desc = request.form.get('pujaDesc')
    puja_fee = request.form.get('pujaFee')
    puja_slots_data = []

    for key in request.form.keys():
        if key.startswith('pujaSlots['):
            slot_index, slot_key = key.split('[')[1].split(']')[0], key.split('[')[2].split(']')[0]
            if len(puja_slots_data) <= int(slot_index):
                puja_slots_data.append({'dateTime': None, 'maxBookings': 0, 'currentBookings': 0})
            if slot_key == 'dateTime':
                puja_slots_data[int(slot_index)][slot_key] = datetime.strptime(request.form[key], '%Y-%m-%dT%H:%M')
            else:
                puja_slots_data[int(slot_index)][slot_key] = int(request.form[key])
    
    docs =  db.collection('Temples').where(filter=FieldFilter('adminEmail', '==', email)).get()
    for doc in docs:
        temple_doc_ref = db.collection('Temples').document(doc.id)
        temple_doc_ref.update({
            'Puja': firestore.ArrayUnion([{
                'pujaName': puja_name,
                'pujaDesc': puja_desc,
                'pujaFee': puja_fee,
                'Slots': puja_slots_data
            }])
        })
    return redirect(url_for('editServices'))



if __name__ == '__main__':
    app.run(debug=True)
