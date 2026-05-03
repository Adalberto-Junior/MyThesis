#=========================================================================
# File: users.py
# Created by: Adalberto Jr
# Created date: 30/04/2025
# Version: 1.0
# Python: 3.10
# Local: Universidade de Aveiro
# Description: This module contains functions to interact with the user collection in MongoDB.
#              It includes functions to create, update, delete and retrieve user data.
#              The module uses Flask and PyMongo for database operations.
#=========================================================================


# # Import necessary modules and packages
import json
import sys
from flask import current_app as app
from bson.objectid import ObjectId
from bson import json_util

sys.path.append("..")
from extensions import mongo

def create_user(data):
    """
    Create a new user in the database.
    :param data: JSON string containing user data.
    :return: The ID of the created user.
    """

    # mongo = app.extensions['pymongo']
    users = mongo.db.user
    # users = mongo.db.therapist
    result = users.insert_one(data)
    return str(result.inserted_id)

def get_user_by_email(email):
    """
    Get a user by their email address.
    :param email: The email address of the user.
    :return: The user data as a dictionary.
    """

    # mongo = app.extensions['pymongo']
    return mongo.db.user.find_one({"email": email})

def get_user_by_id(user_id):
    """
    Get a user by their ID.
    :param user_id: The ID of the user.
    :return: The user data as a dictionary.
    """

    # mongo = app.extensions['pymongo']
    return mongo.db.user.find_one({"_id": ObjectId(user_id)})

def get_user_by_username(username):
    """
    Get a user by their username.
    :param username: The username of the user.
    :return: The user data as a dictionary.
    """

    # mongo = app.extensions['pymongo']
    return mongo.db.user.find_one({"username": username})

def updateUser(user_id, data):
    """
    Update a user by their ID.
    :param user_id: The ID of the user.
    :param data: The data to update the user with.
    :return: True if the update was successful, False otherwise.
    """

    # mongo = app.extensions['pymongo']
    result = mongo.db.user.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return result.modified_count > 0

def updateUserByEmail(email, data):
    """
    Update a user by their email address.
    :param email: The email address of the user.
    :param data: The data to update the user with.
    :return: True if the update was successful, False otherwise.
    """

    # mongo = app.extensions['pymongo']
    result = mongo.db.user.update_one({"email": email}, {"$set": data})
    return result.modified_count > 0

def deleteUser(user_id):
    """
    Delete a user by their ID.
    :param user_id: The ID of the user.
    :return: True if the deletion was successful, False otherwise.
    """

    # mongo = app.extensions['pymongo']
    result = mongo.db.user.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

def deleteUserByEmail(email):
    """
    Delete a user by their email address.
    :param email: The email address of the user.
    :return: True if the deletion was successful, False otherwise.
    """

    # mongo = app.extensions['pymongo']
    result = mongo.db.user.delete_one({"email": email})
    return result.deleted_count > 0

def get_all_users():
    """
    Get all users from the database.
    :return: A cursor to the user data.
    """
    # mongo = app.extensions['pymongo']
    return mongo.db.user.find()

def get_all_users_json():
    """
    Get all users from the database and convert to JSON.
    :return: A JSON string containing all user data.
    """
    # Get all users from the database
    # mongo = app.extensions['pymongo']
    users = mongo.db.user.find()
    return json.loads(json_util.dumps(users))

def get_userId(email):
    """
    Get the user ID by email address.
    :param email: The email address of the user.
    :return: The user ID as a string, or None if not found.
    """
    
    # mongo = app.extensions['pymongo']
    user = mongo.db.user.find_one({"email": email})
    if user:
        return str(user['_id'])
    else:
        return None