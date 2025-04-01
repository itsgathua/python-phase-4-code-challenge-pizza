#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Restaurant, Pizza, RestaurantPizza
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)
CORS(app)

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=('id', 'name', 'address')) for r in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas.id', 'restaurant_pizzas.price', 'restaurant_pizzas.pizza.id', 'restaurant_pizzas.pizza.name', 'restaurant_pizzas.pizza.ingredients')))
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict(only=('id', 'name', 'ingredients')) for p in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not all([price is not None, pizza_id, restaurant_id]):
        return jsonify({"errors": ["Missing required fields"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza:
        return jsonify({"errors": ["Pizza not found"]}), 404
    if not restaurant:
        return jsonify({"errors": ["Restaurant not found"]}), 404

    errors = []
    if price is not None:
        try:
            price = int(price)
            if not 1 <= price <= 30:
                errors.append("validation errors") # Changed error message
        except ValueError:
            errors.append("validation errors") # Changed error message
    else:
        errors.append("Missing price") # Should ideally be caught by the first check

    if errors:
        return jsonify({"errors": errors}), 400

    try:
        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict(only=('id', 'price', 'pizza_id', 'restaurant_id', 'pizza.id', 'pizza.name', 'pizza.ingredients', 'restaurant.id', 'restaurant.name', 'restaurant.address'))), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
    except Exception as e:
        db.session.rollback()
        print("Exception occurred while creating RestaurantPizza:")
        traceback.print_exc()
        return jsonify({"errors": ["Failed to create RestaurantPizza"]}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)