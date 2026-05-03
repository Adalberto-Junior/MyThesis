#======================================================================
# Casa Viva - Backend
# File: app.py
# Created by: Adalberto Jr
# Created date: 30/04/2025
# Version: 1.0
# Python: 3.10
# Local: Universidade de Aveiro
# Description: This file is the main entry point for the Flask application.
#              It initializes the Flask app, sets up the database connection,
#              and registers the routes for the application.
# This file is part of the Casa Viva project.
#=======================================================================
#

# Import necessary modules and packages
from flask import Flask, request, jsonify, send_from_directory, Blueprint
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv
from auth import auth_bp
from utente import utente_bp
from casaViva import casaViva_bp
from extensions import mongo

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")

# Initialize Flask app
app = Flask(__name__, static_url_path="/static")

CORS(app)

# Configurações
app.config["MONGO_URI"] = "mongodb://localhost:27017/Casa_Viva"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Inicializa Mongo
# mongo = PyMongo(app)
mongo.init_app(app)

# Registra Blueprint das rotas
api_bp = Blueprint('api', __name__, url_prefix='/casa_viva')
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(utente_bp)
api_bp.register_blueprint(casaViva_bp)

app.register_blueprint(api_bp)

#app.register_blueprint(auth_bp)
#app.register_blueprint(utente_bp)

"""""
client = MongoClient("mongodb://localhost:27017/")
db = client["test"]
users = db["user"]

def create_token(user_id):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=20)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

@app.route("/casa_viva/register", methods=["POST"])
def register():
    data = request.json
    if users.find_one({"email": data["email"]}):
        return jsonify({"error": "Email já registrado"}), 400

    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
    user_id = users.insert_one({"name":data["username"],"email": data["email"], "password": hashed,"databirth": data["databirth"]}).inserted_id
    token = create_token(user_id)
    return jsonify({"token": token})

@app.route("/casa_viva/login", methods=["POST"])
def login():
    data = request.json
    user = users.find_one({"email": data["email"]})
    if not user or not bcrypt.checkpw(data["password"].encode(), user["password"]):
        return jsonify({"error": "Credenciais inválidas"}), 401

    token = create_token(user["_id"])
    return jsonify({"token": token})

@app.route("/casa_viva/protected", methods=["GET"])
def protected():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    token = auth.split()[1]
    decoded = decode_token(token)
    if not decoded:
        return jsonify({"error": "Token inválido ou expirado"}), 401

    return jsonify({"message": "Você acessou uma rota protegida", "user_id": decoded["user_id"]})

@app.route("/casa_viva/user", methods=["GET"])
def get_user():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Token ausente"}), 401

    token = auth.split()[1]
    decoded = decode_token(token)
    if not decoded:
        return jsonify({"error": "Token inválido ou expirado"}), 401

    user = users.find_one({"_id": ObjectId(decoded["user_id"])})
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    user_data = {
        "name": user["name"],
        "email": user["email"],
        "databirth": user["databirth"]
    }
    return jsonify(user_data)

@app.route("/casa_viva/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})
"""

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../HELLO_WORLD_REACT/build"))

    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    
    static_path = os.path.join(build_dir, "static", path)
    if path.startswith("static/") and os.path.exists(static_path):
        return send_from_directory(os.path.join(build_dir, "static"), path[7:])

    return send_from_directory(build_dir, "index.html")


"""""
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../hello_world_react/build"))
    file_path = os.path.join(root_dir, path)

    if path != "" and os.path.exists(file_path):
        return send_from_directory(root_dir, path)
    else:
        return send_from_directory(root_dir, "index.html")
"""""
# Uncomment the following lines to serve the React app from the Flask server
""""
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(f"../hello_world_react/build/{path}"):
        return send_from_directory("../hello_world_react/build", path)
    else:
        return send_from_directory("../hello_world_react/build", "index.html")
"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    # app.run(debug=True)