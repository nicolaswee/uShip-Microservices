from flask import Flask, request, jsonify, url_for
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

import graphene
from flask_graphql import GraphQLView
from mongoengine import Document, connect
from mongoengine.fields import StringField
from schema import schema

app = Flask(__name__)
CORS(app)

connect(host=os.getenv('MONGODB_NEWS'), alias='db_news')
connect(host=os.getenv('MONGODB_WEATHER'), alias='db_weather')

app.add_url_rule(
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run()