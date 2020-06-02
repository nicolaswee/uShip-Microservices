# uShip - Microservices
![Testing for UShip](https://github.com/nicolaswee/uShip-Microservices/workflows/Testing%20for%20UShip/badge.svg) [![GitHub contributors](https://img.shields.io/github/contributors/nicolaswee/uShip-Microservices.svg)](https://github.com/nicolaswee/uShip-Microservices/graphs/contributors) [![GitHub pull-requests](https://img.shields.io/github/issues-pr/nicolaswee/uShip-Microservices.svg)](https://GitHub.com/nicolaswee/uShip-Microservices/pull/) [![GitHub pull-requests closed](https://img.shields.io/github/issues-pr-closed/nicolaswee/uShip-Microservices.svg)](https://GitHub.com/nicolaswee/uShip-Microservices/pull/) [![GitHub issues](https://img.shields.io/github/issues/nicolaswee/uShip-Microservices.svg)](https://GitHub.com/nicolaswee/uShip-Microservices/issues/) [![GitHub issues-closed](https://img.shields.io/github/issues-closed/nicolaswee/uShip-Microservices.svg)](https://GitHub.com/nicolaswee/uShip-Microservices/issues?q=is%3Aissue+is%3Aclosed)

### Details
> UShip allows for customers to view and purchase products like an online e-store. It also allows suppliers to upload their products for sale

>UData is a dashboard for admins to keep track of the overall profits of UShip, product approval statuses, contacts of suppliers, etc.

>UTele integrates the functionality on Telegram. It allows users to view, add, remove items from their cart.

## uShip Overview
![uShip Video](image/uship.gif)

## uData Overview
![uData Video](image/udata.gif)

## uTele Overview
![uTele Video](image/utele.gif)

## Technical Overview
![Technical Overview](image/uship-TechnicalOverview.png)

## Service Oriented Architecture
![Service Oriented Architecture](image/uship-SOA.png)

## Technical Stack
![Technical Stack](image/uship-TechStack.png)

#### Running on localhost:
``` bash
# Cart Microservice
$ cd cart
$ pip install -r requirements.txt
$ python cart.py

# News Microservice
$ cd news
$ pip install -r requirements.txt
$ python news.py
# OR
$ docker-compose up

# Notification Microservice
$ cd notification
$ pip install -r requirements.txt
$ python notification.py

# Payment Microservice
$ cd payment
$ pip install -r requirements.txt
$ python payment.py

# Product Microservice
$ cd product
$ pip install -r requirements.txt
$ python product.py
# OR
$ docker-compose up

# Recommendation Microservice
$ cd recommendation
$ pip install -r requirements.txt
$ python recommendation.py

# User Microservice
$ cd user
$ pip install -r requirements.txt
$ python user.py

# Weather Microservice
$ cd weather
$ pip install -r requirements.txt
$ python weather.py
# OR
$ docker-compose up

# GraphQL Microservice
$ cd graphql
$ pip install -r requirements.txt
$ python app.py

# Changing of Environment URLs
# Currently all URLs are pointing to our API Gateway, if it goes down please do change the URLs in the environment files to localhost
```

## Ports
- GraphQL = 5000
- Product = 5001
- Cart = 5002
- News = 5003
- Weather = 5004
- Recommendation = 5005
- Payment = 5006
- User = 5007

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) [![ForTheBadge uses-git](http://ForTheBadge.com/images/badges/uses-git.svg)](https://GitHub.com/) [![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)](https://GitHub.com/nicolaswee/) <a href="https://twitter.com/nicolasmarcwee" alt="twitter">![Tweeting](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)</a>
