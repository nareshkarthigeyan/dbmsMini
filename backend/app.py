from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DB_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### Models

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    wallet_balance = db.Column(db.Numeric, default=0)

class Driver(db.Model):
    __tablename__ = 'drivers'
    driver_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=True)
    license_no = db.Column(db.String, nullable=True)
    vehicle_no = db.Column(db.String, nullable=True)
    rating = db.Column(db.Numeric, default=0)
    status = db.Column(db.String, default='available')  # available/busy

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    restaurant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=True)
    cuisine = db.Column(db.String, nullable=True)
    rating = db.Column(db.Numeric, default=0)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    item_id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.restaurant_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    availability = db.Column(db.Boolean, default=True)


class DeliveryPartner(db.Model):
    __tablename__ = 'delivery_partners'
    partner_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=True)
    vehicle_no = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='available')

class Ride(db.Model):
    __tablename__ = 'rides'
    ride_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.driver_id'), nullable=False)
    source = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    fare = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String, default='requested')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.restaurant_id'), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('delivery_partners.partner_id'), nullable=True)
    total_amount = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String, default='placed')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.item_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.ride_id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=True)
    amount = db.Column(db.Numeric, nullable=False)
    mode = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='pending')

class Rating(db.Model):
    __tablename__ = 'ratings'
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)  # driver_id or restaurant_id
    target_type = db.Column(db.String, nullable=False)  # 'driver' or 'restaurant'
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

### Helpers

def row_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

### Routes (minimal CRUD: create & list)

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Multi-service platform API'})

# Create endpoints
@app.route('/api/users/create', methods=['POST'])
def create_user():
    data = request.json or {}
    u = User(name=data.get('name'), phone=data.get('phone'), email=data.get('email'), address=data.get('address'), wallet_balance=data.get('wallet_balance') or 0)
    db.session.add(u)
    db.session.commit()
    return jsonify(row_to_dict(u))

@app.route('/api/users/list', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([row_to_dict(u) for u in users])

@app.route('/api/drivers/create', methods=['POST'])
def create_driver():
    data = request.json or {}
    d = Driver(name=data.get('name'), phone=data.get('phone'), license_no=data.get('license_no'), vehicle_no=data.get('vehicle_no'), rating=data.get('rating') or 0, status=data.get('status') or 'available')
    db.session.add(d)
    db.session.commit()
    return jsonify(row_to_dict(d))

@app.route('/api/drivers/list', methods=['GET'])
def list_drivers():
    drivers = Driver.query.all()
    return jsonify([row_to_dict(d) for d in drivers])

@app.route('/api/restaurants/create', methods=['POST'])
def create_restaurant():
    data = request.json or {}
    r = Restaurant(name=data.get('name'), location=data.get('location'), cuisine=data.get('cuisine'), rating=data.get('rating') or 0)
    db.session.add(r)
    db.session.commit()
    return jsonify(row_to_dict(r))

@app.route('/api/restaurants/list', methods=['GET'])
def list_restaurants():
    rows = Restaurant.query.all()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/menu_items/create', methods=['POST'])
def create_menu_item():
    data = request.json or {}
    item = MenuItem(restaurant_id=data['restaurant_id'], name=data['name'], price=data['price'], availability=data.get('availability', True))
    db.session.add(item)
    db.session.commit()
    return jsonify(row_to_dict(item))

@app.route('/api/menu_items/list', methods=['GET'])
def list_menu_items():
    items = MenuItem.query.all()
    return jsonify([row_to_dict(i) for i in items])


@app.route('/api/delivery_partners/create', methods=['POST'])
def create_partner():
    data = request.json or {}
    p = DeliveryPartner(name=data.get('name'), phone=data.get('phone'), vehicle_no=data.get('vehicle_no'), status=data.get('status','available'))
    db.session.add(p)
    db.session.commit()
    return jsonify(row_to_dict(p))


@app.route('/api/delivery_partners/list', methods=['GET'])
def list_partners():
    parts = DeliveryPartner.query.all()
    return jsonify([row_to_dict(p) for p in parts])

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    data = request.json or {}
    order = Order(user_id=data['user_id'], restaurant_id=data['restaurant_id'], partner_id=data.get('partner_id'), total_amount=data['total_amount'], status=data.get('status','placed'))
    db.session.add(order)
    db.session.commit()
    # add items if provided
    for it in data.get('items', []):
        oi = OrderItem(order_id=order.order_id, item_id=it['item_id'], quantity=it.get('quantity',1))
        db.session.add(oi)
    db.session.commit()
    return jsonify({'order': row_to_dict(order), 'items': [row_to_dict(x) for x in OrderItem.query.filter_by(order_id=order.order_id).all()]})

@app.route('/api/orders/list', methods=['GET'])
def list_orders():
    orders = Order.query.all()
    return jsonify([row_to_dict(o) for o in orders])

@app.route('/api/rides/create', methods=['POST'])
def create_ride():
    data = request.json or {}
    r = Ride(user_id=data['user_id'], driver_id=data['driver_id'], source=data['source'], destination=data['destination'], fare=data['fare'], status=data.get('status','requested'))
    db.session.add(r)
    db.session.commit()
    return jsonify(row_to_dict(r))

@app.route('/api/rides/list', methods=['GET'])
def list_rides():
    rides = Ride.query.all()
    return jsonify([row_to_dict(r) for r in rides])

@app.route('/api/payments/create', methods=['POST'])
def create_payment():
    data = request.json or {}
    p = Payment(user_id=data['user_id'], ride_id=data.get('ride_id'), order_id=data.get('order_id'), amount=data['amount'], mode=data['mode'], status=data.get('status','pending'))
    db.session.add(p)
    db.session.commit()
    return jsonify(row_to_dict(p))

@app.route('/api/payments/list', methods=['GET'])
def list_payments():
    payments = Payment.query.all()
    return jsonify([row_to_dict(p) for p in payments])

@app.route('/api/ratings/create', methods=['POST'])
def create_rating():
    data = request.json or {}
    r = Rating(user_id=data['user_id'], target_id=data['target_id'], target_type=data['target_type'], score=data['score'], comment=data.get('comment'))
    db.session.add(r)
    db.session.commit()
    return jsonify(row_to_dict(r))

@app.route('/api/ratings/list', methods=['GET'])
def list_ratings():
    ratings = Rating.query.all()
    return jsonify([row_to_dict(r) for r in ratings])

### Delete endpoints

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error':'not found'}), 404
    db.session.delete(u)
    db.session.commit()
    return jsonify({'status':'deleted', 'user_id': user_id})

@app.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    d = Driver.query.get(driver_id)
    if not d:
        return jsonify({'error':'not found'}), 404
    db.session.delete(d)
    db.session.commit()
    return jsonify({'status':'deleted', 'driver_id': driver_id})

@app.route('/api/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    r = Restaurant.query.get(restaurant_id)
    if not r:
        return jsonify({'error':'not found'}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({'status':'deleted', 'restaurant_id': restaurant_id})

@app.route('/api/menu_items/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    it = MenuItem.query.get(item_id)
    if not it:
        return jsonify({'error':'not found'}), 404
    db.session.delete(it)
    db.session.commit()
    return jsonify({'status':'deleted', 'item_id': item_id})

@app.route('/api/delivery_partners/<int:partner_id>', methods=['DELETE'])
def delete_partner(partner_id):
    p = DeliveryPartner.query.get(partner_id)
    if not p:
        return jsonify({'error':'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'status':'deleted', 'partner_id': partner_id})

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    o = Order.query.get(order_id)
    if not o:
        return jsonify({'error':'not found'}), 404
    # delete order items first
    OrderItem.query.filter_by(order_id=order_id).delete()
    db.session.delete(o)
    db.session.commit()
    return jsonify({'status':'deleted', 'order_id': order_id})

@app.route('/api/rides/<int:ride_id>', methods=['DELETE'])
def delete_ride(ride_id):
    r = Ride.query.get(ride_id)
    if not r:
        return jsonify({'error':'not found'}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({'status':'deleted', 'ride_id': ride_id})

@app.route('/api/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    p = Payment.query.get(payment_id)
    if not p:
        return jsonify({'error':'not found'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'status':'deleted', 'payment_id': payment_id})

@app.route('/api/ratings/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    r = Rating.query.get(rating_id)
    if not r:
        return jsonify({'error':'not found'}), 404
    db.session.delete(r)
    db.session.commit()
    return jsonify({'status':'deleted', 'rating_id': rating_id})

### CLI helper
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created.')


@app.cli.command('db_reset')
def db_reset():
    # Drop all tables and recreate (development convenience)
    db.drop_all()
    db.create_all()
    print('Database reset (dropped and recreated all tables).')

if __name__ == '__main__':
    app.run(debug=True)
