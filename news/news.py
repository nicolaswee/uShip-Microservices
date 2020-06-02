import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, url_for
from pymongo import MongoClient
import redis
from flask_cors import CORS
import os 
from dotenv import load_dotenv
import json
load_dotenv()

app = Flask(__name__)
mongo = os.getenv('MONGODB')
client = MongoClient(mongo)
db = client.news_db
news = db.news
CORS(app)

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

def sentiment_analysis(description):
    tokenized = word_tokenize(str(description))
    tagged_tokens = nltk.pos_tag(tokenized)
    
    lemmatizer = WordNetLemmatizer()
    def lemmatize(pair):
        word, tag = pair
        try:
            return lemmatizer.lemmatize(word, pos=tag[0].lower())
        except KeyError:
            return word
    
    lemmatized = [lemmatize(token).lower() for token in tagged_tokens]
    STOP_WORDS = stopwords.words()
    filtered = [x for x in lemmatized if x not in STOP_WORDS]
    sid = SentimentIntensityAnalyzer()
    test = ' '.join(filtered)
    ss = sid.polarity_scores(test)
    
    if ss['neg'] > ss['pos']:
        return -(ss['neg'])
    elif ss['pos'] > ss['neg']:
        return ss['pos']
    else:
        return 0

def pull_country_news(news_country):
    currentDT = datetime.now()
    countries = {'argentina': 'ar', 'australia': 'au', 'austria' : 'at', 'belgium': 'be', 'brazil' : 'br', 'bulgaria' : 'bg', 
                 'canada': 'ca', 'china' : 'cn', 'colombia' : 'co', 'cuba' : 'cu', 'czech republic': 'cz','egypt' : 'eg',
                 'france' : 'fr', 'germany': 'de', 'greece' : 'gr','hong kong': 'hk', 'hungary': 'hu', 'india' : 'in',
                 'indonesia' : 'id', 'ireland' : 'ie', 'israel': 'il', 'italy' : 'it', 'japan' : 'jp', 'latvia': 'lv',
                 'lithuania' : 'lt', 'malaysia' : 'my', 'mexico': 'mx', 'morocco': 'ma', 'new zealand': 'nz',
                 'nigeria' : 'ng', 'norway' : 'no', 'philippines' : 'ph', 'poland' : 'pl', 'portugal': 'pt', 'romania': 'ro',
                 'russia' : 'ru', 'saudi arabia': 'sa', 'serbia': 'rs', 'singapore' : 'sg', 'slovakia': 'sk', 'slovenia': 'si',
                 'south africa': 'za', 'south korea': 'kr', 'sweden': 'se', 'switzerland': 'ch', 'taiwan': 'tw', 'thailand': 'th',
                 'turkey' : 'tr', 'uae': 'ae', 'ukraine': 'ua', 'united kingdom' : 'gb', 'united states': 'us', 'venuzuela': 've'}
    news_country = news_country.lower()
    if news_country not in countries:
        return False
    country = countries[news_country]
    api_key = os.getenv('NEWS_API_KEY')
    url = ('http://newsapi.org/v2/top-headlines?'
           'country='+ country+ '&'
           'apiKey=' + api_key)
    response = requests.get(url)
    all_news = dict(response.json())
    total_count = all_news['totalResults']
    news_descriptions = all_news['articles']
    
    if len(news_descriptions) < 1:
        return False 

    score = 0
    bad_count = 0
    good_count = 0
    for article in news_descriptions:
        sentiment = sentiment_analysis(article['description'])
        score += sentiment
        if sentiment < 0:
            bad_count += 1
            article['sentiment'] = -1
        elif sentiment > 0:
            good_count += 1
            article['sentiment'] = 1
        else:
            article['sentiment'] = 0
    for article in news_descriptions:
        if score == 0:
            article['overall_sentiment'] = 0
        else:
            article['overall_sentiment'] = score/(bad_count + good_count)
        article['time_pulled'] = currentDT
        article['country'] = news_country
    return news_descriptions

@app.route('/getNews', methods=['GET'])
def getNews():
    country  = request.args.get('country', None)
    count  = int(request.args.get('count', None))
    output = []
    country = country.lower()
    for o in news.find({'country':country}):
        output.append({'title':o['title'],'description':o['description'],'content' : o['content'], 'url' : o['url'], 'urlToImage' : o['urlToImage'], 'sentiment' : o['sentiment'],'overall_sentiment': o['overall_sentiment'], 'time_pulled': o['time_pulled']})
    #if country has no news yet
    if(len(output)<=0):
        output = pull_country_news(country)
        #bad country
        if output == False:
            return jsonify({'result' : "Country news cannot be found"}), 401
    else:
        one_day_later = output[0]['time_pulled'] + timedelta(hours=24)
        if one_day_later < datetime.now():
            #drop lines that are relating to this country
            news.remove({'country':country})
            output = pull_country_news(country)
    for news_output in output:
        news.insert_one(news_output)
        news_output['_id'] = str(news_output['_id'])
    if len(output) < count:
        return jsonify({'result' : output})
    return jsonify({'result' : output[:count]}), 200

@app.route('/getNewsCache', methods=['GET'])
def getNewsCache():
    country  = request.args.get('country', None)
    count  = int(request.args.get('count', None))
    output = []
    country = country.lower()
    cache_news = cache.get(country)
    if not cache_news:
        for o in news.find({'country':country}):
            output.append({'title':o['title'],'description':o['description'],'content' : o['content'], 'url' : o['url'], 'urlToImage' : o['urlToImage'], 'sentiment' : o['sentiment'],'overall_sentiment': o['overall_sentiment'], 'time_pulled': o['time_pulled']})
        #if country has no news yet
        if(len(output)<=0):
            output = pull_country_news(country)
            #bad country
            if output == False:
                return jsonify({'result' : "Country news cannot be found"}), 401
        else:
            one_day_later = output[0]['time_pulled'] + timedelta(hours=24)
            if one_day_later < datetime.now():
                #drop lines that are relating to this country
                news.remove({'country':country})
                output = pull_country_news(country)
        for news_output in output:
            news.insert_one(news_output)
            news_output['_id'] = str(news_output['_id'])

        cache.setex(country, 300, str(output))

        if len(output) < count:
            return jsonify({'cache': False, 'result' : output})
        return jsonify({'cache': False, 'result' : output[:count]}), 200
    else:
        return jsonify({'cache': True, 'result' : str(cache_news)})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5003)))
    # app.run(port=5003, debug=True)

