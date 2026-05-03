#==============================================================================================================
# Autor      : Adalberto Jr
# Date       : 30/04/2025
# Local      : UA, Aveiro
# Version    : 1.0
# Description: This module is responsible for managing the database connection and executing queries.
#==============================================================================================================

import pymongo
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import sys
import json

class Database:

    def __init__(self, host, port, database):
        self.host = host #localhost
        self.port = port #27017
        self.database = database #
        self.client = MongoClient(host, port) #Conecta ao servidor MongoDB
        self.db = self.client[database]       #Conecta ao banco de dados
    
    def insert_one(self, collection, document):
        try:
            status = self.db[collection].insert_one(document)
            print("_____________________________________")
            print(status)
            print("_____________________________________")
            print(f"Document {document} inserted successfully.")
            return "Documento inserido com sucesso na base de dados",document['_id']
        except Exception as e:
            print(f"Error inserting document: {e}")
            return "Erro ao inserir o docuemnto na base de dados!"

    def insert_many(self, collection, documents):
        try:
            self.db[collection].insert_many(documents)
            print(f"All documents inserted successfully.")
            return "Todos os dados inseridos com sucesso na base de dados"
        except Exception as e:
            print(f"Error inserting documents: {e}")
            return "Erro ao inserir os docuemntos na base de dados!"
    
    def find_one(self, collection, query):
        try:
            result = self.db[collection].find_one(query)
            return result
        except Exception as e:
            print(f"Error finding document: {e}")
            return None
    
    def find_all(self, collection, query):
        try:
            result = self.db[collection].find(query)
            return result
        except Exception as e:
            print(f"Error finding documents: {e}")
            return None
        
    def update_one(self, collection, query, new_values):
        try:
            self.db[collection].update_one(query, new_values)
            print(f"Document updated successfully.")
            return "Documento atualizado com sucesso na base de dados!"
        except Exception as e:
            print(f"Error updating document: {e}")
            return "Erro ao atualizar o docuemnto na base de dados!"
    
    def update_one_v2(self, collection, query, new_values):
        try:
            print(f"Query: {query} and new_values: {new_values}")
            result = self.db[collection].update_one({"$and": query}, {"$set": new_values})
            print("Documentos correspondentes:", result.matched_count)
            print("Documentos modificados:", result.modified_count)

            return "Documento atualizado com sucesso na base de dados!"
        except Exception as e:
            print(f"Error updating document: {e}")
            return "Erro ao atualizar o docuemnto na base de dados!"
    
    def update_all(self, collection, query, new_values):
        try:
            self.db[collection].update_many(query, new_values)
            print(f"All documents updated successfully.")
            return "Lista dos docuemntos atualizados com sucesso na base de dados!"
        except Exception as e:
            print(f"Error updating documents: {e}")
            return "Erro ao atualizar a lista dos docuemntos na base de dados!"
    
    def update_all_v2(self, collection, query, new_values):
        try:
            self.db[collection].update_many({"$and": query}, {"$set": new_values})
            print(f"Document updated successfully.")
            return "Lista dos docuemntos atualizados com sucesso na base de dados!"
        except Exception as e:
            print(f"Error updating document: {e}")
            return "Erro ao atualizar a lista dos docuemntos na base de dados!"
    
    def delete_one(self, collection, query):
        try:
            self.db[collection].delete_one(query)
            print(f"Document deleted successfully.")
            return "Dados eliminados com sucesso na base de dados!"
        except Exception as e:
            print(f"Error deleting document: {e}")
            return "Erro ao eliminar os dados na base de dados!"

    def delete_all(self, collection, query):
        try:
            self.db[collection].delete_many(query)
            print(f"All documents deleted successfully.")
            return "Lista dos dados eliminados com sucesso na base de dados!"
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return "Erro ao eliminar a lista dos dados na base de dados!"
    
    def close_connection(self):
        self.client.close()
        print("Connection closed.")
    
    def __str__(self):
        return f"Database connection: {self.host}:{self.port}/{self.database}"