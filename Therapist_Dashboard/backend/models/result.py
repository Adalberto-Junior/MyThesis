

# # Import necessary modules and packages
from flask import current_app as app
from bson.objectid import ObjectId
from bson import json_util
import json
import sys
from datetime import datetime

sys.path.append("..")
from extensions import mongo


def normalize_object_id(value):
    """
    Aceita:
    - ObjectId
    - string '6866...'
    - string "{'$oid': '6866...'}"
    - dict {'$oid': '6866...'}
    """
    if isinstance(value, ObjectId):
        return value

    if isinstance(value, dict) and "$oid" in value:
        return ObjectId(value["$oid"])

    if isinstance(value, str):
        # Caso: "{'$oid': '6866...'}"
        if value.startswith("{") and "$oid" in value:
            try:
                value = value.replace("'", '"')
                parsed = json.loads(value)
                return ObjectId(parsed["$oid"])
            except Exception:
                pass

        return ObjectId(value)

    raise ValueError(f"Formato de ObjectId inválido: {value}")



def create_result(data):
    """
    Create a new result in the database.
    :param data: JSON string containing result data.
    :return: The ID of the created result.
    """
    
    # Convert JSON string to dictionary
    #data = json.loads(data)
    results = mongo.db.results
    result = results.insert_one(data)
    return str(result.inserted_id)

def get_result_by_id(result_id):
    """
    Get a result by its ID.
    :param result_id: The ID of the result.
    :return: The result data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.results.find_one({"_id": ObjectId(result_id)})

def get_result_by_user(user_id):
    """
    Get all results for a specific user.
    :param user_id: The ID of the user.
    :return: A cursor to the results.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.results.find({"user": ObjectId(user_id)})

def get_result_by_typeOfProcessing(type_of_processing):
    """
    Get all results for a specific type of processing.
    :param type_of_processing: The type of processing.
    :return: A cursor to the results.
    """
    return mongo.db.results.find({"processing_type": type_of_processing})

def get_result_by_recording(recording_id):
    """
    Get all results for a specific recording.
    :param recording_id: The ID of the recording.
    :return: A cursor to the results.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.results.find({"recording": ObjectId(recording_id)})

def update_result(result_id, data):
    """
    Update an existing result.
    :param result_id: The ID of the result to update.
    :param data: The new data for the result.
    :return: The updated result data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    results = mongo.db.results
    results.update_one({"_id": ObjectId(result_id)}, {"$set": data})
    return results.find_one({"_id": ObjectId(result_id)})

def delete_result(result_id):
    """
    Delete a result by its ID.
    :param result_id: The ID of the result to delete.
    :return: The deleted result data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    results = mongo.db.results
    result = results.find_one({"_id": ObjectId(result_id)})
    results.delete_one({"_id": ObjectId(result_id)})
    return result


def get_reported_results(utente_id):
    """
    Get all reported results.
    :param utente_id: The ID of the user.
    :return: A cursor to the reported results.
    """
    return mongo.db.health_user_relatory.find({"utente_id": ObjectId(utente_id), "status": "finalizado"})


def update_reported_views(report_id):
    """
    Update the views of a reported result.
    :param report_id: The ID of the report.
    :return: The updated report data as a dictionary.
    """

    results = mongo.db.health_user_relatory
    results.update_one(
        {"_id": normalize_object_id(report_id)},
        {"$inc": {"views": 1}}
    )
    return results.find_one({"_id": normalize_object_id(report_id)})


