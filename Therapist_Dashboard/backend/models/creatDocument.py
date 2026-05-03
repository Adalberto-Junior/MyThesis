#============================================================================================
#============================================================================================
# Project:       Assistant to speech Therapy
# File:          creatDocument.py
# Created by:    Adalberto Jr
# Created date:  30/04/2025
# Version:       1.0
# Python:        3.10
# Local:         Universidade de Aveiro
# Description: This module is responsible for creating a document to send the database. 
#              This document is created in JSON format and is sent to the database.
# ===========================================================================================
#============================================================================================ 

import json
from bson.objectid import ObjectId
from pymongo import errors
class CreatDocumentToDB:

    def __init__(self):
        self.data = {}

    def ensure_objectid(self,value):
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(value)
        except errors.InvalidURI:
            return None  # ou raise ValueError("ID inválido")

    def userDocument(self, name, email, password,profession, date_of_birth):
        """
        Create a document for the user: therapist.
        :param name: The name of the user.
        :param email: The email of the user.
        :param password: The password of the user.
        :param profession: The profession of the user.
        :param date_of_birth: The date of birth of the user.
        :return: JSON string of the document.
        """
        # password must be hashed
        self.data.clear()
        self.data = {
                    "name": name,
                    "email": email,
                    "password": password,       # password must be hashed
                    "profession": profession,   # profession is the type of therapist: speech therapist, psychologist, etc
                    "date_of_birth": date_of_birth, # date_of_birth is the date of birth of the user
                }
        data = json.dumps(self.data)
        return self.data
    
    
    def curentUserDocument(self,userId, name, email,profession,):
        """
        Create a document for the user: therapist.
        :param name: The name of the user.
        :param email: The email of the user.
        :param profession: The profession of the user.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                     'userId': userId,
                    "name": name,
                    "email": email,
                    "profession": profession,   # profession is the type of therapist: speech therapist, psychologist, etc
                }
        data = json.dumps(self.data)
        return self.data

    def userCasaVivaDocument(self, name, age, email, password, therapist, email_therapist):
        self.data.clear()
        self.data = {
                    "name": name,
                    "age": age,
                    "email": email,
                    "password": password,       # password must be hashed
                    "therapist": therapist,
                    "email_therapist": email_therapist
                }
        # data = json.dumps(self.data)
        return self.data
    
    
    def schedulingDocument(self, title, date, time, local, description, guest, type, user):
        """
        Create a document for the scheduling.
        :param title: The title of the scheduling.
        :param date: The date of the scheduling.
        :param time: The time of the scheduling.
        :param local: The local of the scheduling.
        :param description: The description of the scheduling.
        :param guest: The guest of the scheduling.
        :param type: The type of the scheduling.
        :param user: The user of the scheduling.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "title": title,
                    "date": date,
                    "time": time,
                    "local": local,
                    "description": description,
                    "guest": guest,                 # guest is the name of the therapist or other guest
                    "type": type,                   # type is the type of therapy: remote or presential?
                    "user": self.ensure_objectid(user)                    # user is the id of the user
                }
        return self.data
    
    def exerciseDocument(self, type, name, description, steps, userName, user,typeOfProcessing,therapist):
        """
        Create a document for the exercise.
        :param type: The type of the exercise.
        :param name: The name of the exercise.
        :param description: The description of the exercise.
        :param typeOfProcessing: the type of processing of exercise.
        :param steps: The steps of the exercise.
        :param userName: The name of the user.
        :param user: The user id.
        :param therapist: The therapist id.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "type": type,                                    # type is the type of exercise: speech, reading, writing, etc
                    "name": name,
                    "description": description,
                    "typeOfProcessing":typeOfProcessing,
                    "steps": steps,                      # steps is a list of dictionaries
                    "userName": userName,                # userName is the name of the user
                    "user": self.ensure_objectid(user) if user else None,                       # user is the id of the user
                    "therapist": self.ensure_objectid(therapist),          # therapist is the id of the therapist
                }
        return self.data
    
    def exerciseDocumentWithExerciseId(self,exercise, userId, userName,therapist):
        """
        Create a document for the exercise with exercise ID.
        :param exercise: The exercise ID.
        :param userId: The user ID.
        :param userName: The user name.
        :param therapist: The therapist ID.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "exerciseId": self.ensure_objectid(exercise),
                    "userName": userName,
                    "user": self.ensure_objectid(userId),
                    "therapist": self.ensure_objectid(therapist),
                }
        return self.data

    def genericExerciseDocument(self, type, name, description, steps,typeOfProcessing,therapist):
        """
        Create a document for the exercise.
        :param type: The type of the exercise.
        :param name: The name of the exercise.
        :param description: The description of the exercise.
        :param typeOfProcessing: the type of processing of exercise.
        :param steps: The steps of the exercise.
        :param therapist: The therapist id.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "type": type,                                    # type is the type of exercise: speech, reading, writing, etc
                    "name": name,
                    "description": description,
                    "typeOfProcessing":typeOfProcessing,
                    "steps": steps,                      # steps is a list of dictionaries
                    "therapist": self.ensure_objectid(therapist),          # therapist is the id of the therapist
                }
        return self.data

    def noteDocument(self, note, priority, date, therapist, dataExecucao, category, done):
        """
        Create a document for the exercise.
        :param note: The note to keep.
        :param priority: The priority of the note.
        :param date: The date of create the note.
        :param therapist: the therapist Id.
        :param dataExecucao: The date of execution of the note.
        :param category: The category of the note.
        :param done: The status of the note (done or not).
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "note": note,                            
                    "priority": priority,
                    "date": date,
                    "therapist": self.ensure_objectid(therapist),
                    "dataExecucao": dataExecucao,
                    "category": category,
                    "done": done
                }
        return self.data

    def relatoryDocument(self, title, type_of_analysis,observations,recommendations,internal_note, status,analysis_date,created_at,utenteId,therapist,analysis,views = 0):
        """
        Create a document for the relatory.
        :param title: The title of the relatory.
        :param type_of_analysis: The type of analysis of the relatory.
        :param observations: The observations of the relatory.
        :param recommendations: The recommendations of the relatory.
        :param internal_note: The internal note of the relatory.
        :param status: The status of the relatory.
        :param analysis_date: The date of analysis of the relatory.
        :param created_at: The date of creation of the relatory.
        :param utenteId: The id of the user (utente).
        :param therapist: The id of the therapist.
        :param analysis: The comentary of the analysis of the relatory.
        :param views: The number of views of the relatory, default is 0.
        :type views: int
        :return: JSON string of the document.
        """

        self.data.clear()
        self.data = {
                    "title": title,
                    "type_of_analysis": type_of_analysis,
                    "observations": observations,
                    "recommendations": recommendations,
                    "internal_note": internal_note,
                    "status": status,
                    "analysis_date": analysis_date,
                    "created_at": created_at,
                    "utente_id": self.ensure_objectid(utenteId[0]) if isinstance(utenteId, tuple) else self.ensure_objectid(utenteId),  # utenteId is the id of the user (utente)
                    "therapist": self.ensure_objectid(therapist),
                    "analysis": analysis,  # analysis is the comentary of the analysis of the relatory
                    "views": views,  # views is the number of views of the relatory
                }
        return self.data

    #NOTE:APagar isso depois. Não é importante

    def stepSentence_WordDocument(self, step, description, word = None, sentence = None):
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
        self.data.clear()
        self.data = {
                    "step": step,                                    # step is a number
                    "description": description,                     # description is the step to be done
                    "title": title,                  
                    "text": text                    
            }
        return json.dumps(self.data)
    
    def stepSpeechDocument(self, step, description, question):
        self.data.clear()
        self.data = {
                    "step": step,                                    # step is a number
                    "description": description,                     # description is the step to be done    
                    "question": question,                           # question is the question to be answered                                   
            }
        return json.dumps(self.data)
    
    def stepDiadochokinesiaDocument(self, step, typeOfConsonant, syllables, description):
        self.data.clear()
        self.data = {
                    "step": step,                                    # step is a number
                    "typeOfConsonant": typeOfConsonant,             # typeOfConsonant is the type of consonant to be used
                    "syllables": syllables,                          # syllables is a list of dictionaries 
                    "description": description                # description is the step to be done         
            }
        return json.dumps(self.data)
    

    def healthUserDocument(self, name, email, date_of_birth, therapist,observation, medical_condition,health_user_number, cellphone, address):
        """
        Create a document for the health user.
        :param name: The name of the user.
        :param email: The email of the user.
        :param date_of_birth: The date of birth of the user.
        :param therapist: The therapist of the user.
        :param observation: The observation of the user.
        :param medical_condition: The medical condition of the user.
        :param health_user_number: The health user number of the user.
        :param cellphone: The cellphone of the health user.
        :param address: The address of the health user.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "name": name,
                    "email": email,
                    "date_of_birth": date_of_birth, # date_of_birth is the date of birth of the user
                    "therapist": self.ensure_objectid(therapist), 
                    "observation": observation,   
                    "medical_condition": medical_condition, # medical_condition is the medical condition of the user
                    "health_user_number": health_user_number, # health_user_number is the health user number of the user
                    "cellphone": cellphone, # health_user_cellphone is the cellphone of the health user
                    "address": address, # health_user_address is the address of the health user

                }
        # data = json.dumps(self.data)
        return self.data
    

    def sessionDocument(self, date, start, end, user):
        """
        Create a document for the session.
        :param date: The date of the session.
        :param start: The start time of the session.
        :param end: The end time of the session.
        :param user: The user of the session.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "date": date,
                    "start": start,
                    "end": end,
                    "user": self.ensure_objectid(user)            # user is the id of the user
                }
        
        return self.data
    
    def recordingDocument(self, name, time, path,exercise, exerciseStep, user):
        """
        Create a document for the recording.
        :param name: The name of the recording.
        :param time: The duration of the recording.
        :param path: The path to the recording file.
        :param exercise: The exercise associated with the recording.
        :param exerciseStep: The exercise step associated with the recording.
        :param user: The user who made the recording.
        :return: JSON string of the document.
        """

        self.data.clear()
        self.data = {
                    "name": name,               # name is the name of the Audio file
                    "path": path,
                    "time": time,
                    "exercise": self.ensure_objectid(exercise),         # exercise is the id of the exercise
                    "exerciseStep": exerciseStep, # exerciseStep is the id of the exercise step
                    "user": self.ensure_objectid(user),                 # user is the id of the user
                    }
        return self.data
    
    def resultDocument(self, static_result, no_static_result, date, recording,user,step,processing_type, pathToChart,hour):
        """
        Create a document for the result.
        :param static_result: The static result of the processing.
        :param no_static_result: The non-static result of the processing.
        :param date: The date the result was produced.
        :param hour: The hour the result was produced.
        :param recording: The recording associated with the result.
        :param user: The user who produced the result.
        :param step: The step of the processing.
        :param processing_type: The type of processing.
        :param pathToChart: The path to the chart.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
                    "static_result": static_result,               # result is a list of dictionaries
                    "no_static_result": no_static_result,               # result is a list of dictionaries
                    "date": date,                   # date is the date produced the result
                    "hour": hour,
                    "recording": self.ensure_objectid(recording),          # recording is the id of the recording
                    "user": self.ensure_objectid(user),                   # user is the id of the user
                    "step": step,
                    "processing_type": processing_type, # processing_type is the type of processing: articulation, phonology, etc
                    "pathToChart": pathToChart,
                    }
        return self.data
    
    def rehabilitationExerciseDocument (self, title, category, objective, description, duration, repetitions, difficulty, feedback, notes, steps, images, videos, audios, user, userName, therapist ):
        """
        Create a document for the rehabilitation exercise.
        :param title: The title of the exercise.
        :param category: The category of the exercise.
        :param objective: The objective of the exercise.
        :param description: The description of the exercise.
        :param duration: The duration of the exercise.
        :param repetitions: The number of repetitions for the exercise.
        :param difficulty: The difficulty level of the exercise.
        :param feedback: The feedback for the exercise.
        :param notes: The notes for the exercise.
        :param steps: The steps for the exercise.
        :param images: The images for the exercise.
        :param videos: The videos for the exercise.
        :param audios: The audios for the exercise.
        :param user: The user associated with the exercise.
        :param userName: The name of the user associated with the exercise.
        :param therapist: The therapist associated with the exercise.
        :return: JSON string of the document.
        """
        self.data.clear()
        self.data = {
            "title": title,
            "category": category,
            "objective": objective,
            "description": description,
            "duration": duration,
            "repetitions": repetitions,
            "difficulty": difficulty,
            "feedback": feedback,
            "notes": notes,
            "steps": steps,
            "images": images,
            "videos": videos,
            "audios": audios,
            "user": self.ensure_objectid(user),
            "userName": userName,
            "therapist": self.ensure_objectid(therapist)
        }
        return self.data
