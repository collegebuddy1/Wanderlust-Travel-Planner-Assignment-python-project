import datetime

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import mysql.connector

app = Flask(__name__, template_folder="templates", static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/wtravel'
db = SQLAlchemy(app)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)


class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    activity = db.Column(db.String(200), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(100))
    
    
# Routes for managing users
@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'GET':
        all_users = User.query.all()
        result = []
        for user in all_users:
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        return jsonify(result)

    elif request.method == 'POST':
        data = request.form
        new_user = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user added!'})

@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_single_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found!'})

    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })

    elif request.method == 'PUT':
        data = request.get_json()
        user.username = data['username']
        user.email = data['email']
        user.password = data['password']
        db.session.commit()
        return jsonify({'message': 'User updated!'})

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted!'})
    
    

@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    new_user = User(username=data['username'], password=data['password'], email=data['email'], address=data['address'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/users/<email>', methods=['GET'])
def get_user_details(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"username": user.username, "email": user.email, "address": user.address}), 200
    return jsonify({"message": "User not found"}), 404



@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({"name": user.name, "email": user.email, "address": user.address})
    return jsonify(user_list), 200

@app.route('/users/<email>', methods=['PUT'])
def update_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        data = request.json
        user.name = data.get('name', user.name)
        user.password = data.get('password', user.password)
        user.address = data.get('address', user.address)
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    return jsonify({"message": "User not found"}), 404


@app.route('/users/<email>', methods=['DELETE'])
def delete_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"message": "User not found"}), 404

# Routes for managing destinations
@app.route('/destinations', methods=['GET', 'POST'])
def manage_destinations():
    if request.method == 'GET':
        all_destinations = Destination.query.all()
        result = []
        for destination in all_destinations:
            result.append({
                'id': destination.id,
                'name': destination.name,
                'description': destination.description,
                'location': destination.location
            })
        return jsonify(result)

    elif request.method == 'POST':
        data = request.form
        new_destination = Destination(
            name=data['name'],
            description=data['description'],
            location=data['location']
        )
        db.session.add(new_destination)
        db.session.commit()
        return jsonify({'message': 'New destination added!'})

@app.route('/destinations/<int:destination_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_single_destination(destination_id):
    destination = Destination.query.get(destination_id)

    if not destination:
        return jsonify({'error': 'Destination not found!'})

    if request.method == 'GET':
        return jsonify({
            'id': destination.id,
            'name': destination.name,
            'description': destination.description,
            'location': destination.location
        })

    elif request.method == 'PUT':
        data = request.get_json()
        destination.name = data['name']
        destination.description = data['description']
        destination.location = data['location']
        db.session.commit()
        return jsonify({'message': 'Destination updated!'})

    elif request.method == 'DELETE':
        # Delete related records in the itinerary table
        itineraries = Itinerary.query.filter_by(destination_id=destination_id).all()
        for itinerary in itineraries:
            db.session.delete(itinerary)

        # Delete the destination record
        db.session.delete(destination)
        db.session.commit()
        return jsonify({'message': 'Destination deleted!'})

# Routes for managing itineraries
@app.route('/itineraries', methods=['GET', 'POST'])
def manage_itineraries():
    if request.method == 'GET':
        all_itineraries = Itinerary.query.all()
        result = []
        for itinerary in all_itineraries:
            result.append({
                'id': itinerary.id,
                'destination_id': itinerary.destination_id,
                'activity': itinerary.activity
            })
        return jsonify(result)

    elif request.method == 'POST':
        data = request.form
        destination_id = data['destination_id']
        activity = data['activity']
        # Check if the destination with the provided ID exists
        destination = Destination.query.get(destination_id)
        if destination:
            new_itinerary = Itinerary(destination_id=destination_id, activity=activity)
            db.session.add(new_itinerary)
            db.session.commit()
            return jsonify({'message': 'New itinerary added!'})
        else:
            return jsonify({'error': 'Destination not found!'})

@app.route('/itineraries/<int:itinerary_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_single_itinerary(itinerary_id):
    itinerary = Itinerary.query.get(itinerary_id)

    if not itinerary:
        return jsonify({'error': 'Itinerary not found!'})

    if request.method == 'GET':
        return jsonify({
            'id': itinerary.id,
            'destination_id': itinerary.destination_id,
            'activity': itinerary.activity
        })

    elif request.method == 'PUT':
        data = request.get_json()
        itinerary.destination_id = data['destination_id']
        itinerary.activity = data['activity']
        db.session.commit()
        return jsonify({'message': 'Itinerary updated!'})

    elif request.method == 'DELETE':
        # Delete related records in the expense table
        expenses = Expense.query.filter_by(itinerary_id=itinerary_id).all()
        for expense in expenses:
            db.session.delete(expense)

        # Delete the itinerary record
        db.session.delete(itinerary)
        db.session.commit()
        return jsonify({'message': 'Itinerary deleted!'})

# Routes for managing expenses
@app.route('/expenses', methods=['GET', 'POST'])
def manage_expenses():
    if request.method == 'GET':
        all_expenses = Expense.query.all()
        result = []
        for expense in all_expenses:
            result.append({
                'id': expense.id,
                'itinerary_id': expense.itinerary_id,
                'amount': expense.amount,
                'category': expense.category,
                'date': expense.date.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify(result)

    elif request.method == 'POST':
        data = request.form
        itinerary_id = data['itinerary_id']

        # Check if the itinerary with the given ID exists
        itinerary = Itinerary.query.get(itinerary_id)
        if not itinerary:
            return jsonify({'error': 'Itinerary with the provided ID does not exist'}), 404

        new_expense = Expense(
            itinerary_id=itinerary_id,
            amount=data['amount'],
            category=data['category']
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify({'message': 'Expense added successfully'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)