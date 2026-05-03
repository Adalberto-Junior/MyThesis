# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted

import json


def write_log(text):
    with open("log.txt", "a") as log:
        log.write(text)

class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        write_log("Actions: " + "No_understand: " + "enter\n")
        
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        if tracker.latest_message["intent"].get("confidence") > 0.5:
            dispatcher.utter_message(response="utter_default")
        
        #publish.single(topic="comandos/voz/UI", payload=json.dumps({"comando": "no_understand"}), hostname="localhost")
        
        write_log("Actions: " + "No_understand: " + "exit\n")
        
        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]

class SwitchLightsAction(Action):
    def name(self) -> Text:
        return "action_switch_lights"
   
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        print(tracker.get_slot("switch") + "--" + tracker.get_slot("place"))   
        #tracker.lastest_message["entities"]  [0] - entity - value
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))          
        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")
            return [UserUtteranceReverted()]
        """
        switcher = homecontrol.SwitchLights(lightsimulator)
        message = switcher.switchlight(tracker.get_slot("switch"), tracker.get_slot("place"))
        dispatcher.utter_message(message)
        return [SlotSet("place", None), SlotSet("switch", None)]
         """

class ActionAfirmar(Action):
    
    def name(self) -> Text:
        return "action_afirmar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Afirmar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        msg = {"comando": "confirmar"}
    #    publish.single(topic="comandos/voz/UI", payload=json.dumps(msg), hostname="localhost")
        
        write_log("Actions: " + "Afirmar: " + "exit\n")
        
        return []

class ActionNegar(Action):
    
    def name(self) -> Text:
        return "action_negar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Negar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        msg = {"comando": "negar"}
        #publish.single(topic="comandos/voz/UI", payload=json.dumps(msg), hostname="localhost")
        
        write_log("Actions: " + "Negar: " + "exit\n")
        
        return []

class ActionReadExercise (Action):
    def name(self) -> Text:
        return "action_ler_exercicio"
    
    def __init__(self):
        self.exercicios = self.carregar_exercicios()

    def carregar_exercicios(self):
        """
        Lê o ficheiro de exercícios e retorna um dicionário.
        """
        caminho_ficheiro = "..\ficheiro\exercicio.txt"
        exercicios = {}
        
        # Verifica se o ficheiro existe
        if os.path.exists(caminho_ficheiro):
            with open(caminho_ficheiro, "r", encoding="utf-8") as f:
                for linha in f:
                    identificador, texto = linha.strip().split("|")
                    exercicios[identificador] = texto
        else:
            raise FileNotFoundError(f"Ficheiro '{caminho_ficheiro}' não encontrado!")
        
        return exercicios
   
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Ler exercicios: " + "exit\n")  
         # Obter o identificador do exercício atual do slot
        exercicio_id = tracker.get_slot("exercicio")
        
        print(exercicio_id)   
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))          
       
        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")
            
        else:
             if exercicio_id and exercicio_id in self.exercicios:
                texto_exercicio = self.exercicios[exercicio_id]
                dispatcher.utter_message(text=texto_exercicio)
             else:
                dispatcher.utter_message(text="Não consegui encontrar o exercício solicitado.")
                return [UserUtteranceReverted()]
             
        write_log("Actions: " + "Ler exercicios: " + "exit\n")  
        return []
    
class ActionStartDiagnostic (Action):
    def name(self) -> Text:
        return "action_start_diagnostics"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        write_log("Actions: " + "Começar o diagnostico: " + "exit\n")    
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))          
       
        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")
            return [UserUtteranceReverted()]

        dispatcher.utter_message(response="utter_start_diagnostics")  
        write_log("Actions: " + "Começar o diagnostico: " + "exit\n")    

        return []

class ActionPauseDiagnostic (Action):
    def name(self) -> Text:
        return "action_pause_diagnostics"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        write_log("Actions: " + "Pausar o diagnostico: " + "exit\n")    
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))          
       
        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")
            return [UserUtteranceReverted()]

        dispatcher.utter_message(response="utter_continue_later:")  
        write_log("Actions: " + "Pausar o diagnostico: " + "exit\n")    

        return []


class ActionChangeName(Action):

    def name(self) -> Text:
        return "action_change_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("username", None)]
    