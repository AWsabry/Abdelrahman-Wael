from flask import Flask, redirect, url_for, render_template, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import pyrebase
from getpass import getpass
from google.cloud.firestore_v1 import Increment

app = Flask(__name__)

cred = credentials.Certificate(
    "trutech-464cb-firebase-adminsdk-4v8do-00354706db.json")

firebaseConfig = {
    'apiKey': "AIzaSyBuY3CpF5V6Kceyr5QelfTRocZyIVhvyhw",
    'authDomain': "trutech-464cb.firebaseapp.com",
    'databaseURL': "https://trutech-464cb-default-rtdb.firebaseio.com",
    'projectId': "trutech-464cb",
    'storageBucket': "trutech-464cb.appspot.com",
    'messagingSenderId': "756831507071",
    'appId': "1:756831507071:web:b77aebd7671760cfc4e54a",
    'measurementId': "G-ZV3N9KJ058"
}

firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


db = firestore.client()


@app.route('/', methods=['GET', 'POST'])
@app.route("/index")
def index():
    from google.cloud import firestore
    docs = db.collection(u'users').order_by(
        u'createdAt', direction=firestore.Query.DESCENDING).stream()
    return render_template('index.html', docs=docs)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        auth = firebase.auth()
        email = request.form['email']
        password = request.form['password']
        user = auth.sign_in_with_email_and_password(email, password)
        if(user):
            return redirect('/users')
        if(user == False):
            return 'Login Failed'

    return render_template('login.html', title='login')


@app.route("/users")
def users():
    from google.cloud import firestore
    docs = db.collection(u'users').order_by(
        u'createdAt', direction=firestore.Query.DESCENDING).stream()
    return render_template('users.html', docs=docs)



@app.route("/orders")
def orders():
    from google.cloud import firestore
    docs = db.collection(u'orders').order_by(
        u'createdAt', direction=firestore.Query.DESCENDING).stream()
    return render_template('orders.html', docs=docs)


@app.route("/addcommission", methods=['POST', 'GET'])
def addcommission():
    if request.method == "POST":
        try:
            salesEmail = request.form['salesEmail']
            salesPercentage = request.form['salesPercentage']
            TotalCommissionCalculation = request.form['TotalCommissionCalculation']
            salesWallet = float(salesPercentage) * \
                float(TotalCommissionCalculation)
            new_doc_ref = db.collection('sales').document(salesEmail)
            new_doc_ref.update({
                'salesPercentage': float(salesPercentage),
                'salesWallet': Increment(salesWallet),
                'TotalCommissionCalculation': 0
            })
            print(salesWallet),
        except Exception as e:
            print(str(e))
    else:
        print("ERROR")
    return render_template('addcommission.html', title='addcommission')


@app.route("/products")
def products():
    docs = db.collection(u'products').order_by(u'category').stream()
    auth = firebase.auth()
    print(auth.current_user)
    # ID = uuid.uuid4()
    delete = db.collection(u'products').document()
    return render_template('products.html', docs=docs, delete=delete)


@app.route("/sales")
def sales():
    docs = db.collection(u'sales').stream()
    return render_template('sales.html', docs=docs)


@app.route("/salesOrders", methods=['POST', 'GET'])
def salesOrders():
    from google.cloud import firestore
    if request.method == "POST":
        try:
            salesEmail = request.form['salesEmail']
        except Exception as e:
            print(str(e))
    else:
        print("ERROR")
        docs = db.collection(u'salesOrders').document(salesEmail).collection('salesOrders').order_by(u'CreatedAt', direction= firestore.Query.DESCENDING).stream()
    return render_template('salesOrders.html', docs=docs)


@app.route("/addProduct", methods=['POST', 'GET'])
def addProduct():
    if request.method == "POST":
        try:
            pname = request.form['pname']
            Description = request.form['Description']
            Price = request.form['Price']
            img = request.files['img']
            auth = firebase.auth()
            email = "admin@admin.com"
            password = "123456"
            path_on_cloud = pname
            path_local = img
            ID = uuid.uuid4()
            user = auth.sign_in_with_email_and_password(email, password)
            storage.child(path_on_cloud).put(path_local, user['idToken'])
            url = storage.child(path_on_cloud).get_url(user['idToken'])
            new_doc_ref = db.collection('products').document(str(ID))
            category = request.form['Category']
            if category == 'a':
                category = 'tv'
            elif category == 'b':
                category = "satalite"
            elif category == 'c':
                category = "security"
            elif category == 'd':
                category = "electric"
            elif category == 'e':
                category = "network"
            elif category == 'f':
                category = "sound"
            elif category == 'g':
                category = "other"
            new_doc_ref.set({
                'name': pname,
                'price': float(Price),
                'image': url,
                'id': str(ID),
                'description': Description,
                'category': category
            })
            print(pname)
            print(Description)
            print(Price)
        except Exception as e:
            print(str(e))
    else:
        print("ERROR")
    return render_template('addProduct.html', title='addProduct')


@app.route("/addSales", methods=['POST', 'GET'])
def addSales():
    if request.method == "POST":
        try:
            cart = []
            salesName = request.form['salesName']
            salesEmail = request.form['salesEmail']
            salesPassword = request.form['salesPassword']
            salesGender = request.form['salesGender']
            salesNationalId = request.form['salesNationalId']
            salesPhoneNumber = request.form['salesPhoneNumber']
            salesPercentage = request.form['salesPercentage']
            salesAddress = request.form['salesAddress']
            auth = firebase.auth()
            salesuser = auth.create_user_with_email_and_password(
                salesEmail, salesPassword)
            user = auth.refresh(salesuser['refreshToken'])
            new_doc_ref = db.collection('sales').document(salesEmail)
            new_doc_ref.set({
                'salesName': salesName,
                'salesEmail': salesEmail,
                'salesPassword': salesPassword,
                'salesNationalId': salesNationalId,
                'salesGender': salesGender,
                'salesPhoneNumber': salesPhoneNumber,
                'salesPercentage': float(salesPercentage),
                'salesAddress': salesAddress,
                'salesWallet': 0,
                'cart': cart,
                'TotalOrder': 0,
                'TotalCommissionCalculation': 0,
            })
            print(salesName),
            print(salesEmail),
            print(salesGender)
        except Exception as e:
            print(str(e))
    else:
        print("ERROR")
    return render_template('addSales.html', title='addSales')


if __name__ == '__main__':

    app.run(port=5000, debug=True)
