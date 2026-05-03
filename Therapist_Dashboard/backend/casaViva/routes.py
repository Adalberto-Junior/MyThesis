# Import necessary modules and packages
import base64
import os
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pymongo.cursor import Cursor
import bcrypt
import jwt
import datetime
from . import casaViva_bp
# from models import users as user_model
from models import therapist as therapist_model
from models import users as user_model
from models.creatDocument import *
from models import exercise as exercise_model
from models import recording as recording_model
from models import result as result_model


def convert_to_ObjectId(obj):
    """Converte string para ObjectId se aplicável."""
    try:
        if isinstance(obj, str):
            return ObjectId(obj)
        return obj
    except Exception as e:
        print(f"Erro ao converter {obj} para ObjectId: {e}")
        return None


#todo: add the Scheduling model
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


# @casaViva_bp.route("/upload-imagem", methods=["POST"])
# def upload_imagem():
#     """ Upload an image file to the server.
#     :return: JSON response with the path of the uploaded image.
#     """

#     # token = request.headers.get('Authorization')
#     # if not token or not token.startswith("Bearer "):
#     #     return jsonify({"error": "Token ausente"}), 401
    
#     # try:
#     #     token = token.replace("Bearer ", "")
#     #     decoded = decode_token(token)
#     #     userId = decoded['user_id']

#     # except jwt.ExpiredSignatureError:
#     #     return jsonify({"error": "Token expirado"}), 401
#     # except jwt.InvalidTokenError:
#     #     return jsonify({"error": "Token inválido"}), 401
    


#     data = request.get_json()
#     if not data or "file" not in data or "userName" not in data:
#         return jsonify({"error": "Dados inválidos ou em falta."}), 400
    
#     file = data.get("file")
#     userName = data.get("userName")
#     subpasta = data.get("subpasta", "outros")  # tipo 'articulation', 'prosody', etc.

#     if not file or not userName:
#         return jsonify({"error": "Ficheiro ou nome do utilizador em falta."}), 400

#     pasta_destino = os.path.join("static", "grafico", userName, subpasta)
#     os.makedirs(pasta_destino, exist_ok=True)

#     caminho_absoluto = os.path.join(pasta_destino, file.filename)
#     file.save(caminho_absoluto)

#     caminho_relativo = f"/static/grafico/{userName}/{subpasta}/{file.filename}"
#     return jsonify({"path": caminho_relativo}), 200

@casaViva_bp.route("/upload-imagem", methods=["POST"])
def upload_imagem():
    """ Upload an image file to the server.
    :return: JSON response with the path of the uploaded image.
    """
    file = request.files.get("file")
    userName = request.form.get("userName")
    subpasta = request.form.get("subpasta", "outros")  # Ex: articulation, prosody...

    if not file or not userName:
        return jsonify({"error": "Ficheiro ou nome do utilizador em falta."}), 400

    pasta_destino = os.path.join("static", "grafico", userName, subpasta)
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_absoluto = os.path.join(pasta_destino, file.filename)
    file.save(caminho_absoluto)

    caminho_relativo = f"/static/grafico/{userName}/{subpasta}/{file.filename}"
    return jsonify({"path": caminho_relativo}), 200


@casaViva_bp.route("/upload-audio", methods=["POST"])
def upload_audio():
    
    file = request.files.get("file")
    userName = request.form.get("userName")
    subpasta = request.form.get("subpasta", "outros")  #


    if not file or not userName:
        return jsonify({"error": "Ficheiro ou nome do utilizador em falta."}), 400
    
    pasta_destino = os.path.join("static", "audio", userName, subpasta)
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_absoluto = os.path.join(pasta_destino, file.filename)
    file.save(caminho_absoluto)

    caminho_relativo = f"/static/audio/{userName}/{subpasta}/{file.filename}"
    return jsonify({"path": caminho_relativo}), 200

@casaViva_bp.route("/upload-video", methods=["POST"])
def upload_video():
    data = request.get_json()
    if not data or "file" not in data or "userName" not in data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400
    
    file = data.get("file")
    userName = data.get("userName")
    subpasta = data.get("subpasta", "outros")

    if not file or not userName:
        return jsonify({"error": "Ficheiro ou nome do utilizador em falta."}), 400
    
    pasta_destino = os.path.join("static", "video", userName, subpasta)
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_absoluto = os.path.join(pasta_destino, file.filename)
    file.save(caminho_absoluto)

    caminho_relativo = f"/static/video/{userName}/{subpasta}/{file.filename}"
    return jsonify({"path": caminho_relativo}), 200


@casaViva_bp.route("/exercise", methods=["GET"])
def get_all_exercise():
    """
    Get the exercises in the database.
    :return: JSON response with the exercises.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    exercises = exercise_model.get_exercise_by_health_user(userId)

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


@casaViva_bp.route("/exercise/<exercise_id>", methods=["GET"])
def get_exercise_by_id(exercise_id):
    """
    Get an exercise by its ID.
    :param exercise_id: The ID of the exercise.
    :return: JSON response with the exercise data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    exercise = exercise_model.get_exercise_by_id(exercise_id)

    if not exercise:
        return jsonify({"error": "Exercício não encontrado"}), 404
    
    if exercise.get('exerciseId'):
        new_exercise = exercise_model.get_exercise_by_id(exercise['exerciseId'])
        if new_exercise:
            del new_exercise['_id']  # <- remove o campo _id do dict
            exercise.update(new_exercise) 
            del exercise['exerciseId']  

    
    return jsonify(exercise), 200

@casaViva_bp.route("/exercise/type/<exercise_type>", methods=["GET"])
def get_exercise_by_type(exercise_type):
    """
    Get exercises by their type.
    :param exercise_type: The type of the exercise.
    :return: JSON response with the exercises of that type.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    exercises = exercise_model.get_exercise_by_userId_and_type(userId, exercise_type)

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

@casaViva_bp.route("/exercise/processing/<processing_type>", methods=["GET"])
def get_exercise_by_processing_type(processing_type):
    """
    Get exercises by their processing type.
    :param processing_type: The processing type of the exercise.
    :return: JSON response with the exercises of that processing type.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    exercises = exercise_model.get_exercise_by_processingType_and_userId(processing_type, userId)

    # print(exercises)

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
    
    # print(exercises)
    
    return jsonify(exercises), 200


@casaViva_bp.route("/recording", methods=["POST"])
def create_recording():
    """
    Create a new recording.
    :return: JSON response with the created recording data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400
    
    name = data.get("name")
    time = data.get("time")
    path = data.get("path")
    exercise = data.get("exercise")
    exerciseStep = data.get("exerciseStep")
    user = data.get("user")
    
    if not name or not time or not path or not exercise or not exerciseStep or not user:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400

    documento = CreatDocumentToDB()
    recording_data = documento.recordingDocument(name, time, path, exercise, exerciseStep, user)

    # Save the recording to the database
    status = recording_model.create_recording(recording_data)

    if not status:
        return jsonify({"error": "Erro ao criar gravação."}), 500
    
    return jsonify({"message": "Gravação criada com sucesso.", "id": str(status)}), 201

@casaViva_bp.route("/recording/<recording_id>", methods=["GET"])
def get_recording_by_id(recording_id):
    """
    Get a recording by its ID.
    :param recording_id: The ID of the recording.
    :return: JSON response with the recording data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    recording = recording_model.get_recording_by_id(recording_id)

    if not recording:
        return jsonify({"error": "Gravação não encontrada"}), 404
    
    return jsonify(recording), 200

@casaViva_bp.route("/recording/user/<user_id>", methods=["GET"])
def get_recordings_by_user(user_id):
    """
    Get all recordings by user ID.
    :param user_id: The ID of the user.
    :return: JSON response with the recordings data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    recordings = recording_model.get_recordings_by_user(user_id)

    if not recordings:
        return jsonify({"error": "Gravações não encontradas"}), 404
    
    if isinstance(recordings, Cursor):
        recordings = list(recordings)
    
    return jsonify(recordings), 200

@casaViva_bp.route("/recording/<recording_id>", methods=["PUT"])
def update_recording(recording_id):
    """
    Update a recording by its ID.
    :param recording_id: The ID of the recording.
    :return: JSON response with the update status.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400

    success = recording_model.update_recording(recording_id, data)

    if not success:
        return jsonify({"error": "Falha ao atualizar gravação."}), 500
    
    return jsonify({"message": "Gravação atualizada com sucesso."}), 200

@casaViva_bp.route("/recording/<recording_id>", methods=["DELETE"])
def delete_recording(recording_id):
    """
    Delete a recording by its ID.
    :param recording_id: The ID of the recording.
    :return: JSON response with the delete status.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    success = recording_model.delete_recording(recording_id)

    if not success:
        return jsonify({"error": "Falha ao deletar gravação."}), 500
    
    return jsonify({"message": "Gravação deletada com sucesso."}), 200


@casaViva_bp.route("/result", methods=["POST"])
def create_result():
    """
    Create a new result.
    :return: JSON response with the ID of the created result.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400
    
    static_result = data.get("static_result")
    date = data.get("date")
    recording = data.get("recording")
    no_static_result = data.get("no_static_result")
    user = data.get("user")
    step = data.get("step")
    processing_type = data.get("processing_type")
    pathToChart = data.get("pathToChart")
    hour = data.get("hour")

    # Create a new result document
    result_data = CreatDocumentToDB().resultDocument(static_result=static_result, no_static_result=no_static_result, date=date, recording=recording, user=user, step=step, processing_type=processing_type, pathToChart=pathToChart,hour=hour)

    # Save the result to the database
    result_id = result_model.create_result(result_data)

    if not result_id:
        return jsonify({"error": "Erro ao criar resultado.", "id": None}), 500

    return jsonify({"message": "Resultado criado com sucesso.", "id": str(result_id)}), 201

@casaViva_bp.route("/result/<result_id>", methods=["GET"])
def get_result_by_id(result_id):
    """
    Get a result by its ID.
    :param result_id: The ID of the result.
    :return: JSON response with the result data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    result = result_model.get_result_by_id(result_id)

    if not result:
        return jsonify({"error": "Resultado não encontrado"}), 404
    
    return jsonify(result), 200

@casaViva_bp.route("/result/user/<user_id>", methods=["GET"])
def get_results_by_user(user_id):
    """
    Get all results by user ID.
    :param user_id: The ID of the user.
    :return: JSON response with the results data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    results = result_model.get_result_by_user(user_id)

    if not results:
        return jsonify({"error": "Resultados não encontrados"}), 404
    
    if isinstance(results, Cursor):
        results = list(results)
    
    return jsonify(results), 200

@casaViva_bp.route("/result", methods=["PUT"])
def update_result():
    """
    Update an existing result.
    :return: JSON response with the updated result data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    data = request.get_json()
    
    if not data or "result_id" not in data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400
    
    result_id = data.get("result_id")
    
    updated_result = result_model.update_result(result_id, data)

    if not updated_result:
        return jsonify({"error": "Falha ao atualizar resultado."}), 500
    
    return jsonify(updated_result), 200

@casaViva_bp.route("/result/<result_id>", methods=["DELETE"])
def delete_result(result_id):
    """
    Delete a result by its ID.
    :param result_id: The ID of the result to delete.
    :return: JSON response with the delete status.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    success = result_model.delete_result(result_id)

    if not success:
        return jsonify({"error": "Falha ao deletar resultado."}), 500
    
    return jsonify({"message": "Resultado deletado com sucesso."}), 200


@casaViva_bp.route("/report", methods=["GET"])
def get_report():
    """
    Get all report for the user.
    :return: JSON response with the report data.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    report_data = result_model.get_reported_results(userId)

    if not report_data:
        return jsonify({"error": "Nenhum resultado encontrado."}), 404
    
    if isinstance(report_data, Cursor):
        report_data = list(report_data)

    return jsonify(report_data), 200

@casaViva_bp.route("/report", methods=["PUT"])
def update_report_views():
    """
    Update the views of a reported result.
    :return: JSON response with the updated report data.
    """

    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401
    
    data = request.get_json()
   
    if not data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400
    
    if isinstance(data, (str, bytes, bytearray)):
        data = json.loads(data)
    elif not isinstance(data, dict):
        raise TypeError("Formato de dados inválido")

    updated_report = None
    
    for id_str, new_views in data.items():
        # report_id = ObjectId(id_str)
        updated_report = result_model.update_reported_views(id_str)

    if not updated_report:
        return jsonify({"error": "Falha ao atualizar visualização dos relatórios."}), 500

    return jsonify({"message": "Visualização dos relatórios atualizadas com sucesso."}), 200


@casaViva_bp.route("/pauseAnalysis", methods=["POST"])
def pause_analysis():
    """
    Pause the analysis of a recording.
    :return: JSON response with the status of the pause operation.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    data = request.get_json()
    # print(data)


    if 'user' in data:
        data['user'] = convert_to_ObjectId(data['user'])
    if 'exercise' in data:
        if 'state' in data and data['state'] == 'middle':
            data['exercise'] = convert_to_ObjectId(data['exercise'])
        else:
            for idx, exerId in enumerate(data['exercise']):
                data['exercise'][idx] = convert_to_ObjectId(exerId)
    
    if "audio" in data:
        for values in data["audio"].values():
            for audio_data in values:
                audio_data["id"] = (
                    convert_to_ObjectId(audio_data["id"])
                    if audio_data.get("id", "").strip()
                    else audio_data.get("id")
                )
    # print(data)
    
    # if not data or "recording_id" not in data:
    #     return jsonify({"error": "Dados inválidos ou em falta."}), 400
    if not data:
        return jsonify({"error": "Dados inválidos ou em falta."}), 400

    success = exercise_model.pause_analysis(data) #TODO: VER ISSO

    if not success:
        return jsonify({"error": "Falha ao pausar análise."}), 500

    return jsonify({"message": "Análise pausada com sucesso.","id": str(success)}), 200


@casaViva_bp.route("/statusAnalysis", methods=["GET"])
def get_status_analysis():
    """
    Get the status of the analysis for a user.
    :return: JSON response with the status of the analysis.
    """

    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    # print(userId)
    status = exercise_model.get_status_analysis(userId)

    if not status:
        return jsonify({"error": "Status de análise não encontrado."}), 404
    
    if isinstance(status, Cursor):
        status = list(status)
    
    return jsonify(status), 200


@casaViva_bp.route("/statusAnalysis", methods=["DELETE"])
def delete_status_analysis():
    """
    Delete the status of the analysis for a user.
    :return: JSON response with the status of the delete operation.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    success = exercise_model.delete_status_analysis(userId)

    if not success:
        return jsonify({"error": "Falha ao deletar status de análise."}), 500
    
    return jsonify({"message": "Status de análise deletado com sucesso."}), 200


@casaViva_bp.route("/rehabilitation/exercise", methods=["GET"])
def get_all_rehabilitation_exercise():
    """
    Get the rehabilitation exercises for a user.
    :return: JSON response with the rehabilitation exercises.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    try:
        token = token.replace("Bearer ", "")
        decoded = decode_token(token)
        userId = decoded['user_id']
        username = decoded['user_name']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    exercises = exercise_model.getRehabilitationExercise(userId)

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













