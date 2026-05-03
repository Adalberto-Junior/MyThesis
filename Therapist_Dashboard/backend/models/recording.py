


# # Import necessary modules and packages
from flask import current_app as app
from bson.objectid import ObjectId
from bson import json_util
import json
import sys
from datetime import datetime

sys.path.append("..")
from extensions import mongo


def create_recording(data):
    """
    Create a new recording in the database.
    :param data: JSON string containing recording data.
    :return: The ID of the created recording.
    """

    recordings = mongo.db.recording
    result = recordings.insert_one(data)
    return str(result.inserted_id)

def get_recording_by_id(recording_id):
    """
    Get a recording by its ID.
    :param recording_id: The ID of the recording.
    :return: The recording data as a dictionary.
    """
    recordings = mongo.db.recording
    recording = recordings.find_one({"_id": ObjectId(recording_id)})

    return recording

def get_recordings_by_user(user_id):
    """
    Get all recordings by user ID.
    :param user_id: The ID of the user.
    :return: A cursor to the recordings data.
    """
    recordings = mongo.db.recording
    return recordings.find({"user": ObjectId(user_id)})

def update_recording(recording_id, data):
    """
    Update a recording by its ID.
    :param recording_id: The ID of the recording.
    :param data: The updated data for the recording.
    :return: The result of the update operation.
    """
    recordings = mongo.db.recording
    result = recordings.update_one({"_id": ObjectId(recording_id)}, {"$set": data})
    return result.modified_count > 0

def delete_recording(recording_id):
    """
    Delete a recording by its ID.
    :param recording_id: The ID of the recording.
    :return: The result of the delete operation.
    """
    recordings = mongo.db.recording
    result = recordings.delete_one({"_id": ObjectId(recording_id)})
    return result.deleted_count > 0


