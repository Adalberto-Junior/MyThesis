
"""
Classe para representar uma mensagem com informações sobre a origem, comando, destino e dados associados.

"""
import json

class Message:
    message = ""
    command = ""
    destination = ""
    source = ""
    data = {}
    dataOut = {}

    def __init__(self,source, message, command, destination, new_values=None):
        self.source = source
        self.message = message
        self.command = command
        self.new_values = new_values
        self.destination = destination
        self.data = {"source": source, "message": message, "command": command, "new_values": new_values} 
        self.dataOut = {"data": json.dumps(self.data), "destination": destination}
    
    def get_message(self):
        return json.dumps(self.dataOut)

    def print_data(self):
        print("Data: ",self.dataOut)
        
    def __str__(self):
        return self.message