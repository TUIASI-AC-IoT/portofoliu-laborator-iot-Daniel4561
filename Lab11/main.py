from flask import Flask # type: ignore
from flask import jsonify # type: ignore
from flask import abort # type: ignore
from flask import request # type: ignore
from datetime import datetime
import os
app = Flask(__name__)

directoryPath = "Directory/"

os.makedirs(directoryPath, exist_ok=True)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/Directory", methods=['GET'])
def listFileNames():
    files = [f for f in os.listdir(directoryPath) if os.path.isfile(os.path.join(directoryPath, f))]

    return jsonify({'files':files})

@app.route("/Directory/<fileName>", methods=['GET'])
def listFileContent(fileName):
    path = directoryPath + fileName
    if not os.path.exists(path):
        return jsonify({"error": "Fișierul nu a fost găsit."}), 404
    
    with open(path, 'r') as f:
        content = f.read()
    return jsonify({'file' : fileName, 'content' : content}), 200

@app.route("/Directory/<fileName>", methods=['PUT'])
def createFileByNameAndContent(fileName):
    path = directoryPath + fileName
    content = request.get_data(as_text = True)

    file_exists = os.path.exists(path)
    with open(path, 'w') as f:
        f.write(content)
    
    if file_exists:
        return jsonify({'message' : "Fisier suprascris"}), 200
    else:
        return jsonify({'message' : "Fisier creat"}), 201
    
@app.route("/Directory", methods=['POST'])
def createFileByContent():
    content = request.get_data(as_text=True)
    if not content:
        return jsonify({"error": "Lipsește conținutul cererii."}), 400
    path = directoryPath + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

    with open(path, 'w') as f:
        f.write(content)
    return jsonify({"message":"Fisier creat", "file" : path}), 201

@app.route("/Directory/<fileName>", methods=['DELETE'])
def deleteFile(fileName):
    path = directoryPath + fileName
    if not os.path.exists(path):
        abort(404)
    os.remove(path=path)
    return ({"message" : "Fisier sters"}), 200

if __name__ == "__main__":
    app.run()