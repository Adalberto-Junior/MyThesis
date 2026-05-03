

# # Import necessary modules and packages
from flask import current_app as app
from bson.objectid import ObjectId
from bson import json_util
import json
import sys
from datetime import datetime

sys.path.append("..")
from extensions import mongo

def create_session(data):
    """
    Create a new session in the database.
    :param data: JSON string containing session data.
    :return: The ID of the created session.
    """
    
    sessions = mongo.db.session
    result = sessions.insert_one(data)
    return str(result.inserted_id)

def get_session_by_id(session_id):
    """
    Get a session by its ID.
    :param session_id: The ID of the session.
    :return: The session data as a dictionary.
    """
    sessions = mongo.db.session
    session = sessions.find_one({"_id": ObjectId(session_id)})

    return session

def get_sessions_by_user(user_id):
    """
    Get all sessions by user ID.
    :param user_id: The ID of the user.
    :return: A cursor to the sessions data.
    """
    sessions = mongo.db.session
    return sessions.find({"user": ObjectId(user_id)})

def update_session(session_id, dataEnd):
    """
    Update a session by its ID.
    :param session_id: The ID of the session.
    :param data: The updated data for the session.
    :return: The result of the update operation.
    """
    
    sessions = mongo.db.session
    result = sessions.update_one({"_id": ObjectId(session_id)}, {"$set": {"end": dataEnd}})
    return result.modified_count > 0

def delete_session(session_id):
    """
    Delete a session by its ID.
    :param session_id: The ID of the session.
    :return: The result of the delete operation.
    """
    
    sessions = mongo.db.session
    result = sessions.delete_one({"_id": ObjectId(session_id)})
    return result.deleted_count > 0

def get_sessions_by_date(date):
    """
    Get all sessions for a specific date.
    :param date: The date to filter sessions by.
    :return: A cursor to the sessions data.
    """
    
    sessions = mongo.db.session
    return sessions.find({"start": {"$gte": datetime.strptime(date, "%Y-%m-%d")}})