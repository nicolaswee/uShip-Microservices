import shortuuid
from flask import Flask, request, jsonify, url_for
from bson import ObjectId
from pymongo import MongoClient
from flask_cors import CORS
import os 
import codecs
from dotenv import load_dotenv
import pika
import json
import base64
import boto3
from botocore.client import Config
import redis
from io import BytesIO
load_dotenv()

app = Flask(__name__)
mongo = os.getenv('MONGODB')
client = MongoClient(mongo)
db = client.products_db
products = db.product
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

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.route("/getConfirmed", methods=['GET'])
def get_all_product():
    output = []
    items = products.find({'status': "confirmed"}).sort('_id', -1)
    for o in items:
        output.append({'UID':o['uid'],'ProductId': str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'],'Country' : o['country'], 'Category' : o['category'], 'Image': o['image']})
    if(len(output)<=0):
        return jsonify({'result' : "Product not found"})
    return jsonify({'result' : output})

@app.route("/getConfirmedCache", methods=['GET'])
def get_all_product_cache():
    output = []
    cache_product = cache.get("all")
    if not cache_product:
        items = products.find({'status': "confirmed"}).sort('_id', -1)
        for o in items:
            output.append({'UID':o['uid'],'ProductId': str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'],'Country' : o['country'], 'Category' : o['category'], 'Image': o['image']})
        if(len(output)<=0):
            return jsonify({'result' : "Product not found"})
        cache.setex("all", 300, str(output))
        return jsonify({'cache': False, 'result' : output})
    else:
        return jsonify({'cache': True, 'result' : str(cache_product)})
    
@app.route("/getPending", methods=['GET'])
def get_all_pending_product():
    output = []
    items = products.find({'status': "pending"}).sort('_id', -1)
    for o in items:
        output.append({'UID':o['uid'],'ProductId': str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'],'Country' : o['country'], 'Category' : o['category'], 'Image': o['image'], 'SupplierId': o['email']})
    if(len(output)<=0):
        return jsonify({'result' : "Product not found"})
    return jsonify({'result' : output})

@app.route('/findByCountry', methods=['GET'])
def find_by_country():
    country = request.args.get('country')
    output = []
    for o in products.find({'status': "confirmed", 'country':country}):
        output.append({'UID':o['uid'],'ProductId':str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'], 'Country' : o['country'], 'Category' : o['category'],'Image': o['image']})
    if(len(output)<=0):
        return jsonify({'result' : "Product cannot be found"}), 404
    return jsonify({'result' : output})

@app.route('/findByCategory', methods=['GET'])
def find_by_category():
    category = request.args.get('category')
    output = []
    for o in products.find({'status': "confirmed", 'category':category}):
        output.append({'UID':o['uid'],'ProductId':str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'], 'Country' : o['country'], 'Category' : o['category'],'Image': o['image']})
    if(len(output)<=0):
        return jsonify({'result' : "Product cannot be found"}), 404
    return jsonify({'result' : output})

@app.route('/findByKeyword', methods=['GET'])
def find_by_keyword():
    keyname = request.args.get('q')
    output = []
    for o in products.find({'status': "confirmed"}):
        if(keyname.lower() in o['name'].lower()):
            output.append({'UID':o['uid'],'ProductId':str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'], 'Country' : o['country'], 'Category' : o['category'],'Image': o['image']})
    if(len(output)<=0):
        return jsonify({'result' : "Product cannot be found"}), 200
    return jsonify({'result' : output})

@app.route('/updateProduct', methods=['POST'])
def update_product():
    product_id= products.find_one({'uid':request.form.get("uid"), 'status':"confirmed"})
    product_id1= products.find_one({'uid':request.form.get("uid"), 'status':"pending"})
    if (product_id or product_id1):
        if(request.form.get("category")):
            products.update_one({'uid':request.form.get("uid")},{"$set":{'category':request.form.get("category")}})
        if(request.form.get("name")):
            products.update_one({'uid':request.form.get("uid")},{"$set":{'name':request.form.get("name")}})
        if(request.form.get("country")):
            products.update_one({'uid':request.form.get("uid")},{"$set":{'country':request.form.get("country")}})
        if(request.form.get("desc")):
            products.update_one({'uid':request.form.get("uid")},{"$set":{'desc':request.form.get("desc")}})
        if 'image' in request.files:
            key = request.form.get("uid") + ".jpg"
            s3 = boto3.resource(
                's3',
                aws_access_key_id=ACCESS_KEY_ID,
                aws_secret_access_key=ACCESS_SECRET_KEY,
                config=Config(signature_version='s3v4')
            )
            s3.Bucket(BUCKET_NAME).put_object(Key=key, Body=request.files['image'], ACL='public-read')
        return jsonify({'result' : "Product has been updated"})
    else:
        return jsonify({'result': "Cannot find product"})

@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    product_id = products.find_one({'uid':request.form.get("uid")})
    if (product_id):
        products.delete_one({'uid':request.form.get("uid")})
        return jsonify({'result' : "Product has been deleted"})
    else:
        return jsonify({'result': "Cannot find product"})


@app.route('/updateStatus', methods=['PUT'])
def updatestatus():
    product_id= products.find_one({'uid':request.get_json()['uid']})
    if (product_id):
        products.update_one({'uid':request.get_json()['uid']},{"$set":{'status':request.get_json()['status']}})
        body = {"subject": request.get_json()['status'], "id":request.get_json()['uid'] , 'content': product_id["name"], "to": product_id['email'], "admin": False}
        body = json.dumps(body, default=str)
        channel.queue_declare(queue='notification', durable=True)
        channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification')
        channel.basic_publish(exchange=exchangename, routing_key="status.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))
        return jsonify({'result' : "Product has been updated"})
    else:
        return jsonify({'result': "Cannot find product"}), 400

@app.route('/createProduct', methods = ["POST"])
def createProduct():
    uid = shortuuid.ShortUUID().random(length=6)
    if 'image' in request.files:
        key = uid + ".jpg"
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        s3.Bucket(BUCKET_NAME).put_object(Key=key, Body=request.files['image'], ACL='public-read')
    query = {
        'email':request.form.get('email'),
        'uid':uid,
        'name': request.form.get('name'),
        'desc':request.form.get('desc'),
        'country': request.form.get('country'),
        'category': request.form.get('category'),
        'status': "pending",
        'image': "https://uship-img-bucket.s3-ap-southeast-1.amazonaws.com/" + uid + ".jpg"
    }
    status = products.insert_one(query)
    if status:
        body = {"subject": "pending", "id": uid, 'content': request.form.get('name'), "to": "ushipnotification@gmail.com", "admin": True}
        body = json.dumps(body, default=str)
        channel.queue_declare(queue='notification', durable=True)
        channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification')
        channel.basic_publish(exchange=exchangename, routing_key="pending.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))
        return jsonify({'result': 'Product uploaded successfully'}),201
    return jsonify({'result': 'Error occurred during uploading'}),500

@app.route('/findById', methods=['GET'])
def find_by_id():
    uid = request.args.get('uid')
    output = []
    for o in products.find({'uid': uid}):
        output.append({'UID':o['uid'],'ProductId':str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'], 'Country' : o['country'], 'Category' : o['category'],'Image': o['image'], 'Supplier': o['email'], 'Status': o['status']})
    if(len(output)<=0):
        return jsonify({'result' : "Product cannot be found"}), 404
    return jsonify({'result' : output})


@app.route('/findBySupplier',methods = ['GET'])
def find_by_sid():
    email = request.args.get('email')
    output = []
    for o in products.find({'email':email}).sort('_id',-1):
        output.append({'UID':o['uid'],'ProductId':str(o['_id']),'ProductName' : o['name'], 'ProductDescription' : o['desc'], 'Country' : o['country'], 'Category' : o['category'],'Image': o['image'], 'Status': o['status']})
    if(len(output)<=0):
        return jsonify({'result' : "Product cannot be found"}), 404
    return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5001)))
    # app.run(port=5001, debug=True)