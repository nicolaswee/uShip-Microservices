from flask import Flask, request, jsonify
from pymongo import MongoClient, ReturnDocument
from flask_cors import CORS
import jwt
import os  # REQUIRE pip install dnspythonh
import bcrypt
from dotenv import load_dotenv
from datetime import date
load_dotenv()

app = Flask(__name__)
mongo = os.getenv('MONGODB')
client = MongoClient(mongo)
db = client.users_db
user = db.users
CORS(app)


@app.route("/login", methods=["POST"])
def user_login():

    data = request.get_json()
    # JSON should be {username: ##, password: ##}
    value = user.find_one({'email': data['username']})

    if value is not None:
        if bcrypt.checkpw(data['password'].encode('utf8'), value['password']):
            encoded_jwt = jwt.encode({'email': value['email']}, os.getenv('SECRET'),algorithm='HS256').decode('utf-8')
            # print(encoded_jwt)
            # print('logged in')
            return jsonify({'status': True, 'token': str(encoded_jwt), 'name': value['name']}), 200
            # decoded_jwt = jwt.decode(encoded_jwt, 'secret', algorithms=['HS256'])
            # print(decoded_jwt)

        # print('Wrong username or password')
        return jsonify({'status': False, 'message': 'Wrong email or password'}), 401 

    # print("No such account found")
    return jsonify({'status': False, 'message': 'No such account registered'}), 401 


@app.route("/register", methods=["POST"])
def user_register():

    data = request.get_json()

    # If the user's password and confirmed password is different
    if data['password'] != data['confirmPassword']:
        return jsonify({'status': False, 'message': 'Password and confirmed password is different'}), 401

    existing_user = user.find_one({'email': data['email']})

    if existing_user is None:  # If the username is not taken, prevents duplicate entries
        encryptedPassword = bcrypt.hashpw(
            data['password'].encode('utf8'), bcrypt.gensalt())

        query = {
            'email': data['email'],
            'password': encryptedPassword,
            'type': 'customer',
            'name': data['name']
        }

        status = user.insert_one(query)

        print(status)
        if status:
            print('Account has been created successfully')
            return jsonify({'status': True, 'message': 'Account created successfully'}), 200

    print('Username is already in use')
    return jsonify({'status': False, 'message': 'Username is already in uset'}), 401

@app.route("/me", methods =['GET'])
def me():
    token = request.headers.get('Authorization')
    if token == None or token == '':
        return jsonify({'status':False, 'message':'Empty token'}), 401 

    try:
        emailJSON = jwt.decode(token,os.getenv('SECRET'), algorithms='HS256')
    except:
        return jsonify({'status': False, 'message':'Invalid token'}), 401 

    try:
        existing_user = user.find_one({'email':emailJSON['email']})
        userJSON = {'name': existing_user['name'], 'email':existing_user['email'], 'userType':existing_user['type']}
        return jsonify({'status':True, 'user':userJSON}), 200
        
    except:
        return jsonify({'status': False, 'message': 'No such user'}), 401 



@app.route("/registerSupplier", methods = ['POST'])
def registerSupplier():
    data = request.get_json()

    # If the user's password and confirmed password is different
    if data['password'] != data['confirmPassword']:
        return jsonify({'status': False, 'message': 'Password and confirmed password is different'}), 401

    existing_user = user.find_one({'email': data['email']})

    if existing_user is None:  # If the username is not taken, prevents duplicate entries
        encryptedPassword = bcrypt.hashpw(
            data['password'].encode('utf8'), bcrypt.gensalt())

        query = {
            'email': data['email'],
            'password': encryptedPassword,
            'type': 'supplier',
            'name': data['name'],
            'created': str(date.today())
        }

        status = user.insert_one(query)

        if status:
            print('Account has been created successfully')
            return jsonify({'status': True, 'message': 'Account created successfully'}), 200

    print('Username is already in use')
    return jsonify({'status': False, 'message': 'Username is already in uset'}), 401

@app.route("/getAllSupplier", methods = ['GET'])
def getAllSupplier():
    result = user.find({"type":'supplier'}).sort('_id', -1)

    if result:
        suppliers = []
        for supplier in result:
            supplier_dict = {
                'email':supplier['email'],
                'name':supplier['name'],
                'date': supplier['created']
            }
            suppliers.append(supplier_dict)
        return jsonify({'status': True, 'message':suppliers}), 200
    
    return jsonify({'status': False, 'message':'Error, no suppliers registered'}), 401


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 5007)))
    # app.run(port=5007, debug=True)
