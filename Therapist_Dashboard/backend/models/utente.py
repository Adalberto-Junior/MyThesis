#===========================================================================================
# File: utente.py
# Created by: Adalberto Jr
# Created date: 30/04/2025
# Version: 1.0
# Python: 3.10
# Local: Universidade de Aveiro
# Description: This module is responsible for managing the user data and the user results.
#              It includes functions to create, update, delete and get user data and results.
#===========================================================================================
#
# Import necessary modules and packages
import json
import sys
from flask import current_app as app
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime

from extensions import mongo

def create_health_user(data):
    """
    Create a new health user in the database.
    :param data: JSON string containing user data.
    :return: The ID of the created user.
    """
    #data = json.loads(data)
    # mongo = app.extensions['pymongo']
    utente = mongo.db.health_user
    result = utente.insert_one(data)
    return str(result.inserted_id)

def get_health_user_by_id(user_id):
    """
    Get a health user by their ID.
    :param user_id: The ID of the user.
    :return: The user data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find_one({"_id": ObjectId(user_id)})

def get_health_user_by_email(email):
    """
    Get a health user by their email.
    :param email: The email of the user.
    :return: The user data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find_one({"email": email})

def get_health_user_by_username(username):
    """
    Get a health user by their username.
    :param username: The username of the user.
    :return: The user data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find_one({"username": username})

def update_health_user(user_id, data):
    """
    Update a health user's data.
    :param user_id: The ID of the user.
    :param data: Dictionary containing the updated user data.
    :return: True if the update was successful, False otherwise.
    """
    # mongo = app.extensions['pymongo']
    result = mongo.db.health_user.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return result.modified_count > 0

def delete_health_user(user_id):
    """
    Delete a health user from the database.
    :param user_id: The ID of the user.
    :return: True if the deletion was successful, False otherwise.
    """
    # mongo = app.extensions['pymongo']
    result = mongo.db.health_user.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

def delete_health_user_by_email(email):
    """
    Delete a health user by their email.
    :param email: The email of the user.
    :return: True if the deletion was successful, False otherwise.
    """
    # mongo = app.extensions['pymongo']
    result = mongo.db.health_user.delete_one({"email": email})
    return result.deleted_count > 0


def get_all_health_users_by_therapist(therapist_id):
    """
    Get all health users associated with a specific therapist.
    :param therapist_id: The ID of the therapist.
    :return: A list of user data as dictionaries.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find({"therapist": ObjectId(therapist_id)})

def get_health_user_by_email_and_therapist(email, therapist_id):
    """
    Get a health user by their email and associated therapist.
    :param email: The email of the user.
    :param therapist_id: The ID of the therapist.
    :return: The user data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find_one({"email": email, "therapist": ObjectId(therapist_id)})

def get_health_user_by_username_and_therapist(username, therapist_id):
    """
    Get a health user by their username and associated therapist.
    :param username: The username of the user.
    :param therapist_id: The ID of the therapist.
    :return: The user data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find_one({"username": username, "therapist": ObjectId(therapist_id)})

def get_health_user_by_email_and_username_and_therapist(email, username, therapist_id):
    """
    Get a health user by their email, username, and associated therapist.
    :param email: The email of the user.
    :param username: The username of the user.
    :param therapist_id: The ID of the therapist.
    :return: The user data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user.find_one({"email": email, "username": username, "therapist": ObjectId(therapist_id)})


################Relatory

def create_health_user_relatory(data):
    """
    Create a new health user relatory in the database.
    :param data: JSON string containing relatory data.
    :return: The ID of the created relatory.
    """
    #data = json.loads(data)
    # mongo = app.extensions['pymongo']
    relatory = mongo.db.health_user_relatory
    result = relatory.insert_one(data)
    return str(result.inserted_id)

def get_health_user_relatory_by_id(relatory_id):
    """
    Get a health user relatory by its ID.
    :param relatory_id: The ID of the relatory.
    :return: The relatory data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user_relatory.find_one({"_id": ObjectId(relatory_id)})

def get_health_user_relatory_by_user_id(user_id):
    """
    Get all relatories for a specific health user.
    :param user_id: The ID of the health user.
    :return: A list of relatory data as dictionaries.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user_relatory.find({"utente_id": ObjectId(user_id) if isinstance(user_id, str) else user_id})

def get_health_user_relatory_by_user_id_and_date(user_id, date):
    """
    Get a health user relatory by user ID and date.
    :param user_id: The ID of the health user.
    :param date: The date of the relatory.
    :return: The relatory data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user_relatory.find_one({"utente_id": ObjectId(user_id), "date": date})

def update_health_user_relatory(relatory_id, data):
    """
    Update a health user relatory.
    :param relatory_id: The ID of the relatory.
    :param data: Dictionary containing the updated relatory data.
    :return: True if the update was successful, False otherwise.
    """
    # mongo = app.extensions['pymongo']
    result = mongo.db.health_user_relatory.update_one({"_id": ObjectId(relatory_id)}, {"$set": data})
    return result.modified_count > 0

def delete_health_user_relatory(relatory_id):
    """
    Delete a health user relatory from the database.
    :param relatory_id: The ID of the relatory.
    :return: True if the deletion was successful, False otherwise.
    """
    # mongo = app.extensions['pymongo']
    result = mongo.db.health_user_relatory.delete_one({"_id": ObjectId(relatory_id)})
    return result.deleted_count > 0

def get_all_health_user_relatories_by_therapist(therapist_id):
    """
    Get all health user relatories associated with a specific therapist.
    :param therapist_id: The ID of the therapist.
    :return: A list of relatory data as dictionaries.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user_relatory.find({"therapist": ObjectId(therapist_id)})

def get_health_user_relatory_by_user_id_and_therapist(user_id, therapist_id):
    """
    Get a health user relatory by user ID and associated therapist.
    :param user_id: The ID of the health user.
    :param therapist_id: The ID of the therapist.
    :return: The relatory data as a dictionary.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.health_user_relatory.find_one({"utente_id": ObjectId(user_id), "therapist": ObjectId(therapist_id)})

