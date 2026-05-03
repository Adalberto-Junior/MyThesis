#=================================================================================================================
# Author:      Adalberto Júnior
# Date:        2025-04-30
# Version:     1.0
# Python:      3.10
# Local:       UA, Aveiro
# Description: This file contains the routes for the health user management system.
# It includes the routes for getting health user information, updating health user information, and deleting a user.
# It also includes the routes for getting health user results and deleting health user results.
#=================================================================================================================

# Import necessary modules and packages
from flask import request, jsonify, current_app, make_response
from pymongo.cursor import Cursor
from werkzeug.security import generate_password_hash, check_password_hash
# from bson.objectid import ObjectId
from bson import ObjectId
from bson.errors import InvalidId
import bcrypt
import jwt
import datetime
import os
from werkzeug.utils import secure_filename

from . import utente_bp
# from models import users as user_model
# from models import therapist as therapist_model
from models import analysisResult as result_model
from models import exercise as exercise_model
from models import utente as utente_model
from models import users as user_model
from models import recording as record_model
from models.creatDocument import *

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

def verifyAuth():
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        therapist_id = decoded['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401
    
    return therapist_id

def is_objectid(value):
    """
    Verifica se o valor é um ObjectId válido do MongoDB.
    Aceita tanto instâncias ObjectId quanto strings no formato correto.
    """
    # Caso já seja uma instância de ObjectId
    if isinstance(value, ObjectId):
        return True
    
    # Caso seja string, tenta converter
    if isinstance(value, str):
        try:
            ObjectId(value)  # Tentativa de conversão
            return True
        except (InvalidId, TypeError):
            return False
    
    return False 
    
@utente_bp.route('/', methods=['POST'])
def register_utente():
    """
    Register a new health user.
    :return: JSON response with the user ID and a success message.
    """
   

    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapist_id = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401
    therapist_id = verifyAuth()
    
    if not is_objectid(therapist_id):
        return jsonify({"error": "Falha na autenticação"}), 401
    
    data = request.get_json()
    name = data.get('name')
    email = data.get('email').lower()
    observation = data.get('observation')
    medical_condition = data.get('medical_condition')
    date_birth = data.get('date_birth')
    health_user_number = data.get('health_user_number')
    cellphone = data.get('health_user_cellphone')
    address = data.get('health_user_address')

    if utente_model.get_health_user_by_email(email):
        return jsonify({"error": " Já há utente com este email registrado"}), 400

    docuemnto = CreatDocumentToDB()
    doc = docuemnto.healthUserDocument(name=name, email=email, date_of_birth=date_birth, observation=observation, medical_condition=medical_condition, therapist=therapist_id, health_user_number=health_user_number, cellphone=cellphone, address=address)
    health_user_id = utente_model.create_health_user(doc)



    return jsonify({"message": "Utente registrado com sucesso", "id": str(health_user_id)}), 201

@utente_bp.route('/', methods=['GET'])
def get_utente():
    """
    Get the health users information by Therapist ID.
    :return: JSON response with the health users information.
    """

    # print("estou aqui no get Utente 1")

    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401
    
    # print("estou aqui no get Utente")

    health_users = utente_model.get_all_health_users_by_therapist(therapistId)

    if not health_users:
        return jsonify({"error": "Utentes não encontrado"}), 404
    
    if isinstance(health_users, Cursor):
        health_users = list(health_users)

    return jsonify(health_users), 200

@utente_bp.route('/informacao/<string:user_id>', methods=['GET'])
def get_utente_by_id(user_id):
    """
    Get the health user information by user ID.
    :param user_id: The ID of the health user.
    :return: JSON response with the health user information.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    health_user = utente_model.get_health_user_by_id(user_id)

    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    # response_data = health_user
    # response = make_response(jsonify(response_data))
    # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # response.headers["Pragma"] = "no-cache"
    # response.headers["Expires"] = "0"
    
    # return response

    # return jsonify(list(health_user)), 200
    return jsonify(health_user), 200

@utente_bp.route('/informacao/<string:user_id>', methods=['PUT'])
def update_utente(user_id):
    """
    Update the health user information by user ID.
    :param user_id: The ID of the health user.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401
    
    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    data = request.get_json()
    name = data.get('name')
    email = data.get('email').lower()
    observation = data.get('observation')
    medical_condition = data.get('medical_condition')
    date_birth = data.get('date_of_birth')
    health_user_number = data.get('health_user_number')
    cellphone = data.get('cellphone')
    address = data.get('address')

    documento = CreatDocumentToDB()
    doc = documento.healthUserDocument(name=name, email=email, date_of_birth=date_birth, observation=observation, medical_condition=medical_condition, therapist=therapistId, health_user_number=health_user_number, cellphone=cellphone, address=address)


    health_user = utente_model.update_health_user(user_id, doc)

    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    return jsonify({"message": "Utente atualizado com sucesso"}), 200

@utente_bp.route('/informacao/<string:user_id>', methods=['DELETE'])
def delete_utente(user_id):
    """
    Delete the health user by user ID.
    :param user_id: The ID of the health user.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401
    
    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    health_user = utente_model.get_health_user_by_id(user_id)

    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    utente_model.delete_health_user(user_id)

    return jsonify({"message": "Utente deletado com sucesso"}), 200

@utente_bp.route('/informacao/<string:health_user_name>', methods=['GET'])
def get_utente_by_name(health_user_name):
    """
    Get the health user information by user name and therapist id.
    :param health_user_name: The name of the health user.
    :return: JSON response with the health user information.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404

    return jsonify(health_user), 200


@utente_bp.route('/<string:user_id>/analise/fonacao', methods=['GET'])
def get_analise_fonacao(user_id):
    """
    Get the phonation analysis results for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the analysis results.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    analysis_results = result_model.get_result_by_user_and_processingtype(casa_viva_user['_id'],'phonation')

    if not analysis_results:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    if isinstance(analysis_results, Cursor):
        analysis_results = list(analysis_results)

    
    for result in analysis_results:
        recordId = result.get('recording')
        if recordId:
            record = record_model.get_recording_by_id(recordId)
            result['pathToRecord'] = record.get('path') if record else None
    
    return jsonify(analysis_results), 200

@utente_bp.route('/<string:user_id>/analise/articulacao', methods=['GET'])
def get_analise_articulacao(user_id):
    """
    Get the articulation analysis results for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the articulation analysis results.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401
    
    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    analysis_results = result_model.get_result_by_user_and_processingtype(casa_viva_user['_id'],'articulation')

    if not analysis_results:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    if isinstance(analysis_results, Cursor):
        analysis_results = list(analysis_results)

    for result in analysis_results:
        recordId = result.get('recording')
        if recordId:
            record = record_model.get_recording_by_id(recordId)
            result['pathToRecord'] = record.get('path') if record else None

    return jsonify(analysis_results), 200

@utente_bp.route('/<string:user_id>/analise/prosodia', methods=['GET'])
def get_analise_prosodia(user_id):
    """
    Get the prosody analysis results for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the prosody analysis results.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    analysis_results = result_model.get_result_by_user_and_processingtype(casa_viva_user['_id'],'prosody')

    if not analysis_results:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    if isinstance(analysis_results, Cursor):
        analysis_results = list(analysis_results)
    
    for result in analysis_results:
        recordId = result.get('recording')
        if recordId:
            record = record_model.get_recording_by_id(recordId)
            result['pathToRecord'] = record.get('path') if record else None

    return jsonify(analysis_results), 200

@utente_bp.route('/<string:user_id>/analise/glotal', methods=['GET'])
def get_analise_glotal(user_id):
    """
    Get the glottal analysis results for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the glottal analysis results.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    analysis_results = result_model.get_result_by_user_and_processingtype(casa_viva_user['_id'],'glottal')

    if not analysis_results:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    if isinstance(analysis_results, Cursor):
        analysis_results = list(analysis_results)
    
    for result in analysis_results:
        recordId = result.get('recording')
        if recordId:
            record = record_model.get_recording_by_id(recordId)
            result['pathToRecord'] = record.get('path') if record else None

    return jsonify(analysis_results), 200

@utente_bp.route('/<string:user_id>/analise/reaprendizado', methods=['GET'])
def get_analise_reaprendizado(user_id):
    """
    Get the replearning analysis results for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the replearning analysis results.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    analysis_results = result_model.get_result_by_user_and_processingtype(casa_viva_user['_id'],'replearning')

    if not analysis_results:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    if isinstance(analysis_results, Cursor):
        analysis_results = list(analysis_results)

    for result in analysis_results:
        recordId = result.get('recording')
        if recordId:
            record = record_model.get_recording_by_id(recordId)
            result['pathToRecord'] = record.get('path') if record else None

    return jsonify(analysis_results), 200

@utente_bp.route('/<string:user_id>/analise/fonologica', methods=['GET'])
def get_analise_fonologica(user_id):
    """
    Get the phonological analysis results for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the phonological analysis results.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    analysis_results = result_model.get_result_by_user_and_processingtype(casa_viva_user['_id'],'phonological')

    if not analysis_results:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    if isinstance(analysis_results, Cursor):
        analysis_results = list(analysis_results)
    
    for result in analysis_results:
        recordId = result.get('recording')
        if recordId:
            record = record_model.get_recording_by_id(recordId)
            result['pathToRecord'] = record.get('path') if record else None

    return jsonify(analysis_results), 200

@utente_bp.route('/<string:user_id>/analise/<string:analise_Id>', methods=['Delete'])
def delete_analise(user_id, analise_Id):
    """
    Delete a specific analysis result by its ID for a specific health user by their id.
    :param user_id: The id of the health user.
    :param analise_Id: The ID of the analysis result to be deleted.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    result = result_model.delete_result(analise_Id)

    if not result:
        return jsonify({"error": "Resultado de análise não encontrado"}), 404
    
    return jsonify({"message": "Resultado de análise deletado com sucesso"}), 200

@utente_bp.route('/<string:user_id>/analise/<string:type_of_processing>/<string:date>', methods=['DELETE'])
def delete_analise_by_type_and_date(user_id, type_of_processing, date):
    """
    Delete all analysis results of a specific type and date for a specific health user by their id.
    :param user_id: The id of the health user.
    :param type_of_processing: The type of processing (e.g., 'phonation', 'articulation').
    :param date: The date of the analysis results to be deleted.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    result = result_model.delete_result_by_user_type_and_date(casa_viva_user['_id'], type_of_processing, date)

    if not result:
        return jsonify({"error": "Resultados de análise não encontrados"}), 404
    
    return jsonify({"message": "Resultados de análise deletados com sucesso"}), 200

@utente_bp.route('/<string:user_id>/exercicio/', methods=['GET'])
def get_exercicios(user_id):
    """
    Get the exercises for a specific health user by their id.
    :param user_id: The id of the health user.
    :return: JSON response with the exercises.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)

    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    exercises = exercise_model.get_exercise_by_health_user(casa_viva_user['_id'])

    if not exercises:
        return jsonify({"error": "Exercícios não encontrados"}), 404
    
    if isinstance(exercises, Cursor):
        exercises = list(exercises)
    
    if exercises:
        for exercise in exercises:
            if exercise.get('exerciseId'):
                new_exercise = exercise_model.get_exercise_by_id(exercise['exerciseId'])
                if new_exercise:
                    del new_exercise['_id']  # <- remove o campo _id do dict
                    exercise.update(new_exercise)  # <- modifica o dict da lista
                    del exercise['exerciseId']  # <- remove o campo exerciseId do dict


                

    return jsonify(exercises), 200

@utente_bp.route('/exercicio/<string:exercise_id>/', methods=['GET'])
def get_exercicio(exercise_id):
    """
    Get the a specific exercise by their id.
    :param exercise_id: The id of the health user.
    :return: JSON response with the exercise.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    exercise = exercise_model.get_exercise_by_id(exercise_id)

    if not exercise:
        return jsonify({"error": "Exercício não encontrados"}), 404
    
    # if isinstance(exercises, Cursor):
    #     exercises = list(exercises)

    if exercise.get('exerciseId'):
        new_exercise = exercise_model.get_exercise_by_id(exercise['exerciseId'])
        if new_exercise:
            del new_exercise['_id']  # <- remove o campo _id do dict
            exercise.update(new_exercise) 
            del exercise['exerciseId']  

    return jsonify(exercise), 200

@utente_bp.route('/exercicio/', methods=['GET'])
def get_all_exercicio():
    """
    Get the exercises in the database.
    :return: JSON response with the exercises.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    exercises = exercise_model.get_exerciseGeneric(therapistId)

    if not exercises:
        return jsonify({"error": "Exercícios não encontrados"}), 404
    
    if isinstance(exercises, Cursor):
        exercises = list(exercises)
    
    # print(exercises)

    return jsonify(exercises), 200

@utente_bp.route('/exercicios/tipo/<string:type>/', methods=['GET'])
def get_all_exercise_by_type(type):
    """
    Get all exercises by type in the database.
    :param type: The type of the exercise.
    :return: JSON response with the exercises.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    exercises = exercise_model.get_exercise_by_type(type)
    # print(exercises)

    if not exercises:
        return jsonify({"error": "Exercícios não encontrados"}), 404
    
    if isinstance(exercises, Cursor):
        exercises = list(exercises)
    
    # print(exercises)

    return jsonify(exercises), 200


@utente_bp.route('/<string:user_id>/exercicio/', methods=['POST'])
def add_exercicio(user_id):
    """
    Add a new exercise for a specific health user by their id.
    :param user_id: The name of the health user.
    :return: JSON response with the exercise ID and a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401
    
    # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)

    health_user = utente_model.get_health_user_by_id(user_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    data = request.get_json()
    # print(data)
    if data.get('edit'):
        exercise_id = data.get('id')
        userId = data.get('userId')
        if not exercise_model.get_exercise_by_id(exercise_id):
            return jsonify({"error": "Exercício não encontrado"}), 404
        documento = CreatDocumentToDB()
        doc = documento.exerciseDocumentWithExerciseId(exercise=exercise_id, userId=casa_viva_user['_id'], userName=casa_viva_user['name'], therapist=therapistId)
        exercise_id = exercise_model.create_exercise(doc)
    else:
        name = data.get('name')
        type = data.get('type')
        description = data.get('description') if data.get('description') else None
        typeOfProcessing = data.get('typeOfProcessing')
        # video_url = data.get('video_url')
        steps = data.get('steps')

        if exercise_model.get_exercise_by_name(name):
            return jsonify({"error": "Já há exercício com este nome registrado"}), 400

        docuemnto = CreatDocumentToDB()
        doc = docuemnto.exerciseDocument(name=name, type=type, description=description, userName=casa_viva_user['name'], user=casa_viva_user['_id'], steps=steps,typeOfProcessing=typeOfProcessing, therapist=therapistId)
        
        exercise_id = exercise_model.create_exercise(doc)

    return jsonify({"message": "Exercício adicionado com sucesso", "id": str(exercise_id)}), 201

@utente_bp.route('/exercicio/', methods=['POST'])
def add_generic_exercicio():
    """
    Add a new exercise in database.
    :return: JSON response with the exercise ID and a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    data = request.get_json()
    name = data.get('name')
    type = data.get('type')
    description = data.get('description') if data.get('description') else None
    typeOfProcessing = data.get('typeOfProcessing')
    steps = data.get('steps')

    if exercise_model.get_exercise_by_name(name):
        return jsonify({"error": "Já há exercício com este nome registrado"}), 400

    docuemnto = CreatDocumentToDB()
    doc = docuemnto.genericExerciseDocument(name=name, type=type, description=description, steps=steps,typeOfProcessing=typeOfProcessing, therapist=therapistId)
    
    exercise_id = exercise_model.create_exercise(doc)

    return jsonify({"message": "Exercício adicionado com sucesso", "id": str(exercise_id)}), 201

@utente_bp.route('/exercicio/<string:exercise_id>/', methods=['PUT'])
def update_exercicio(exercise_id):
    """
    Update an existing exercise for a specific health user by their id.
    :param exercise_id: The ID of the exercise to be updated.
    :return: JSON response with a success message.
    """
    
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401
    
    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401
    
    
    if not exercise_id:
        return jsonify({"error": "ID do exercício não fornecido"}), 400

    if not exercise_model.get_exercise_by_id(exercise_id):
        return jsonify({"error": "Exercício não encontrado"}), 404

    data = request.get_json()
    # print(data)
    name = data.get('name')
    type = data.get('type')
    description = data.get('description') if data.get('description') else None
    userID = data.get('user') if data.get('user') else ""
    typeOfProcessing = data.get('typeOfProcessing')
    therapist = therapistId
    userName = data.get('userName') if data.get('userName') else None

    steps = data.get('steps')

    documento = CreatDocumentToDB()
    doc = documento.exerciseDocument(name=name, type=type, description=description, userName=userName, user=userID, steps=steps, therapist=therapist, typeOfProcessing=typeOfProcessing)
    exercise = exercise_model.update_exercise(exercise_id, doc)

    if not exercise:
        return jsonify({"error": "Exercício não encontrado"}), 404

    return jsonify({"Sucess": "Exercício atualizado com sucesso"}), 200

@utente_bp.route('/exercicio/<string:exercise_id>/', methods=['DELETE'])
def delete_exercicio(exercise_id):
    """
    Delete an existing exercise for a specific health user by their id.
    :param exercise_id: The ID of the exercise to be deleted.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    exercise = exercise_model.delete_exercise(exercise_id)

    if not exercise:
        return jsonify({"error": "Exercício não encontrado"}), 404

    return jsonify({"Sucess": "Exercício deletado com sucesso"}), 200




# #TODO: Verificar isso
# @utente_bp.route('/<string:user_id>/exercicio/update/<string:exercise_id>', methods=['PUT'])
# def update_exercicio(user_id, exercise_id):
#     """
#     Update an existing exercise for a specific health user by their id.
#     :param user_id: The id of the health user.
#     :param exercise_id: The ID of the exercise to be updated.
#     :return: JSON response with a success message.
#     """
#     token = request.headers.get('Authorization')
#     if not token or not token.startswith("Bearer "):
#         return jsonify({"error": "Token ausente"}), 401

#     try:
#         token = token.replace("Bearer ", "")
#         decoded = decode_token(token)
#         therapistId = decoded['user_id']
#     except jwt.ExpiredSignatureError:
#         return jsonify({"error": "Token expirado"}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({"error": "Token inválido"}), 401

#     # health_user = utente_model.get_health_user_by_username_and_therapist(health_user_name, therapistId)
#     health_user = utente_model.get_health_user_by_id(user_id)

#     if not health_user:
#         return jsonify({"error": "Utente não encontrado"}), 404
    
#     casa_viva_user = user_model.get_user_by_email(health_user['email'])

#     if not casa_viva_user:
#         return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

#     data = request.get_json()
#     name = data.get('name')
#     type = data.get('type')
#     description = data.get('description')
#     video_url = data.get('video_url')
#     steps = data.get('steps')

#     docuemnto = CreatDocumentToDB()
#     doc = docuemnto.exerciseDocument(name=name, type=type, description=description, userName=casa_viva_user['name'], user=casa_viva_user['_id'], steps=steps)
#     exercise = exercise_model.update_exercise(exercise_id, doc)

#     if not exercise:
#         return jsonify({"error": "Exercício não encontrado"}), 404
    
#     return jsonify({"Sucess": "Exercício atualizado com sucesso"}), 200


@utente_bp.route('/<string:utente_id>/relatorio/', methods=['POST'])
def generate_relatorio(utente_id):
    """
    Generate a report for a specific health user by their id.
    :param utente_id: The id of the health user.
    :return: JSON response with the report data.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

 

    health_user = utente_model.get_health_user_by_id(utente_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email'])

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404
    
    data = request.json
    
    utenteId = casa_viva_user['_id']
    therapist = therapistId
    title = data["title"]
    type_of_analysis =  data["type_of_analysis"]
    observations =  data["observations"]
    recommendations = data["recommendations"]
    internal_note = data.get("internal_note", "")
    status = data["status"]
    analysis_date = data["analysis_date"]
    # created_at = datetime.utcnow()
    created_at = data["created_at"]
    analysis = data["analises"]

    document = CreatDocumentToDB()
    doc = document.relatoryDocument(
        utenteId=utenteId,
        therapist=therapistId,
        title=title,
        type_of_analysis=type_of_analysis,
        observations=observations,
        recommendations=recommendations,
        internal_note=internal_note,
        status=status,
        analysis_date=analysis_date,
        created_at=created_at,
        analysis=analysis
    )
    relatory = utente_model.create_health_user_relatory(doc)
    if not relatory:
        return jsonify({"error": "Erro ao salvar o relatório"}), 500
    
    return jsonify({"message": "Relatório salvo com sucesso."}), 201

@utente_bp.route('/<string:utente_id>/relatorio/', methods=['GET'])
def get_relatorio(utente_id):
    """
    Get the reports for a specific health user by their id.
    :param utente_id: The id of the health user.
    :return: JSON response with the reports data.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    health_user = utente_model.get_health_user_by_id(utente_id)
    if not health_user:
        return jsonify({"error": "Utente não encontrado"}), 404
    
    casa_viva_user = user_model.get_user_by_email(health_user['email']) #TODO: Verificar se é necessário fazer a busca pelo email do utente na casa viva

    if not casa_viva_user:
        return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

    relatories = utente_model.get_health_user_relatory_by_user_id(casa_viva_user['_id'])
    
    if not relatories:
        return jsonify({"error": "Relatórios não encontrados"}), 404
    
    if isinstance(relatories, Cursor):
        relatories = list(relatories)
    

    return jsonify(relatories), 200

@utente_bp.route('/relatorio/<string:reportId>/', methods=['GET'])
def get_relatorio_by_id(reportId):
    """
    Get a specific report by its ID.
    :param reportId: The ID of the report to be retrieved.
    :return: JSON response with the report data.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401

    relatory = utente_model.get_health_user_relatory_by_id(reportId)

    if not relatory:
        return jsonify({"error": "Relatório não encontrado"}), 404
    
    return jsonify(relatory), 200


@utente_bp.route('/relatorio/<string:reportId>', methods=['PUT'])
def update_relatorio(reportId):
    """
    Update a specific report by its ID.
    :param reportId: The ID of the report to be updated.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401
    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401
    
    
    data = request.get_json()
    
    title = data["title"]
    type_of_analysis =  data["type_of_analysis"]
    observations =  data["observations"]
    recommendations = data["recommendations"]
    internal_note = data.get("internal_note", "")
    status = data["status"]
    analysis_date = data["analysis_date"]
    views = data["views"]
    created_at = data["created_at"]
    analysis = data["analises"]

    health_user_report = utente_model.get_health_user_relatory_by_id(reportId)
    if not health_user_report:
        return jsonify({"error": "Relatório não encontrado"}), 404
    
    document = CreatDocumentToDB()
    doc = document.relatoryDocument(
        utenteId=health_user_report['utente_id'],
        therapist=therapistId,
        title=title,
        type_of_analysis=type_of_analysis,
        observations=observations,
        recommendations=recommendations,
        internal_note=internal_note,
        status=status,
        analysis_date=analysis_date,
        views=views,
        created_at=created_at,
        analysis=analysis
    )
    
    relatory = utente_model.update_health_user_relatory(reportId, doc)

    if not relatory:
        return jsonify({"error": "Erro ao atualizar o relatório"}), 500
    
    return jsonify({"message": "Relatório atualizado com sucesso."}), 200

@utente_bp.route('/<string:reportId>/relatorio/', methods=['DELETE'])
def delete_relatorio(reportId):
    """
    Delete a specific report by its ID.
    :param reportId: The ID of the report to be deleted.
    :return: JSON response with a success message.
    """
    # token = request.headers.get('Authorization')
    # if not token or not token.startswith("Bearer "):
    #     return jsonify({"error": "Token ausente"}), 401

    # try:
    #     token = token.replace("Bearer ", "")
    #     decoded = decode_token(token)
    #     therapistId = decoded['user_id']
    # except jwt.ExpiredSignatureError:
    #     return jsonify({"error": "Token expirado"}), 401
    # except jwt.InvalidTokenError:
    #     return jsonify({"error": "Token inválido"}), 401

    therapistId = verifyAuth()
    if not is_objectid(therapistId):
        return jsonify({"error": "Falha na autenticação"}), 401


    relatory = utente_model.delete_health_user_relatory(reportId)

    if not relatory:
        return jsonify({"error": "Relatório não encontrado"}), 404
    
    return jsonify({"message": "Relatório deletado com sucesso."}), 200



############################################



# app = Flask(__name__)
# CORS(app)  # Permite requests do frontend React

# # Configurações
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# # Conecta ao MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["speech_therapy"]
# exercises_collection = db["exercises"]

# # Rota para criar exercício
@utente_bp.route("/rehabilitation/<string:utenteId>/exercises/", methods=["POST"])
def create_exercise(utenteId):
    """
    Cria um novo exercício de reabilitação para um utente específico.

    """
    try:
        # token = request.headers.get('Authorization')
        # if not token or not token.startswith("Bearer "):
        #     return jsonify({"error": "Token ausente"}), 401

        # try:
        #     token = token.replace("Bearer ", "")
        #     decoded = decode_token(token)
        #     therapistId = decoded['user_id']
        # except jwt.ExpiredSignatureError:
        #     return jsonify({"error": "Token expirado"}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({"error": "Token inválido"}), 401

        therapistId = verifyAuth()
        if not is_objectid(therapistId):
            return jsonify({"error": "Falha na autenticação"}), 401

        health_user = utente_model.get_health_user_by_id(utenteId)
        if not health_user:
            return jsonify({"error": "Utente não encontrado"}), 404
        
        casa_viva_user = user_model.get_user_by_email(health_user['email'])

        if not casa_viva_user:
            return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404
        
        # Dados do formulário
        # Campos de texto
        data = request.form.to_dict()
        # print("Dados recebidos:", data)

        if not data:
            return jsonify({"error": "Dados ausentes"}), 400

        title = data.get("title")
        category = data.get("category")
        objective = data.get("objective")
        description = data.get("description")
        duration = data.get("duration")
        repetitions = data.get("repetitions")
        difficulty = data.get("difficulty")
        feedback = data.get("feedback")
        notes = data.get("notes")

        # Passos (JSON)
        steps = data.get("steps")
        if steps:
            import json
            steps = json.loads(steps)
        else:
            steps = []

        # Ficheiros
        def save_files1(files, subfolder):
            paths = []
            folder_path = os.path.join( current_app.config["UPLOAD_FOLDER"], subfolder)
            os.makedirs(folder_path, exist_ok=True)
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)
                paths.append(file_path)
            return paths

        def save_files(files, subfolder, userName=None):
            """
            Guarda múltiplos ficheiros e retorna os caminhos relativos (para o frontend).
            
            :param files: lista de ficheiros (request.files.getlist(...))
            :param subfolder: subpasta (ex: "articulation", "prosody", "reaprendizagem")
            :param userName: nome do utente (opcional, se quiseres organizar por utilizador)
            :return: lista de caminhos relativos (para o React/HTML usar nas <img>)
            """
            paths = []
            
            # Pasta base configurada no Flask (ex: "static/uploads")
            folder_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], 
                userName if userName else "", 
                subfolder
            )
            os.makedirs(folder_path, exist_ok=True)

            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(folder_path, filename)
                file.save(file_path)

                # caminho relativo acessível pelo frontend
                rel_path = os.path.relpath(file_path, current_app.static_folder)
                paths.append(f"/static/{rel_path.replace(os.sep, '/')}")
            
            return paths

        images = save_files(request.files.getlist("images"), "images", userName=casa_viva_user['name'])
        videos = save_files(request.files.getlist("videos"), "videos", userName=casa_viva_user['name'])
        audios = save_files(request.files.getlist("audios"), "audios", userName=casa_viva_user['name'])

        


        document = CreatDocumentToDB()

        doc = document.rehabilitationExerciseDocument(title=title, category=category, objective=objective, description=description, duration=duration, repetitions=repetitions, difficulty=difficulty, feedback=feedback, notes=notes, steps=steps, images=images, videos=videos, audios=audios, user=casa_viva_user['_id'], userName=casa_viva_user['name'], therapist=therapistId)

        exerciseId = exercise_model.createRehabilitationExercise(doc)

        if exerciseId:
            return jsonify({"success": True, "exercise": exerciseId}), 201

        return jsonify({"success": False, "error": "Failed to create exercise"}), 500

    except Exception as e:
        # print(e)
        return jsonify({"success": False, "error": str(e)}), 500
    

@utente_bp.route("/rehabilitation/<string:utenteId>/exercises/", methods=["GET"])
def list_exercises(utenteId):
    """
    Lista todos os exercícios de reabilitação para um utente específico.

    """
    try:
        # token = request.headers.get('Authorization')
        # if not token or not token.startswith("Bearer "):
        #     return jsonify({"error": "Token ausente"}), 401

        # try:
        #     token = token.replace("Bearer ", "")
        #     decoded = decode_token(token)
        #     therapistId = decoded['user_id']
        # except jwt.ExpiredSignatureError:
        #     return jsonify({"error": "Token expirado"}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({"error": "Token inválido"}), 401

        therapistId = verifyAuth()
        if not is_objectid(therapistId):
            return jsonify({"error": "Falha na autenticação"}), 401

        health_user = utente_model.get_health_user_by_id(utenteId)
        if not health_user:
            return jsonify({"error": "Utente não encontrado"}), 404
        
        casa_viva_user = user_model.get_user_by_email(health_user['email'])

        if not casa_viva_user:
            return jsonify({"error": "Utente não corresponde ao utilizador da casa viva"}), 404

        exercises = exercise_model.getRehabilitationExercise(casa_viva_user['_id'])

        if exercises:
            for e in exercises:
                e["_id"] = str(e["_id"])
        
        return jsonify(exercises), 200

    except Exception as e:
        # print(e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@utente_bp.route("/rehabilitation/exercises/<string:exerciseId>", methods=["GET"])
def get_exercise_rehabilitation(exerciseId):
    """
    Obtém um exercício de reabilitação específico pelo seu ID.

    """
    try:
        # token = request.headers.get('Authorization')
        # if not token or not token.startswith("Bearer "):
        #     return jsonify({"error": "Token ausente"}), 401

        # try:
        #     token = token.replace("Bearer ", "")
        #     decoded = decode_token(token)
        #     therapistId = decoded['user_id']
        # except jwt.ExpiredSignatureError:
        #     return jsonify({"error": "Token expirado"}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({"error": "Token inválido"}), 401

        therapistId = verifyAuth()
        if not is_objectid(therapistId):
            return jsonify({"error": "Falha na autenticação"}), 401

        exercise = exercise_model.getRehabilitationExerciseById(exerciseId)

        if not exercise:
            return jsonify({"error": "Exercício não encontrado"}), 404
        
        exercise["_id"] = str(exercise["_id"])
        
        return jsonify(exercise), 200

    except Exception as e:
        # print(e)
        return jsonify({"success": False, "error": str(e)}), 500

@utente_bp.route("/rehabilitation/exercises/<string:exerciseId>", methods=["DELETE"])
def delete_exercise_rehabilitation(exerciseId):
    """
    Deleta um exercício de reabilitação específico pelo seu ID.

    """
    try:
        # token = request.headers.get('Authorization')
        # if not token or not token.startswith("Bearer "):
        #     return jsonify({"error": "Token ausente"}), 401

        # try:
        #     token = token.replace("Bearer ", "")
        #     decoded = decode_token(token)
        #     therapistId = decoded['user_id']
        # except jwt.ExpiredSignatureError:
        #     return jsonify({"error": "Token expirado"}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({"error": "Token inválido"}), 401

        therapistId = verifyAuth()
        if not is_objectid(therapistId):
            return jsonify({"error": "Falha na autenticação"}), 401

        exercise = exercise_model.deleteRehabilitationExercise(exerciseId)

        if not exercise:
            return jsonify({"error": "Exercício não encontrado"}), 404
        
        return jsonify({"message": "Exercício deletado com sucesso"}), 200

    except Exception as e:
        # print(e)
        return jsonify({"success": False, "error": str(e)}), 500


# # Rota para listar exercícios
# @app.route("/reabilitation/<string:utenteId>/exercises", methods=["GET"])
# def list_exercises():
#     try:
#         exercises = list(exercises_collection.find())
#         for e in exercises:
#             e["_id"] = str(e["_id"])
#         return jsonify(exercises), 200
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

