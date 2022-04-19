from distutils.log import error
from os import urandom
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]

def UserExist(username):
    if users.find({"Username":username}).count()==0:
        return False
    else
        return True

class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)
            
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": password,
            "Tokens": 4
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for this API"
        }
        return jsonify(retJson) 

class Classify(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        ur       = postedData["url"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        tokens = users.find({
            "Username": username
        })[0]["Tokens"]

        if tokens <= 0:
            return jsonify (generateReturnDictionary(303, "Not Enough Tokens!"))

        r = requests.get(url)
        retJson = {}
        with open("temp.jpg","wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify.image.py --model_dir=. --image_file=./temp.jpg')
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                retJson = json.load(g)

        users.update({
            "Username": username
        }, {
            "$set":{
                "Tokens": tokens-1
            }
        })
        return retJson