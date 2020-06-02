from flask import Flask, request, jsonify, url_for
from pymongo import MongoClient
from flask_cors import CORS
from darksky import forecast
from datetime import datetime, timedelta, date
import os
import pika
import json
import redis
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
mongo = os.getenv('MONGODB')
client = MongoClient(mongo) 
db = client.weather_db
country = db.country
weather = db.weather
API_KEY = os.getenv('DARKSKY_API_KEY')
CORS(app)

url = os.getenv('AMQP_LINK')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
exchangename="uship"
channel.exchange_declare(exchange=exchangename, exchange_type='topic')

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

def pull_weather(countryName):
    latitude = float(countryName['latitude'])
    longitude = float(countryName['longitude'])
    countryName = countryName['name']
    datenow = datetime.now()
    todayweather = forecast(API_KEY,latitude,longitude)
    text = ""

    with todayweather as tweather:
        for day in tweather.daily:
            text += date.strftime(datenow,'%a') +": "+day.summary+"\nTemp range: "+str(day.temperatureMin) +"-"+str(day.temperatureMax)+"\n"
            datenow += timedelta(days=1)
    
    query ={
        'country':countryName,
        'time_pulled':datetime.now(),
        'currentsummary':str(todayweather['currently']['summary']),
        'weeklysummary':str(todayweather['daily']['summary']),
        'dailysummary':text
        }

    status = weather.insert_one(query)

    if not status:
        jsonify({'result':'error uploading'}), 500

    if hasattr(todayweather,'alert'):
        w = weather.find_one({'country':countryName})
        body = {"subject": "weather_alert", 'country':countryName,'summary': todayweather.alert, "admin": False}
        body = json.dumps(body, default=str)
        channel.queue_declare(queue='notification', durable=True) 
        channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification') 
        channel.basic_publish(exchange=exchangename, routing_key="alert.notification", body=body,
            properties=pika.BasicProperties(delivery_mode = 2))
        return jsonify({'result': todayweather.alert, 'daily summary':w['dailysummary'], 'weekly summary':w['weeklysummary']}), 200
    else:
        w = weather.find_one({'country':countryName})
        return jsonify({'result':todayweather['currently']['summary'],'daily summary':w['dailysummary'], 'weekly summary':w['weeklysummary'], 'country':w['country']}), 200

@app.route('/getWeather/<string:countryName>', methods=['GET'])
def get_weather_by_country(countryName):
    w = weather.find_one({'country':countryName.title()})
    if(w != None and w['time_pulled'] + timedelta(hours=24) > datetime.now()):
        return jsonify({'result':w['currentsummary'],'daily summary':w['dailysummary'], 'weekly summary':w['weeklysummary'], 'country':w['country']}), 200
    else:
        country_to_search = country.find_one({'name':countryName.title()})
        if country_to_search:
            return pull_weather(country_to_search)

    return jsonify({'result':'country is not found'}), 401

@app.route('/getWeatherCache/<string:countryName>', methods=['GET'])
def get_weather_by_country_Cache(countryName):
    cache_weather = cache.get(countryName)
    if not cache_weather:
        w = weather.find_one({'country':countryName.title()})
        if(w != None and w['time_pulled'] + timedelta(hours=24) > datetime.now()):
            cache.setex(countryName, 300, str(w))
            return jsonify({'result':w['currentsummary'],'daily summary':w['dailysummary'], 'weekly summary':w['weeklysummary'], 'country':w['country']}), 200
        else:
            country_to_search = country.find_one({'name':countryName.title()})
            if country_to_search:
                output = pull_weather(country_to_search)
                cache.setex(countryName, 300, str(output))
                return output

        return jsonify({'result':'country is not found'}), 401
    else:
        return jsonify({'cache': True, 'result' : str(cache_weather)})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5004)))
    # app.run(port=5004, debug=True)
