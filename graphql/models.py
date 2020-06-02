from datetime import datetime
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    ObjectIdField,
    DateTimeField,
    EmbeddedDocumentField,
    ListField,
    ReferenceField,
    StringField,
    IntField,
    FloatField,
)

class News(Document):

    meta = {"db_alias": "db_news", "collection": "news_current"}
    source = ListField()
    _id = ObjectIdField()
    author = StringField()
    title = StringField()
    description = StringField()
    url = StringField()
    urlToImage = StringField()
    publishedAt = StringField()
    content = StringField()
    sentiment = IntField()
    overall_sentiment = FloatField()
    time_pulled = DateTimeField(default=datetime.now)
    country = StringField()

class Weather(Document):

    meta = {"db_alias": "db_weather", "collection": "weather"}
    _id = ObjectIdField()
    country = StringField()
    time_pulled = DateTimeField(default=datetime.now)
    currentsummary = StringField()
    weeklysummary = StringField()
    dailysummary = StringField()