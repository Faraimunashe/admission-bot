from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
import datetime

#initialize DB and Marshmallow
db = SQLAlchemy()

# table Model Class
class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    menu = db.Column(db.String(80))
    firstname = db.Column(db.String(80), nullable=True)
    surname = db.Column(db.String(80), nullable=True)

    def __init__(self, name, phone, menu, firstname, surname):
        self.name=name
        self.phone=phone
        self.menu=menu
        self.firstname=firstname
        self.surname=surname
        

class Qualification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer)
    type = db.Column(db.String(30))
    subject = db.Column(db.String(80))
    symbol = db.Column(db.String(1))

    def __init__(self, bot_id, type, subject, symbol):
        self.bot_id=bot_id
        self.type=type
        self.subject=subject
        self.symbol=symbol 


class Programme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name=name


class ProgrammeRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    programme_id = db.Column(db.Integer)
    subject = db.Column(db.String(80))
    minimum = db.Column(db.String(1))

    def __init__(self, programme_id, subject, minimum):
        self.programme_id=programme_id
        self.subject=subject
        self.minimum=minimum     


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer)
    status = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now())
    
    def __init__(self, bot_id, status, created_at):
        self.bot_id=bot_id
        self.status=status
        self.created_at=created_at
    
    
        
class ApplicationChoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer)
    programme_id = db.Column(db.Integer)
    choice = db.Column(db.Integer)

    def __init__(self, application_id, programme_id, choice):
        self.application_id=application_id
        self.programme_id=programme_id
        self.choice=choice  
         
        
        
class Aid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name=name 
    
    
class ApplicantAid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer)
    aid_id = db.Column(db.Integer)

    def __init__(self, application_id, aid_id):
        self.application_id=application_id
        self.aid_id=aid_id    


class Faq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100))
    response = db.Column(db.String(100))

    def __init__(self, question, response):
        self.question=question 
        self.response=response
        
        
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_id = db.Column(db.Integer)
    description = db.Column(db.String(80))
    
    def __init__(self, bot_id, description):
        self.bot_id=bot_id
        self.description=description