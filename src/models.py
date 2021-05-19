from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    fk_character = db.relationship("Character_Favorite", lazy=True)
    fk_planet = db.relationship("Planet_Favorite", lazy=True)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    climate = db.Column(db.String(40))
    population = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    rotation_period = db.Column(db.Integer)
    diameter = db.Column(db.Integer)
    terrain = db.Column(db.String(40))
    
    def _repr_(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "Name": self.name,
            "Climate": self.climate,
            "Population": self.population,
            "Orbital_Period": self.orbital_period,
            "Rotation_Period": self.rotation_period,
            "Diameter": self.diameter,
            "Terrain": self.terrain
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(15))
    hair_color = db.Column(db.String(40))
    eye_color = db.Column(db.String(40))
    birth_year = db.Column(db.String(40), nullable=False)
    height = db.Column(db.Integer)
    skin_color = db.Column(db.String(40))
    
    def __repr__(self):
        return '<character %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "Name": self.name,
            "Gender": self.gender,
            "Hair_Color": self.hair_color,
            "Eye_Color": self.eye_color,
            "Birth_Year": self.birth_year,
            "Height": self.height,
            "Skin_Color": self.skin_color
        }

class Character_Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    character = db.relationship("Character", lazy="subquery")
    
    def _repr_(self):
        return "<Fav_Character %r>" % self.character.name
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "route": "/character/" + str(self.id),
            "name": self.character.name
        }

class Planet_Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"))
    planet = db.relationship("Planet", lazy="subquery")
    
    def _repr_(self):
        return "<Fav_Planet %r>" % self.planet.name
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "route": "/planet/" + str(self.id),
            "name": self.planet.name
        }