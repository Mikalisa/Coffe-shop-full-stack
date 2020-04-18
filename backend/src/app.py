import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drink():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_detail(payload):
    drinks = Drink.query.order_by(Drink.id).all()
    return jsonify({
            'success': True,
            "drinks": [drink.long() for drink in drinks]
        }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):

    data = request.get_json()

    try:
        data_recipe = data.get('recipe', None)
        if isinstance(data_recipe, dict):
            data_recipe = [data_recipe]

        drink = Drink()
        drink.title = data.get('title', None)
        drink.recipe = json.dumps(data_recipe)
        drink.insert()

    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):
    data = request.get_json()
    drink = Drink.query.get(id)
    try:
        data_title = data.get('title', None)
        data_recipe = data.get('recipe', None)
        if drink is None:
            abort(404)
        elif (data_title):
            drink.title = data_title
        elif (data_recipe):
            drink.recipe = data_recipe
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except:
        abort(401)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
        }), 422


# error handlers for all expected errors 
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
        }), error.status_code


if __name__ == "__main__":
    app.run()
