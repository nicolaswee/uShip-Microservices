import graphene
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import News as NewsModel
from models import Weather as WeatherModel


class News(MongoengineObjectType):
    class Meta:
        model = NewsModel
        interfaces = (Node,)


class Weather(MongoengineObjectType):
    class Meta:
        model = WeatherModel
        interfaces = (Node,)

class Query(graphene.ObjectType):
    node = Node.Field()
    news = MongoengineConnectionField(News)
    weather = MongoengineConnectionField(Weather)

schema = graphene.Schema(query=Query, types=[News, Weather])
