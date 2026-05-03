import xml.etree.ElementTree as ET
import requests

# Registrar namespaces corretamente
ET.register_namespace("mmi", "http://www.w3.org/2008/04/mmi-arch")
ET.register_namespace("emma", "http://www.w3.org/2003/04/emma")

# Classe para representar o EMMA
class EMMA:
    def __init__(self, id, medium, mode, confidence, start, end=None):
        self.namespaceEMMA = "http://www.w3.org/2003/04/emma"
        self.id = id
        self.medium = medium
        self.mode = mode
        self.confidence = confidence
        self.start = start
        self.end = end
        self.value = ""
    
    def setValues(self, value):
        self.value = value
        return self
    
    def getElem(self):
        emma_elem = ET.Element("{http://www.w3.org/2003/04/emma}emma", version="1.0")
        interpretation = ET.SubElement(emma_elem, "{http://www.w3.org/2003/04/emma}interpretation", {
            "id": self.id,
            "medium": self.medium,
            "mode": self.mode,
            "start": str(self.start),
            "confidence": str(self.confidence)
        })

        if self.end is not None:
            interpretation.set("end", str(self.end))
        
        command = ET.SubElement(interpretation, "command")
        command.text = self.value  # Removemos aspas extras
        
        return emma_elem

# Classe para representar o Lifecycle
class Lifecycle:
    def __init__(self, source, target, requestId, contextId=None):
        self.namespaceMMI = "http://www.w3.org/2008/04/mmi-arch"
        self.source = source
        self.target = target
        self.requestId = requestId
        self.contextId = contextId
    
    def _create_base_mmi(self):
        mmi_elem = ET.Element("{http://www.w3.org/2008/04/mmi-arch}mmi", {
            "xmlns:mmi": "http://www.w3.org/2008/04/mmi-arch",
            "xmlns:emma": "http://www.w3.org/2003/04/emma",
            "mmi:version": "1.0"
        })
        return mmi_elem

    def _set_base_params(self, elem):
        elem.set("source", self.source)
        elem.set("target", self.target)
        elem.set("requestId", self.requestId)
        if self.contextId:
            elem.set("context", self.contextId)
    
    def do_start_request(self, emma):
        mmi_elem = self._create_base_mmi()
        start_request = ET.SubElement(mmi_elem, "{http://www.w3.org/2008/04/mmi-arch}startRequest")
        self._set_base_params(start_request)

        data_elem = ET.SubElement(start_request, "{http://www.w3.org/2008/04/mmi-arch}data")
        data_elem.append(emma.getElem())

        return ET.tostring(mmi_elem, encoding="unicode")
    
    def print_xml(self, emma):
        print(self.do_start_request(emma))

# Classe para enviar requisição HTTP com requests
class MMIClient:
    def __init__(self, fusion_address, verify, cert_path = None, key_path = None):
        self.fusion_address = fusion_address
        self.verify = verify
        self.cert_ = (cert_path, key_path)

    def sendToIm(self, lifecycle_event_xml):
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(self.fusion_address, data=lifecycle_event_xml, headers=headers, verify=self.verify)
        if response.status_code == 200:
            print("Resposta recebida:", response.text)
        else:
            print("Erro ao enviar:", response.status_code, response.text)
