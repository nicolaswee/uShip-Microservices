from flask import Flask, render_template, request, redirect, url_for,jsonify, session, Markup
from pymongo import MongoClient
from flask_cors import CORS
import os 
import codecs
from dotenv import load_dotenv
import pika
import json
import stripe
import requests
load_dotenv()

app = Flask(__name__)
app.secret_key = b'{\x80\xc8v\x7f\xa08\xd9\x9aJr\xf2^\xacI\xb7'
mongo = os.getenv('MONGODB')
client = MongoClient(mongo)
CARTURL = os.getenv('CART_MICROSERVICE_URL') 
paymentdb = client.payments_db
payments = paymentdb.payment
CORS(app)

url = os.getenv('AMQP_LINK')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
exchangename="uship"
channel.exchange_declare(exchange=exchangename, exchange_type='topic')

ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
ACCESS_SECRET_KEY = os.getenv('ACCESS_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
pub_key = os.getenv('pub_key')
secret_key = os.getenv('secret_key')
stripe.api_key = secret_key

@app.route('/')
def index():
    return render_template('index.html', pub_key=pub_key)

@app.route('/details/<string:email>', methods=['GET'])
def checkout(email):
    # to get name here
    total = 0
    text = "Total amount to pay :"
    product = requests.get(url = CARTURL + 'findByUser/' +email, params = {"status":'Payment'})
    session['email'] = email
    if(product):
        cartitem= product.json()
        items = []
        htmloutput= '<div class="product-container">'
        for o in cartitem['result']:
            htmloutput += '<div class="product">'
            htmloutput += '<div class="image-container">'
            htmloutput += '<img src="' + o['Image'] + '">'
            htmloutput += '</div>'
            htmloutput += '<div class="details-container">'
            htmloutput += '<h5>' + o['ProductName'] + '</h5>'
            htmloutput += '<p>' + o['ProductDescription'] + '</p>'
            htmloutput += '<p>' + o['Country'] + '</p>'
            htmloutput += '<p>$' + str(o['Price']) + '</p>'
            htmloutput += '</div>'
            htmloutput += '</div>'
            total += float(o['Price'])
            items.append([o['ProductName'],o['Price']])
        
        session['items'] = items
        session['oid'] = cartitem['oid']
        htmloutput += "</div>"
        output = Markup(htmloutput)
        return render_template('index.html', pub_key=pub_key, email=email, output=output, text=text, total=total)
    else:
        reply = "no items in cart"
        return render_template('index.html', pub_key=pub_key, email=email, reply=reply)

@app.route('/purchasesuccessful')
def purchasesuccessful():
    if 'email' in session:
        email = session['email']
    else:
        print('email not in session')
    requests.post(url = CARTURL + 'updateStatus',data={'email':email,'status':'Settled'})
    r = requests.get(url = CARTURL + 'findByUser/' +email) 
    query = {
        'email':email,
        'oid':session['oid'],
        'items':session['items']
    }
    status = payments.insert_one(query)
    body = {"subject": "payment", "to": email, "admin": False}
    body = json.dumps(body, default=str)
    channel.queue_declare(queue='notification', durable=True)
    channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification')
    channel.basic_publish(exchange=exchangename, routing_key="payment.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))
    return render_template('purchasesuccessful.html')

@app.route('/pay', methods=['POST'])
def pay():
    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])
    charge = stripe.Charge.create(
        customer=customer.id,
        currency = 'SGD',
        amount = 200
    )
    return redirect(url_for('purchasesuccessful'))

@app.route('/getPayment', methods =['GET'])
def getPayment():
    result = payments.find({})
    items = {}
    for row in payments.find({}):
        
        for item in row['items']:
            if item[0] not in items:
                items[item[0]] = [item[1]]
            else:
                items[item[0]].append(item[1])
        
    return jsonify({'result':items}),200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5006)))
    # app.run(port=5006, debug=True)