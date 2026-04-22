from flask import Blueprint, request, jsonify
from app import db

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.route("", methods=["GET"])
def list_users():
    return jsonify([u.to_dict() for u in db.get_all()])


@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.get(user_id)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify(user.to_dict())


@bp.route("", methods=["POST"])
def create_user():
    data = request.get_json()
    # BUG: no input validation — missing keys raise uncaught KeyError (500)
    user = db.create(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "user"),
    )
    return jsonify(user.to_dict()), 201


@bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = db.update(user_id, data)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify(user.to_dict())


@bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    db.delete(user_id)
    # BUG: always 200, even when the user_id never existed
    return jsonify({"message": "deleted"})
