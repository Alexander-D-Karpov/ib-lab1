from flask import Blueprint, g, jsonify, request
from markupsafe import escape

from app.auth import generate_token, token_required
from app.models import Crystal, Purchase, User, db

api = Blueprint("api", __name__)


@api.post("/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "username already taken"}), 409

    user = User(username=username, balance=1000)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "username": str(escape(username))}), 201


@api.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify({"token": generate_token(user)})


@api.get("/api/data")
@token_required
def get_data():
    crystals = Crystal.query.order_by(Crystal.id).all()
    return jsonify(
        {
            "user": str(escape(g.current_user.username)),
            "balance": g.current_user.balance,
            "crystals": [
                {
                    "id": c.id,
                    "color": str(escape(c.color)),
                    "price": c.price,
                    "stock": c.stock,
                }
                for c in crystals
            ],
        }
    )


@api.post("/api/buy")
@token_required
def buy():
    data = request.get_json(silent=True) or {}
    crystal_id = data.get("crystal_id")
    quantity = data.get("quantity", 1)

    if not isinstance(crystal_id, int) or not isinstance(quantity, int):
        return jsonify({"error": "crystal_id and quantity must be integers"}), 400
    if quantity <= 0:
        return jsonify({"error": "quantity must be positive"}), 400

    crystal = db.session.get(Crystal, crystal_id)
    if crystal is None:
        return jsonify({"error": "crystal not found"}), 404
    if crystal.stock < quantity:
        return jsonify({"error": "not enough stock"}), 409

    total = crystal.price * quantity
    user = g.current_user
    if user.balance < total:
        return jsonify({"error": "insufficient balance"}), 402

    crystal.stock -= quantity
    user.balance -= total
    purchase = Purchase(
        user_id=user.id,
        crystal_id=crystal.id,
        quantity=quantity,
        total_price=total,
    )
    db.session.add(purchase)
    db.session.commit()

    return (
        jsonify(
            {
                "purchase_id": purchase.id,
                "color": str(escape(crystal.color)),
                "quantity": quantity,
                "total_price": total,
                "balance": user.balance,
            }
        ),
        201,
    )
