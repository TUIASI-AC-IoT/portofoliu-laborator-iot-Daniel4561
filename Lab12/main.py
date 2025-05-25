from flask import Flask
from flask import request
from flask import jsonify
import os
app = Flask(__name__)

directoryPath = "Sensors/"

os.makedirs(directoryPath, exist_ok=True)

@app.route('/')
def home():
    return 'Hello, Flask!'

@app.route('/Sensors/<sensorID>', methods=['GET'])
def get_sensor(sensorID):
    file_path = os.path.join(directoryPath, f"{sensorID}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = file.read()
        return jsonify({"sensorID": sensorID, "data": data})
    else:
        return "Sensor data not found", 404

@app.route('/Sensors/<sensorID>', methods=['POST'])
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
    app.run(debug=True)