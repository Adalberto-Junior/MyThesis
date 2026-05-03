#=========================================================================
# Flaskr - Authentication Routes
### This file is part of the Flaskr project.
# Author: Adalberto Júnior
# Date: 2025-04-30
# Description: This file contains the routes for the authentication system.
# It includes the login and logout routes, as well as the registration route.
# It also includes the functions for checking if a user is logged in and for getting the current user.
#=========================================================================

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
# from models import users as user_model
from models import therapist as therapist_model
from models.creatDocument import *

def create_token(user_id,user_name):
    """
    Create a JWT token for the user.
    :param user_id: The ID of the user.
    :param user_name: The name of the user.
    :return: The JWT token.
    """

    payload = {
        "user_id": str(user_id),
        "user_name": user_name,
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
    profession = data.get('profession')
    date_birth = data.get('date_birth')

    if therapist_model.get_therapist_by_email(email):
        return jsonify({"error": "Email já registrado"}), 400


    # hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_pw = hash_password(password)

    docuemnto = CreatDocumentToDB()
    doc = docuemnto.userDocument(name=name, email=email, profession=profession, date_of_birth=date_birth, password=hashed_pw,)
    user_id = therapist_model.create_therapist(doc)

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

    user = therapist_model.get_therapist_by_email(email)
    if not user or not verify_password(password, user['password']):
        return jsonify({"error": "Credenciais inválidas"}), 401

    #payload = {
    #    'user_id': str(user['_id']),
    #    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    #}
    # token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    token = create_token(user['_id'], user['name'])
    # print(token)
    
    return jsonify({'token': token, 'user': {'id': str(user['_id']), 'name': user['name']}})

# Exemplo de rota protegida
@auth_bp.route('/me', methods=['GET'])
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

    user = therapist_model.get_therapist_by_id(user_id)

    # print(user)

    if not user:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    return jsonify({"user": {"id": str(user['_id']), "name": user['name'], "email": user['email'], "profession": user['profession'], "date_of_birth": user['date_of_birth']}}), 200

# Exemplo de rota protegida
@auth_bp.route('/notas', methods=['GET'])
def get_notas():
    """
    Get the current user's notes.
    :return: JSON response with the user's notes.
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

    notes = therapist_model.get_therapist_notes_by_therapist_id(user_id)

    if not notes:
        return jsonify({"error": "Ainda não há notas"}), 404

    if isinstance(notes, Cursor):
        notes = list(notes)

    return jsonify(notes), 200

# Exemplo de rota protegida
@auth_bp.route('/notas', methods=['POST'])
def add_notas():
    """
    Add the current user's notes.
    :return: JSON response with the user's notes.
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
    
    data = request.get_json()
    note = data.get('texto')
    priority = data.get('prioridade')
    date = data.get('data')
    dataExecucao = data.get('dataExecucao')
    category = data.get('categoria')
    done = data.get('done')

    documento = CreatDocumentToDB()
    doc = documento.noteDocument(note=note, priority=priority, date=date, dataExecucao=dataExecucao, category=category, done=done, therapist=user_id)

    noteId = therapist_model.create_therapist_note(doc)

   
    return jsonify({"message": "Nota Guardado com sucesso", "id": str(noteId)}), 201

@auth_bp.route('/notas/<note_id>', methods=['PUT'])
def update_notas(note_id):
    """
    Update a user's note.
    :param note_id: The ID of the note to update.
    :return: JSON response with the updated note.
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

    data = request.get_json()
    note = data.get('note')
    priority = data.get('priority')
    date = data.get('date')
    dataExecucao = data.get('dataExecucao')
    category = data.get('category')
    done = data.get('done')

    documento = CreatDocumentToDB()
    doc = documento.noteDocument(note=note, priority=priority, date=date, dataExecucao=dataExecucao, category=category, done=done, therapist=user_id)

    updated_note = therapist_model.update_therapist_note(note_id, doc)

    if not updated_note:
        return jsonify({"error": "Nota não encontrada"}), 404

    return jsonify({"message": "Nota atualizada com sucesso", "note": updated_note}), 200


@auth_bp.route('/notas/<note_id>', methods=['DELETE'])
def delete_notas(note_id):
    """
    Delete a user's note.
    :param note_id: The ID of the note to delete.
    :return: JSON response indicating the result of the deletion.
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

    deleted = therapist_model.delete_therapist_note(note_id)

    if not deleted:
        return jsonify({"error": "Nota não encontrada"}), 404

    return jsonify({"message": "Nota deletada com sucesso"}), 200