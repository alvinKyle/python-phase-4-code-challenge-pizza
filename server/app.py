#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response ,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def restaurant ():
    restaurant  = []
    for resto in  Restaurant.query.all():
        restaurant_dict = {
            'id':resto.id,
            'name':resto.name,
            'address':resto.address
        }
        restaurant.append(restaurant_dict)
    return jsonify(restaurant),200

@app.route('/restaurants/<int:id>' , methods = ['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        restaurant_dict = {
            'id':restaurant.id,
            'name':restaurant.name,
            'address':restaurant.address,
            'restaurant_pizzas':[
                {
                'id':restaurant_pizza.id,
                'restaurant_id':restaurant_pizza.restaurant_id,
                'pizza_id':restaurant_pizza.pizza_id,
                'price':restaurant_pizza.price,
                'pizza':{
                    'id':restaurant_pizza.pizza.id,
                    'name':restaurant_pizza.pizza.name,
                    'ingredients':restaurant_pizza.pizza.ingredients
                    }
                }for restaurant_pizza in restaurant.pizzas
            ]
        }
        res = make_response(jsonify(restaurant_dict),200 )
        return res
    
    else:
        res = make_response(jsonify({"error": "Restaurant not found"}),404 )    
        return res
    
@app.route('/restaurants/<int:id>', methods = ['GET','DELETE'])
def delete_restaurant(id):
    restau = Restaurant.query.filter_by(id=id).first()
    if restau:
        RestaurantPizza.query.filter_by(restaurant_id = id).delete()
        db.session.delete(restau)
        db.session.commit()
        res = make_response('',204)
        return res
    else:
        res = make_response(
            jsonify({"error": "Restaurant not found"}),404
        )
        return res
    
@app.route('/pizzas')  
def pizza ():
    pizza = Pizza.query.all()
    pizzas = []

    for p in pizza:
        pizza_dict = {
            'id':p.id,
            'name':p.name,
            'ingredients':p.ingredients
        }
        pizzas.append(pizza_dict)
    return jsonify(pizzas)

@app.route('/restaurant_pizzas',methods = ['POST'])
def add_pizza():
    if request.method == 'POST':
        output = request.get_json()
        try:
            restaurant_pizza = RestaurantPizza(
                price = output['price'],
                restaurant_id = output['restaurant_id'],
                pizza_id  = output['pizza_id']
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            restaurant = Restaurant.query.get(restaurant_pizza.restaurant_id)
            pizza = Pizza.query.get(restaurant_pizza.pizza_id)

            output_data = {
                'id': restaurant_pizza.id,
                'pizza':{
                    'id': pizza.id,
                    'ingredients':pizza.ingredients,
                    'name':pizza.name
                },
                'pizza_id':restaurant_pizza.pizza_id,
                'price':restaurant_pizza.price,
                'restaurant':{
                    'name':restaurant.name,
                    'address': restaurant.address,
                    'id':restaurant.id
                },
                'restaurant_id':restaurant_pizza.restaurant_id
            }

            res = make_response(jsonify(output_data),201)
            return res
        
        except ValueError as e:
            message = {'errors':['validation errors']}
            res = make_response(jsonify(message),400)
            return res


if __name__ == "__main__":
    app.run(port=5555, debug=True)
