import pika
import json
import requests
from flask import Flask, request
import smtplib
from email.message import EmailMessage
from pymongo import MongoClient, ReturnDocument
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
mongo = os.getenv('MONGODB')
client = MongoClient(mongo)
db = client.telegram_db
telegramdb = db.telegram

# Declare AMQP queue
url = os.getenv('AMQP_LINK')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
exchangename="uship"
channel.exchange_declare(exchange=exchangename, exchange_type='topic')

# Get email details
EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

def startConsuming():
    channelqueue = channel.queue_declare(queue="notification", durable=True)
    queue_name = channelqueue.method.queue
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.notification')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def callback(channel, method, properties, body):
    body = json.loads(body)
    productData = ""
    
    if(body["subject"] == "payment"):
        emailPayment(body)
        return
    if(body["subject"] == "cart_checkout"):
        emailCartCheckout(body)
        return
    if(body["subject"] == "cart_payment"):
        emailCartPayment(body)
        return
    if(body["subject"] != "weather_alert"):
        URL = os.getenv('PRODUCT_MICROSERVICE_URL') + "/findById"
        r = requests.get(url = URL, params = {"uid":body['id']})
        productData = r.json()
        productData = productData['result'][0]
        email(body, productData)
    telegram(body, productData)

def email(data, productData):

    msg = EmailMessage()
    if data['subject'] == "confirmed":
        msg['Subject'] = "Item " + data['content'] + " has been approved!"
        email_title_html = """<td style="color: #006400; font-family: Arial, sans-serif; font-size: 24px;"align="center">
                                <b>Your Upload has been Approved!</b>
                            </td>"""
        email_bottom_html = """<td bgcolor="#006400" style="padding: 30px 30px 30px 30px;">"""
    elif data['subject'] == "rejected":
        msg['Subject'] = "Item " + data['content'] + " has been rejected."
        email_title_html = """<td style="color: #B22222; font-family: Arial, sans-serif; font-size: 24px;"align="center">
                                <b>Your Upload has been Rejected.</b>
                            </td>"""
        email_bottom_html = """<td bgcolor="#B22222" style="padding: 30px 30px 30px 30px;">"""
    else:
        msg['Subject'] = "Item " + data['content'] + " is pending."
        email_title_html = """<td style="color: #C2C5CC; font-family: Arial, sans-serif; font-size: 24px;"align="center">
                                <b>An Upload is pending.</b>
                            </td>"""
        email_bottom_html = """<td bgcolor="#C2C5CC" style="padding: 30px 30px 30px 30px;">"""
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = data['to']

    #region HTML
    html = """\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>uShip Notification</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="margin: 0; padding: 0;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%"> 
            <tr>
                <td style="padding: 10px 0 30px 0;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border: 1px solid #cccccc; border-collapse: collapse;">
                        <tr>
                            <td align="center" bgcolor="#70bbd9" style="padding: 40px 0 30px 0; color: #153643; font-size: 28px; font-weight: bold; font-family: Arial, sans-serif;">
                                <img src="https://uship-img-bucket.s3-ap-southeast-1.amazonaws.com/uship_white_logo.png" alt="Creating Email Magic" width="400" height="400" style="display: block;" />
                            </td>
                        </tr>
                        <tr>
                            <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        {email_title_html}
                                    </tr>
                                    <tr>
                                        <td style="padding: 20px 0 30px 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;" align="center">
                                        The details are as follows
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <img src="{image}" alt="" width="100%" align="center" style="display: block;" />
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                <tr>
                                                    <td valign="top">
                                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                            <tr>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-weight: bold;font-size: 16px; line-height: 20px;"align="center">
                                                                    ProductId:
                                                                </td>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;"align="center">
                                                                    {productId}
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-weight: bold; font-size: 16px; line-height: 20px;"align="center">
                                                                    ProductName:
                                                                </td>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;"align="center">
                                                                    {productName}
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-weight: bold;font-size: 16px; line-height: 20px;"align="center">
                                                                    Category:
                                                                </td>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;"align="center">
                                                                    {category}
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif;font-weight: bold; font-size: 16px; line-height: 20px;"align="center">
                                                                    Country:
                                                                </td>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;"align="center">
                                                                    {country}
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-weight: bold; font-size: 16px; line-height: 20px;"align="center">
                                                                    Description:
                                                                </td>
                                                                <td style="padding: 25px 0 0 0; color: #153643; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px;"align="center">
                                                                    {description}
                                                                </td>
                                                            </tr>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    <td style="font-size: 0; line-height: 0;" width="20">
                                                        &nbsp;
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            {email_bottom_html}
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #ffffff; font-family: Arial, sans-serif; font-size: 14px;" width="75%">
                                            &reg;UShip, 2020<br/>
                                            <a href="#" style="color: #ffffff;"><font color="#ffffff">Unsubscribe</font></a> here.
                                        </td>
                                        <td align="right" width="25%">
                                            <table border="0" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="font-family: Arial, sans-serif; font-size: 12px; font-weight: bold;">
                                                        <a href="http://www.twitter.com/" style="color: #ffffff;">
                                                            <img src="https://webstockreview.net/images/twitter-icon-png-3.png" alt="Twitter" width="38" height="38" style="display: block;" border="0" />
                                                        </a>
                                                    </td>
                                                    <td style="font-family: Arial, sans-serif; font-size: 12px; font-weight: bold;">
                                                        <a href="http://www.twitter.com/" style="color: #ffffff;">
                                                            <img src="https://cdn3.iconfinder.com/data/icons/2018-social-media-logotypes/1000/2018_social_media_popular_app_logo_facebook-512.png" alt="Facebook" width="38" height="38" style="display: block;" border="0" />
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """.format(email_title_html=email_title_html, category=productData['Category'], country=productData['Country'], image=productData['Image'], description=productData['ProductDescription'], productId="https://esd-uship.herokuapp.com/product/" + productData['UID'], productName=productData['ProductName'], email_bottom_html=email_bottom_html)
    #endregion
    
    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)

def emailCartCheckout(data):
    msg = EmailMessage()
    msg['Subject'] = "There is a cart on Checkout Status"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = data['to']

    msg.set_content("There is a checkout cart!")
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)

def emailCartPayment(data):
    msg = EmailMessage()
    msg['Subject'] = "There is a Payment Pending for your Cart"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = data['to']

    msg.set_content("Your invoice is ready!")
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)

def emailPayment(data):
    msg = EmailMessage()
    msg['Subject'] = "Your Payment is Successful!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = data['to']

    msg.set_content("Payment done!")
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)

def telegram(data, productData):
    
    telegramData = telegramdb.find_one({'email': data['to']})

    if data['subject'] == "confirmed":
        message = "Item " + data['content'] + " has been approved!\nCategory : " + productData['Category'] + "\nCountry : " + productData['Country'] + "\nDescription : " + productData['ProductDescription'] + "\nProduct Image : " + productData['Image'] + "\nProduct Link : https://esd-uship.herokuapp.com/product/" + productData['UID'] + "\nProduct Name : " + productData['ProductName']
    elif data['subject'] == "rejected":
        message = "Item " + data['content'] + " has been rejected.\nCategory : " + productData['Category'] + "\nCountry : " + productData['Country'] + "\nDescription : " + productData['ProductDescription'] + "\nProduct Image : " + productData['Image'] + "\nProduct Link : https://esd-uship.herokuapp.com/product/" + productData['UID'] + "\nProduct Name : " + productData['ProductName']
    elif data['subject'] == "pending":
        message = "Item " + data['content'] + " is pending.\nCategory : " + productData['Category'] + "\nCountry : " + productData['Country'] + "\nDescription : " + productData['ProductDescription'] + "\nProduct Image : " + productData['Image'] + "\nProduct Link : https://esd-uship.herokuapp.com/product/" + productData['UID'] + "\nProduct Name : " + productData['ProductName']
    elif data['subject'] == "weather_alert":
        message = "THERE IS A WEATHER ALERT AT " + data['country'] + ".\nSummary : " + data['summary']
    else:
        message = "Error pls report to admin."

    URL = "https://api.telegram.org/bot" + os.getenv('BOT_API_KEY') + "/sendMessage?chat_id=" + telegramData["telegram"] + "&text=" + message
    r = requests.get(url = URL)
    response = r.json

if __name__ == '__main__':
    startConsuming()