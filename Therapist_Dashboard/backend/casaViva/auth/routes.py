# Import necessary modules and packages
import base64
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pymongo.cursor import Cursor
import bcrypt
import jwt
import datetime
from . import auth_bp
from models import users as user_model
from models import therapist as therapist_model
from models.creatDocument import *
from models import session as session_model

def create_token(user_id,user_name,session_id=None):
    """
    Create a JWT token for the user.
    :param user_id: The ID of the user.
    :param user_name: The name of the user.
    :return: The JWT token.
    """

    payload = {
        "user_id": str(user_id),
        "user_name": user_name,
        "session_id": str(session_id) if session_id else None,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
    }
    
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """
    Decode the JWT token to get the user ID and username.
    :param token: The JWT token.
    :return: The decoded token data.
    """

    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None


def hash_password(password):
    salt = bcrypt.gensalt()  # salt
    hashed = bcrypt.hashpw(password.encode(), salt)
    hashed = base64.b64encode(hashed).decode('utf-8')
    return hashed

def verify_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode()  # Codifica para bytes
    
    return bcrypt.checkpw(password.encode(), base64.b64decode(hashed))

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    :return: JSON response with the user ID and a success message.
    """

    data = request.get_json()
    name = data.get('name')
    email = data.get('email').lower()
    password = data.get('password')
    therapist = data.get('therapist')
    email_therapist = data.get('email_therapist')
    age = data.get('age')

    if user_model.get_user_by_email(email):
        return jsonify({"error": "Email já registrado"}), 400


    hashed_pw = hash_password(password)

    documento = CreatDocumentToDB()
    doc = documento.userCasaVivaDocument(name=name, email=email, age=age, therapist=therapist, email_therapist=email_therapist, password=hashed_pw)
    user_id = user_model.create_user(doc)

    return jsonify({"message": "Utilizador registrado", "id": str(user_id)}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user and return a JWT token.
    :return: JSON response with the JWT token and user information.
    """

    data = request.get_json()
    email = data.get('email').lower()
    password = data.get('password')

    user = user_model.get_user_by_email(email)
    if not user or not verify_password(password, user['password']):
        return jsonify({"error": "Credenciais inválidas"}), 401

    status = create_session(user['_id'])
    if not status:
        return jsonify({"error": "Erro ao criar sessão"}), 500
    
    token = create_token(user['_id'], user['name'], status)


    return jsonify({'token': token, 'user': {'userId': str(user['_id']), 'name': user['name'], 'email': user['email'], 'therapist': user['therapist'], 'email_therapist': user['email_therapist'], 'age': user['age']}}), 200


def create_session(userId):
    """
    Create a new session.
    :return: JSON response with the created session data.
    """
    
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    start = datetime.datetime.now().strftime('%H:%M:%S')

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos."}), 400

    session_data = {
        "user": ObjectId(userId),
        "date": today,
        "start": start,
        "end": None
    }


    session_id = session_model.create_session(session_data)
    if not session_id:
        return None

    return  str(session_id)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout a user and invalidate the JWT token.
    :return: JSON response with a success message.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        session_id = decoded['session_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    endDate = datetime.datetime.now().strftime('%H:%M:%S')

    status = session_model.update_session(session_id, endDate)

    if not status:
        return jsonify({"error": "Erro ao atualizar sessão."}), 500

    return jsonify({"message": "Logout realizado com sucesso."}), 200

# Exemplo de rota protegida
@auth_bp.route('/user', methods=['GET'])
def get_profile():
    """
    Get the current user's profile information.
    :return: JSON response with the user's profile information.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        user_id = decoded['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    user = user_model.get_user_by_id(user_id)

    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    return jsonify({"user": {"id": str(user['_id']), "name": user['name'], "email": user['email'], "age": user['age'], "therapist": user['therapist'], "email_therapist": user['email_therapist']}}), 200