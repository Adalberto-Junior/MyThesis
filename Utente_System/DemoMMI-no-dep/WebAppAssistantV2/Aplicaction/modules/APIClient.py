import requests
import os


#====================================================================================================
# APIClient Class, responsible for handling API requests and user authentication
#=====================================================================================================

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = self.load_token()
        self.user = None
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def load_token(self):
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                return f.read().strip()
        return None

    def save_token(self, token):
        with open("token.txt", "w") as f:
            f.write(token)
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def login(self, email, password):
        url = f"{self.base_url}/auth/login"
        payload = {"email": email, "password": password}
        response = self.session.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user = data.get("user")
            if token:
                self.save_token(token)
                self.user = user
                print("✅ Login efetuado com sucesso!")
                return True
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
        return False

    def get(self, endpoint, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint, json=None, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def put(self, endpoint, json=None, **kwargs):
        return self.session.put(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
    
    def logout(self):
        url = f"{self.base_url}/auth/logout"
        response = self.session.post(url)
        if response.status_code == 200:
            self.token = None
            self.user = None
            self.session.headers.pop("Authorization", None)
            if os.path.exists("token.txt"):
                os.remove("token.txt")
            print("✅ Logout efetuado com sucesso!")
            return True
        else:
            print(f"❌ Erro no logout: {response.status_code} - {response.text}")
            return False
        
    def get_user(self):
        if self.user:
            return self.user
        else:
            print("❌ Usuário não autenticado.")
            return None
