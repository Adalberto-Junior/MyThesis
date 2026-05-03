#============================================================================================
#============================================================================================
# Project:       Assistant to speech Therapy
# File:          CreatDocumentToDB.py
# Created by:    Adalberto Jr
# Created date:  24/03/2025
# Version:       1.0
# Python:        3.10
# Local:         Universidade de Aveiro
# Description: This module is responsible for creating a document to send the database. 
#              This document is created in JSON format and is sent to the database.
# ===========================================================================================
#============================================================================================ 

import json

##==========================================================================================
# Class to create document to send to the database
##==========================================================================================

class CreatDocumentToDB:

    def __init__(self):
        self.data = {}


    def userDocument(self, name, age, email, password,therapist, email_therapist):
        """ Create a document to send to the database for a new user """

        self.data.clear()
        self.data = {
                    "name": name,
                    "age": age,
                    "email": email,
                    "password": password,       # password must be hashed
                    "therapist": therapist,
                    "email_therapist": email_therapist
                }
        data = json.dumps(self.data)
        return data
    
    def curentUserDocument(self,userId, name, age, email,therapist, email_therapist):
        """ Create a document to send to all clients for an existing user """

        self.data.clear()
        self.data = {
                     'userId': userId,
                    "name": name,
                    "age": age,
                    "email": email,
                    "therapist": therapist,
                    "email_therapist": email_therapist
                }
        data = json.dumps(self.data)
        return data
    
    def sessionDocument(self, date, start, end, user):
        """ Create a document to send to the database for a new session """
        self.data.clear()
        self.data = {
                    "date": date,
                    "start": start,
                    "end": end,
                    "user": user            # user is the id of the user
                }
        return json.dumps(self.data)
    
    def schedulingDocument(self, title, date, time, local, description, guest, type, user):
        """ Create a document to send to the database for a new scheduling """

        self.data.clear()
        self.data = {
                    "title": title,
                    "date": date,
                    "time": time,
                    "local": local,
                    "description": description,
                    "guest": guest,                 # guest is the name of the therapist or other guest
                    "type": type,                   # type is the type of therapy: remote or presential?
                    "user": user                    # user is the id of the user
                }
        return json.dumps(self.data)
    
    def exerciseDocument(self, type, name, description, steps, userName, user):
        """ Create a document to send to the database for a new exercise """

        self.data.clear()
        self.data = {
                    "type": type,                                    # type is the type of exercise: speech, reading, writing, etc
                    "name": name,
                    "description": description,
                    "steps": steps,                      # steps is a list of dictionaries
                    "userName": userName,                # userName is the name of the user
                    'user': user,
                }
        return json.dumps(self.data)
    
    def stepSentence_WordDocument(self, step, description, word = None, sentence = None):
        """ Create a document to send to the database for a new step with a word or sentence """

        self.data.clear()
        if word:
            self.data = {
                    "step": step,                                    # step is a number
                    "description": description,                     # description is the step to be done
                    "word": word                                    # can be a word, a sentence or a paragraph
                }
        elif sentence:
            self.data = {
                    "step": step,                                    # step is a number
                    "description": description,                      # description is the step to be done
                    "sentence": sentence                             # can be a word, a sentence or a paragraph
                }
        return json.dumps(self.data)
    
    
    def stepReadingDocument(self, step, description, title, text):
        """ Create a document to send to the database for a new step with a reading """

        self.data.clear()
        self.data = {
                    "step": step,                                    # step is a number
                    "description": description,                     # description is the step to be done
                    "title": title,                  
                    "text": text                    
            }
        return json.dumps(self.data)
    
    def stepSpeechDocument(self, step, description, question):
        """ Create a document to send to the database for a new step with a speech """
        self.data.clear()
        self.data = {
                    "step": step,                                    # step is a number
                    "description": description,                     # description is the step to be done    
                    "question": question,                           # question is the question to be answered                                   
            }
        return json.dumps(self.data)
    
    def stepDiadochokinesiaDocument(self, step, typeOfConsonant, syllables, description):
        """ Create a document to send to the database for a new step with diadochokinesia """
        self.data.clear()
        self.data = {
                    "step": step,                                    # step is a number
                    "typeOfConsonant": typeOfConsonant,             # typeOfConsonant is the type of consonant to be used
                    "syllables": syllables,                          # syllables is a list of dictionaries 
                    "description": description                # description is the step to be done         
            }
        return json.dumps(self.data)
    
    def recordingDocument(self, name, time, path,exercise, exerciseStep, user,userName):
        """ Create a document to send to the database for a new recording """
        self.data.clear()
        self.data = {
                    "name": name,               # name is the name of the Audio file
                    "path": path,
                    "time": time,
                    "exercise": exercise,         # exercise is the id of the exercise
                    "exerciseStep": exerciseStep, # exerciseStep is the id of the exercise step
                    "user": user,                 # user is the id of the user
                    "userName": userName
                    }
        return json.dumps(self.data)
    
    def resultDocument(self, static_result, no_static_result, date, recording,user,step,processing_type, pathToChart,hour):
        """ Create a document to send to the database for a new result """

        self.data.clear()
        self.data = {
                    "static_result": static_result,               # result is a list of dictionaries
                    "no_static_result": no_static_result,               # result is a list of dictionaries
                    "date": date,                   # date is the date produced the result
                    "hour": hour,
                    "recording": recording,          # recording is the id of the recording
                    "user": user,                   # user is the id of the user
                    "step": step,
                    "processing_type": processing_type, # processing_type is the type of processing: articulation, phonology, etc
                    "pathToChart": pathToChart,
                    }
        return json.dumps(self.data)
    
    def resultFildDocument(self,key, value, unit):
        """ Create a document to send to the database for a new result field """
        self.data.clear()
        self.data = {
                     key: value,                   # key is the name of the field
                    "unidade": unit                # unit is the unit of the value (Hz, dB, etc)
                    }
        return json.dumps(self.data)
    