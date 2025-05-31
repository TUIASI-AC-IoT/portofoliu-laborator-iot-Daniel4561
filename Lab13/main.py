from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from datetime import timedelta
import os

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = '456123901234567890' 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

jwt_blocklist = set()

users = {
    "user1": {"password": "parola1", "role": "admin"},
    "user2": {"password": "parola2", "role": "owner"},
    "user3": {"password": "parolaX", "role": "owner"},
}

directoryPath = "Sensors/"
os.makedirs(directoryPath, exist_ok=True)


@app.route('/auth', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if username in users and users[username]["password"] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify(msg="Bad username or password"), 401

@app.route('/auth/jwtStore', methods=['GET'])
@jwt_required()
def check_token():
    jti = get_jwt()["jti"]
    if jti in jwt_blocklist:
        return jsonify(msg="Token invalid"), 404
    username = get_jwt_identity()
    role = users[username]["role"]
    return jsonify(role=role), 200

@app.route('/auth/jwtStore', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)
    return jsonify(msg="Token invalidat"), 200

def role_required(*roles):
    def wrapper(fn):
        @jwt_required()
        def decorator(*args, **kwargs):
            jti = get_jwt()["jti"]
            if jti in jwt_blocklist:
                return jsonify(msg="Token invalid"), 401
            username = get_jwt_identity()
            user_role = users.get(username, {}).get("role", "guest")
            if user_role not in roles:
                return jsonify(msg="Access denied"), 403
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return decorator
    return wrapper

# RUTE protejate după roluri

@app.route('/')
def home():
    return 'Hello, Flask!'

@app.route('/Sensors/<sensorID>', methods=['GET'])
@role_required("owner", "admin")
def get_sensor(sensorID):
    file_path = os.path.join(directoryPath, f"{sensorID}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = file.read()
        return jsonify({"sensorID": sensorID, "data": data})
    else:
        return "Sensor data not found", 404

@app.route('/Sensors/<sensorID>', methods=['POST'])
@role_required("admin")
def configFile(sensorID):
    file_path = os.path.join(directoryPath, f"config_{sensorID}.txt")
    content = request.get_data(as_text=True)
    if not content:
        return jsonify({"sensorID": sensorID, "status": "No data provided"}), 400
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(content)
        return jsonify({"sensorID": sensorID, "status": "Configuration file created"}), 201
    else:
        return jsonify({"sensorID": sensorID, "status": "Configuration file already exists"}), 409

@app.route('/Sensors/<configFile>', methods=['PUT'])
@role_required("admin")
def updateFile(configFile):
    file_path = os.path.join(directoryPath, f"config_{configFile}.txt")
    content = request.get_data(as_text=True)
    if not content:
        return jsonify({"fileID": configFile, "status": "No data provided"}), 400
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(content)
        return jsonify({"fileID": configFile, "status": "File updated"}), 200
    else:
        return jsonify({"fileID": configFile, "status": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
