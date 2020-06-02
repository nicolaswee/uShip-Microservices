from flask import Flask
from product import app

def test_debug():
    assert not app.debug, 'Ensure the app not in debug mode'

# TEST UPDATE PRODUCT
# @app.route('/')
# def index():
#     return '''
#     <form method = "POST" action = "/updateProduct" enctype ="multipart/form-data">
#         <input type = "text" name = "uid">
#         <input type = "text" name = "name">
#         <input type = "text" name = "desc">
#         <input type = "text" name = "country">
#         <input type = "text" name = "category">
#         <input type = "file" name = "image">
#         <input type = "submit">
#     </form>
#     '''

# TEST CREATE PRODUCT
# @app.route('/')
# def index():
#     return '''
#     <form method = "POST" action = "/createProduct" enctype ="multipart/form-data">
#         <input type = "text" name = "name">
#         <input type = "text" name = "desc">
#         <input type = "text" name = "country">
#         <input type = "text" name = "category">
#         <input type = "file" name = "image">
#         <input type = "text" name = "email">
#         <input type = "submit">
#     </form>
#     '''