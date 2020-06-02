from flask import Flask, request, jsonify, url_for
import requests
from pymongo import MongoClient
from flask_cors import CORS
import os
import codecs
from dotenv import load_dotenv
import pika
import json
import base64
import shortuuid
import random
from io import BytesIO
load_dotenv()

app = Flask(__name__)
mongo = os.getenv('MONGODB')
client = MongoClient(mongo)
db = client.cart_db
cart = db.cart
CORS(app)

url = os.getenv('AMQP_LINK')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
exchangename="uship"
channel.exchange_declare(exchange=exchangename, exchange_type='topic')

@app.route("/addProduct", methods=['POST'])
def add_product():
    # e.g body = {'email': 'test@test.com','uid': 'test'}
    oid = shortuuid.ShortUUID().random(length=6)
    data = request.get_json()
    email = data['email']
    uid = data['uid']

    current_cart = cart.find_one({'email':email})

    if current_cart:

        if current_cart['status'] == 'Pending':
            uid_list = current_cart['uid']

            if any(uid in sl for sl in uid_list):
                return jsonify({'result': 'Product already added to cart'}), 401

            uid_list.append([uid,0])
            status = cart.update_one({'email':email},{"$set": { "uid": uid_list }})

            if status:
                return jsonify({'result': 'Product added to cart'}), 200

            return jsonify({'result': 'Product cannot be added to cart'}), 500

        else:
            return jsonify({'result':'Cart is not in pending stage'}), 402

    status = cart.insert_one({'email':email,'status':'Pending','uid':[[uid,0]],'price':0,'oid':oid})

    if status:
        return jsonify({'result': 'Product added to cart'}), 200

    return jsonify({'result': 'Product cannot be added to cart'}), 500

@app.route("/removeProduct", methods=['POST'])
def remove_product():
    # e.g body = {'email': 'test@test.com','uid': 'test'}
    data = request.get_json()
    email = data['email']
    uid = data['uid']

    current_cart = cart.find_one({'email':email})
    if current_cart:

        if current_cart['status'] == 'Pending':
            uid_list = current_cart['uid']

            if any(uid in sl for sl in uid_list):
                uid_list.remove([uid,0])
                status = cart.update_one({'email':email},{"$set": { "uid": uid_list }})

                if status:
                    return jsonify({'result': 'Product removed from the cart'}), 200

                return jsonify({'result': 'Product cannot be removed from cart'}), 500

            else:
                return jsonify({'result': 'Product is not in cart'}), 401

        else:
            return jsonify({'result':'Cart is not in pending stage'}), 402

    return jsonify({'result': 'No cart'}), 403

@app.route('/findByUser/<string:email>', methods=['GET'])
def find_by_user(email):
    output = []
    current_cart = cart.find_one({'email': email})

    if current_cart:
        items_id = current_cart['uid'][::-1]
        URL = os.getenv('PRODUCT_MICROSERVICE_URL') + "/findById"

        for item_id in items_id:
            r = requests.get(url = URL, params = {"uid": item_id[0]})
            product_data = r.json()

            p = product_data['result'][0]

            if p:
                output.append({'UID': p['UID'], 'ProductId': str(p['ProductId']), 'ProductName': p['ProductName'], 'ProductDescription': p['ProductDescription'], 'Country': p['Country'], 'Category': p['Category'], 'Image': p['Image'], 'Price':item_id[1]})
        
        if len(output) == 0:
            return jsonify({'result':'Your cart is empty'}), 500

        return jsonify({'result': output, 'status': current_cart['status'], 'price':current_cart['price'], 'oid':current_cart['oid']}), 200

    return jsonify({'result': "Your cart is empty"}), 500


#Find by status
@app.route('/findByStatus', methods=['GET'])
def find_by_status():
    data = request.args.get('status')
    output = []
    URL = os.getenv('PRODUCT_MICROSERVICE_URL') + "/findById"
    
    for result in cart.find({'status':data}):

        number_of_items = len(result['uid'])

        item_array = []
        for items in result['uid']:
            r = requests.get(url = URL, params = {"uid": items[0]})
            product_data = r.json()

            p = product_data['result'][0]

            if p:
                item_array.append({'UID': p['UID'], 'ProductId': str(p['ProductId']), 'ProductName': p['ProductName'], 'ProductDescription': p['ProductDescription'], 'Country': p['Country'], 'Category': p['Category'], 'Image': p['Image'],'Price':items[1]})
        output.append({'email':result['email'], 'numberOfItems':number_of_items,'product':item_array,'status':result['status']})

    if len(output) == 0:
        return jsonify({'result':'No users match the status'}), 401

    return jsonify({'result':output}), 200

@app.route('/updateStatus', methods=['PUT'])
def update_status():
    status = request.form.get("status")
    email = request.form.get('email')

    current_cart = cart.find_one({'email': email})

    if current_cart:
        result = cart.update_one({'email':email}, {"$set" : {'status':status}})
        if result:
            if status == "Checkout":
                body = {"subject": "cart_checkout", "to": "ushipnotification@gmail.com", "admin": True}
                body = json.dumps(body, default=str)
                channel.queue_declare(queue='notification', durable=True)
                channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification')
                channel.basic_publish(exchange=exchangename, routing_key="cart_checkout.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))
            return jsonify({'result':'Status has been updated to '+status}), 200
        
        return jsonify({'result':'Unable to change cart status'}), 400
    
    return jsonify({'result':'User cart does not exist'}), 404

@app.route('/updatePrice', methods=['PUT'])
def update_price():
    data = request.get_json()
    email = data['email']

    current_cart = cart.find_one({'email':email})
    products = data['products']

    if current_cart:
        output = []

        price = 0
        for item in current_cart['uid']:
            if item[0] in products:
                item[1] = float(products[item[0]])
                price += float(products[item[0]])

            output.append(item)

        result = cart.update_one({'email':email}, {"$set" : {'uid':output, 'status':'Payment', 'price': price}})

        if result:
            body = {"subject": "cart_payment", "to": email, "admin": False}
            body = json.dumps(body, default=str)
            channel.queue_declare(queue='notification', durable=True)
            channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification')
            channel.basic_publish(exchange=exchangename, routing_key="cart_payment.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))
            return jsonify({'result':'Price updated'}), 200

        return jsonify({'result':'Unable to update price'}), 500

    return jsonify({'result':'The user does not have a cart'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5002)))
    # app.run(port=5002, debug=True)