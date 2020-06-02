from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os 
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/getRecommendation', methods=['GET'])
def getRecommendation():
    productname = request.args.get('productname')
    productid = request.args.get('productid')
    country = request.args.get('country')
    
    #get all items
    url = (os.getenv('PRODUCT_MICROSERVICE_URL') + '/findByKeyword?q=' + productname)
    response = requests.get(url)
    output = json.loads(response.text)['result']
    
    output_without_country = []
    for item in output:
        if item['Country'] != country and item['ProductId'] != productid:
            output_without_country.append(item)
    
    countries = []
    #get all countries of items with same name
    for item in output_without_country:
        countries.append(item['Country'])

    for country in countries:
        score = 0
        #grabbing the response for the news
        url = (os.getenv('NEWS_MICROSERVICE_URL') + '/getNews?country=' + country + "&count=10")
        newsreponse = requests.get(url)
        #add overall sentiment into the score
        overall_sentiment = json.loads(newsreponse.text)['result'][0]['overall_sentiment']
        score += overall_sentiment
        url = (os.getenv('WEATHER_MICROSERVICE_URL') + '/getWeather/'+ country)
        weatherresponse = requests.get(url)
        #if alert in response
        if 'alert' in json.loads(weatherresponse.text):
            score -= 0.2
        #get weekly summary and calculate score
        output_weather = json.loads(weatherresponse.text)['weekly summary']
        # no precipitation
        if 'no' in output_weather:
            score += 0.05
        #possible means not confirmed
        elif 'possible' in output_weather:
            score += 0.025
        # light rain = possible bad weather in the future forecast
        elif 'light' in output_weather:
            score -= 0.025
        #means will rain, will affect delivery of goods through shipping
        else:
            score -= 0.05
#         combine both scores and get the highest one
        for product in output_without_country:
            # append score as new key value pair to sort
            if product['Country'] == country:
                product['score'] = score
    # sort and return the best country
    return jsonify(sorted(output_without_country, key = lambda i: i['score'], reverse = True))

@app.route('/getRecommendationQL', methods=['GET'])
def getRecommendationQL():
    productid = request.args.get('productid')
    country = request.args.get('country')
    
    #get all items
    url = (os.getenv('GRAPHQL_MICROSERVICE_URL'))
    query = """{
        weather {
            edges {
            node {
                country,
                weeklysummary,
                timePulled
            }
            }
        },
        news {
            edges {
            node {
                country,
                sentiment,
                overallSentiment,
                timePulled
            }
            }
        }
    }"""
    response = requests.post(url, json={'query': query})
    output = json.loads(response.text)
    
    output_without_country = []
    for item in output:
        if item['Country'] != country and item['ProductId'] != productid:
            output_without_country.append(item)
    
    countries = []
    #get all countries of items with same name
    for item in output_without_country:
        countries.append(item['Country'])

    for country in countries:
        score = 0
        #grabbing the response for the news
        url = (os.getenv('NEWS_MICROSERVICE_URL') + '/getNews?country=' + country + "&count=10")
        newsreponse = requests.get(url)
        #add overall sentiment into the score
        overall_sentiment = json.loads(newsreponse.text)['result'][0]['overall_sentiment']
        score += overall_sentiment
        url = (os.getenv('WEATHER_MICROSERVICE_URL') + '/getWeather/'+ country)
        weatherresponse = requests.get(url)
        #if alert in response
        if 'alert' in json.loads(weatherresponse.text):
            score -= 0.2
        #get weekly summary and calculate score
        output_weather = json.loads(weatherresponse.text)['weekly summary']
        # no precipitation
        if 'no' in output_weather:
            score += 0.05
        #possible means not confirmed
        elif 'possible' in output_weather:
            score += 0.025
        # light rain = possible bad weather in the future forecast
        elif 'light' in output_weather:
            score -= 0.025
        #means will rain, will affect delivery of goods through shipping
        else:
            score -= 0.05
#         combine both scores and get the highest one
        for product in output_without_country:
            # append score as new key value pair to sort
            if product['Country'] == country:
                product['score'] = score
    # sort and return the best country
    return jsonify(sorted(output_without_country, key = lambda i: i['score'], reverse = True))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5005)))
    # app.run(port=5005, debug=True) 