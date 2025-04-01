from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    address = db.Column(String, nullable=False)

    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    pizzas = relationship('Pizza', secondary='restaurant_pizzas', back_populates='restaurants')

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    ingredients = db.Column(String, nullable=False)

    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza')
    restaurants = relationship('Restaurant', secondary='restaurant_pizzas', back_populates='pizzas')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.pizzas')

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(Integer, primary_key=True)
    price = db.Column(Integer, nullable=False)
    pizza_id = db.Column(Integer, ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(Integer, ForeignKey('restaurants.id'), nullable=False)

    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    __table_args__ = (
        CheckConstraint('price >= 1 AND price <= 30', name='price_range'),
    )

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas',
                         '-restaurant.pizzas', '-pizza.restaurants') # Add these

    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30.")
        return price