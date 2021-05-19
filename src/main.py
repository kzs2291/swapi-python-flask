"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Character_Favorite, Planet_Favorite

# JWT authentication
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import datetime

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

# error handling
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# endpoints listing
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# user registration
@app.route("/register", methods=["POST"])
def register_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email is None:
        return jsonify({"msg": "Please provide a valid email."}), 400
    if password is None:
        return jsonify({"msg": "Please provide a valid password."}), 400
    
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        # case user not found in db
        return jsonify({"msg": "User already exists."}), 401
    else:
        new_user = User()
        new_user.email = email
        new_user.password = password

        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User account was successfully created."}), 200
    
# user log in
@app.route("/login", methods=["POST"])
def login():
        email = request.json.get("email", None)
        password = request.json.get("password", None)

        # user validation step
        if email is None:
            return jsonify({"error": "Please provide a valid email."}), 400
        if password is None:
            return jsonify({"error": "Please provide a valid password."}), 400
        
        user = User.query.filter_by(email=email, password=password).first()

        if user is None:
            return jsonify({"error": "Invalid email or password."}), 401 
        elif user.password != password:
            return jsonify({"error": "User or password not found."}), 401
        else:
            print(user)
            # pass user id as parameter to generate a new token
            access_token = create_access_token(identity=user.id)
            return jsonify({ "token": access_token, "user_id": user.id }), 200


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    
     # UAM with get_jwt_identity
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    print(current_user_id, user)
    return jsonify({"id": user.id, "email": user.email }), 200

# users
@app.route('/users', methods=['GET'])
def getUsers():
    users = User.query.all()
    request = list(map(lambda user:user.serialize(),users))    
    return jsonify(request), 200


@app.route('/users', methods=["POST"])
def createUsers():
    data = request.get_json()
    user1 = User(username=data["username"],email=data["email"],password=data["password"])
    db.session.add(user1)
    db.session.commit()
    return jsonify("Message : New user has been added!."),200

@app.route('/users/<id>', methods=["DELETE"])
@jwt_required()
def delUsers(id):
    current_user = get_jwt_identity()
    user1 = User.query.get(id)
    if user1 is None:
        raise APIException("The user does not exist!.",status_code=404)
    db.session.delete(user1)
    db.session.commit()
    return jsonify({"Proccess completed by:" : current_user}),200


# planets

@app.route('/planet', methods=['GET'])
def getPlanets():
    planets = Planet.query.all()
    request = list(map(lambda planet:planets.serialize(),planets))    
    return jsonify(request), 200

@app.route('/planets/<int:id>', methods=['GET'])
def getPlanets_id(id):
    planets = Planet.query.filter_by(id=id).first()
    if planeta is None:
        raise APIException("Message: Requested data not found.",status_code=404)
    request = planets.serialize()
    return jsonify(request), 200

# characters
@app.route('/characters', methods=['GET'])
def getcharacter():
    characters = Character.query.all()
    request = list(map(lambda character:characters.serialize(),characters))    
    return jsonify(request), 200

@app.route('/character/<int:id>', methods=['GET'])
def getcharacter_id(id):
    #user = User.query.get(id)
    characters = Character.query.filter_by(id=id).first()
    if character is None:
        raise APIException("Message: Requested data not found.",status_code=404)
    request = characters.serialize()
    return jsonify(request), 200

# favorites
@app.route('/favorites/', methods=['GET'])
def get_favorites():
    response = {"message": "it worked"}
    return jsonify(response)

@app.route('/users/<int:id_user>/favorites', methods=['GET'])
def get_favoritesfromuser(id_user):
    favcharacter = Fav_character.query.filter_by(user_id=id_user)
    favplanet = Fav_Planet.query.filter_by(user_id=id_user)
    favcharacter_serialize = list(map(lambda x:x.serialize(),favcharacter))
    favplanet_serialize = list(map(lambda x:x.serialize(),favplanet))
    fav_response = favcharacter_serialize + favplanet_serialize
    return jsonify(fav_response)

@app.route('/users/<int:id_user>/favorites', methods=['POST'])
# @jwt_required()
def POST_favoritestouser(id_user):
    tipo = request.json.get("tipo", None)
    id = request.json.get("id", None)
    
    if tipo == "planet":
        favPlanet = Planet_Favorite(user_id=id_user, planet_id=id)
        db.session.add(favPlanet)
        db.session.commit()
        
        return jsonify(favPlanet.serialize()), 200
    
    if tipo == "character":
        favcharacter = Character_Favorite(user_id=id_user, character_id=id)
        db.session.add(favcharacter)
        db.session.commit()
        
        return jsonify(favcharacter.serialize()), 200
    return APIException("Bad Request", status_code=400)

@app.route('/favorite/<string:tipo>/<int:favorite_id>', methods=['DELETE'])
# @jwt_required()
def delete_favfromuser(tipo, favorite_id):
    if tipo == "planet":
        delete_fav = Planet_Favorite.query.filter_by(id=favorite_id).first()
        print(delete_fav)
        if delete_fav is None:
            return "Not Found", 401
        else:
            db.session.delete(delete_fav)
            db.session.commit()
            return jsonify(delete_fav.serialize()),200
    elif tipo == "character":
        delete_fav = Character_Favorite.query.filter_by(id=favorite_id).first()
        print(delete_fav)
        if delete_fav is None:
            return "Not Found", 401
        else:
            db.session.delete(delete_fav)
            db.session.commit()
            return jsonify(delete_fav.serialize()),200
        
    return "Wrong Request", 402


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)