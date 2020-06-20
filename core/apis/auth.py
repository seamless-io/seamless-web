from flask import Blueprint, jsonify

from core.db.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    return jsonify({'logging': 'success'}), 200
