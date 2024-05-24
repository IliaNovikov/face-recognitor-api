from fastapi import FastAPI, File, UploadFile
from fastapi.responses import *
from fastapi.requests import Request
# from keras.models import load_model
# from PIL import Image, ImageOps
import numpy as np
import os
import socket
import yaml
import face_recognition
from os import walk
import requests

app = FastAPI()

# ip = "127.0.0.1"
# port = 3312
# login = "operator"
# password = "1234"

with open(r"config.yml") as file:
    config_data = yaml.load(file, Loader=yaml.FullLoader)
    ip = config_data["localserver_ip"]
    port = config_data["localserver_port"]
    login = config_data["user_login"]
    password = config_data["user_password"]

@app.get("/")
def root():
    return "Hello world"

# @app.post("/face")
# def face(file: UploadFile = File(...)):
#     print(file.filename)
#     content = file.file.read()
#     with open(file.filename, "wb") as f:
#         f.write(content)
#     file.file.close()
#     return "success"

@app.post("/add/{name}")
def add(name: str, file: UploadFile = File(...)):
    content = file.file.read()
    filename_array = file.filename.split(".")
    filename_array[0] = name
    filename = ".".join(filename_array)
    with open("known_images/" + filename, "wb") as f:
        f.write(content)
    file.file.close()

@app.post("/predict")
def predict(file: UploadFile = File(...)):

    print(file.filename)
    content = file.file.read()
    with open(file.filename, "wb") as f:
        f.write(content)
    file.file.close()

    # files = {'media': open(file.file, 'rb')}

    # response = requests.post("http://192.168.88.207:9090/face_analytics/predict",   data={
    #   'filename': file.file ,
    #   "msg":"hello" ,
    #   "type" : "multipart/form-data"
    # }, files={"file": file.file})
    data = {'name': (None, file.filename), 'description': (None, 'упс'), 'image': open(file.filename, 'rb')}
    response = requests.post("http://192.168.88.207:9090/face_analytics/predict", files=data)
    print(response.json()['confidence_bbox'])

    if(response.json()['confidence_bbox'] >= 0.8):
        message = f"LOGIN 1.8 {login} {password}\r\nALLOWPASS 1 1 UNKNOWN\r\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(message.encode('utf-8'))
        s.close()
        return "success"



@app.post("/access")
def access(file: UploadFile = File(...)):
    known_images = next(walk("known_images"), (None, None, []))[2]
    print(known_images)

    unknown_image = face_recognition.load_image_file("face.jpg")
    unknown_encoding = face_recognition.face_encodings(unknown_image)

    for i in known_images:
        known_image = face_recognition.load_image_file("known_images/" + i)
        known_encoding = face_recognition.face_encodings(known_image)
        results = face_recognition.compare_faces(known_encoding[0], unknown_encoding)
        if results[0] == True:
            message = f"LOGIN 1.8 {login} {password}\r\nALLOWPASS 1 1 UNKNOWN\r\n"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(message.encode('utf-8'))
            s.close()
            break

    print(known_encoding)
    print(unknown_encoding)


    print("result:", results)

    # message = f"LOGIN 1.8 {login} {password}\r\nALLOWPASS 1 1 UNKNOWN\r\n"
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((ip, port))
    # s.send(message.encode('utf-8'))
    # s.close()
    return "success"
