from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from models import *
from helpers import *
 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ProfessorSecret'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/admission_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admission.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()


def recommend_programs(bot_id):
    applicant_qualifications = Qualification.query.filter_by(bot_id=bot_id).all()

    recommended_programs = []

    for qualification in applicant_qualifications:
        program_requirements = ProgrammeRequirement.query.filter_by(subject=qualification.subject).all()

        for requirement in program_requirements:
            if compare_symbols(qualification.symbol, requirement.minimum):
                recommended_programs.append(requirement.programme_id)

    recommended_program_names = Programme.query.filter(Programme.id.in_(recommended_programs)).all()

    return recommended_program_names


 
@app.route("/wasms", methods=['POST'])
def wa_sms_reply():
    phone = request.form.get('WaId')
    name = request.form.get('ProfileName')
    #print(phone)
    bot = Bot.query.filter(phone==phone).first()
    
    print(bot)

    if bot is None:
        new_bot = Bot(name, phone, 'main', '', '')
        db.session.add(new_bot)
        db.session.commit()
 
    msg = request.form.get('Body').lower() # Reading the message from the whatsapp
 
    
    resp = MessagingResponse()
    reply=resp.message()
    print(msg)
    # Create reply
 
    # Text response
    if msg == "cancel":
        bot.menu = 'main'
        db.session.commit()

        reply.body("The process has been cancelled.")
        return str(resp)
        
    if bot.firstname == '' and bot.menu != 'profile-firstname':
        bot.menu = 'profile-firstname'
        db.session.commit()

        reply.body("What is your firstname?")
        return str(resp)
        
    if bot.menu == 'profile-firstname':
        if not msg.strip():
            reply.body("Your firstname cannot be empty")
            return str(resp)
            
        bot.firstname = msg
        bot.menu = 'profile-surname'
        db.session.commit()
            
        reply.body("What is your surname?")
        return str(resp)
        
        
    if bot.menu == 'profile-surname':
        if not msg.strip():
            reply.body("Your surname cannot be empty")
            return str(resp)
                
        bot.surname = msg
        bot.menu = 'o-qualifications'
        db.session.commit()
                
        reply.body("*WHAT O LEVEL QUALIFICATIONS DO YOU HAVE:*\n\n_Enter your qualification and symbol obtained like this: *Mathematics,C* do not space after comma._")
        return str(resp)
     
     
    if bot.menu == 'o-qualifications':
        if not msg.strip():
            reply.body("O Level Qualifications cannot be empty")
            return str(resp)
        
        if msg == '1':
            bot.menu = 'a-qualifications'
            db.session.commit()   
            
            reply.body("*WHAT A LEVEL QUALIFICATIONS DO YOU HAVE:*\n\n_Enter your qualification and symbol obtained like this: *Mathematics,C* do not space after comma._")
            return str(resp) 
        
        if msg == '2':
            bot.menu = 'main'
            db.session.commit()   
            
            reply.body("Process was ended!")
            return str(resp)
        
        if not validate_subject_grade(msg):
            reply.body("Invalid O level qualification input format, *TRY AGAIN*")
            return str(resp)
        
        subject = msg.split(',')[0]
        symbol = msg.split(',')[1]
        
        new_qualification = Qualification(bot.id, 'O LEVEL', subject.capitalize(), symbol.capitalize())
        db.session.add(new_qualification)
        db.session.commit()
        
        reply.body("O LEVEL SUBJECT WAS ADDED SUCCESSFULLY\n\n You may add another one or... \n*1) Move To A Level Qualifications*\n*2) Cancel And Move To Main Menu*")
        return str(resp)
    
    
    if bot.menu == 'a-qualifications':
        if not msg.strip():
            reply.body("A Level Qualifications cannot be empty")
            return str(resp)
        
        if msg == '1':
            bot.menu = 'o-qualifications'
            db.session.commit()   
            
            reply.body("*WHAT O LEVEL QUALIFICATIONS DO YOU HAVE:*\n\n_Enter your qualification and symbol obtained like this: *Mathematics,C* do not space after comma._")
            return str(resp) 
        
        if msg == '2':
            bot.menu = 'main'
            db.session.commit()   
            
            reply.body("Process was ended!")
            return str(resp)
        
        if not validate_subject_grade(msg):
            reply.body("Invalid A level qualification input format, *TRY AGAIN*")
            return str(resp)
        
        subject = msg.split(',')[0]
        symbol = msg.split(',')[1]
        
        new_qualification = Qualification(bot.id, 'A LEVEL', subject.capitalize(), symbol.capitalize())
        db.session.add(new_qualification)
        db.session.commit()
        
        reply.body("A LEVEL SUBJECT WAS ADDED SUCCESSFULLY\n\n You may add another one or... \n*1) Back To O Level Qualifications*\n*2) Cancel And Move To Main Menu*")
        return str(resp)
    
    
    if bot.menu == 'main':
        
        if msg == '1':
            bot.menu = 'select-programme'
            db.session.commit()
            
            programmes = Programme.query.all()
            progs = ''
            
            for programme in programmes:
                progs += str(programme.id)+') '+programme.name+'\n'
                
            reply.body("*Select Programme From List*\n"+progs)
            
            return str(resp)
        
        if msg == '2':
            application = Application.query.filter_by(bot_id=bot.id).first()
            if not application:
                reply.body("YOU HAVE NO APPLICATION TO TRACK, SELECT OPTION 1) TO APPLY")
                return str(resp)
            
            programme_choices = db.session.query(Programme.name, ApplicationChoice.choice)\
                   .join(ApplicationChoice, Programme.id == ApplicationChoice.programme_id)\
                   .join(Application, Application.id == ApplicationChoice.application_id)\
                   .filter(Application.bot_id == bot.id)\
                   .all()
            
            if not programme_choices:
                reply.body("YOU HAVE NO APPLICATION PROGRAMME CHOICES TO TRACK, SELECT OPTION 1) TO APPLY")
                return str(resp)
            
            choices_string = ""
            for ch in programme_choices:
                choices_string += "\t*"+str(ch[1])+")* "+ch[0]+"\n"
                
            bot.menu = 'track-application'
            db.session.commit()    
            application_string = "*APPLICATION DETAILS*\n\nNAME: _"+ bot.firstname.capitalize()+" " + bot.surname.capitalize() +"_\nSTATUS: _"+application.status+"_\nDATE: _"+str(application.created_at)+"_\nPROGRAMME CHOICES:\n"+choices_string+"\n*1)* EXIT\n*2)* DELETE APPLICATION"
            reply.body(application_string)
            return str(resp)
        
        if msg == '3':
            programmes = recommend_programs(bot.id)
            progs = ''
            
            for programme in programmes:
                progs += str(programme.id)+') '+programme.name+'\n'
                
            reply.body("*LIST OF SYSTEM SUGGESTED PROGRAMMES*\n"+progs)
            
            return str(resp)
        
        if msg == '4':
            faqs = Faq.query.all()
            faqs_string = ''
            
            i = 0
            for faq in faqs:
                i+=1
                faqs_string += "*"+str(i)+')* *'+faq.question+'*\n_'+faq.response+"_\n"
                
            reply.body("*FAQs*\n\n"+faqs_string)
            
            return str(resp)
        
        if msg == '5':
            bot.menu = 'give-feedback'
            db.session.commit()
            
            reply.body("*GIVE US FEED ON YOUR EXPERIENCE, QUERY, ERRORS AND/OR SUGGESTIONS*\n_type your feedback and send_")
            return str(resp)
        
            
        reply.body("*ADMISSIONS MAIN MENU*\n1) Start Application\n2) Track Application\n3) Suggested Programmes\n4) FAQs\n5) Give Us Feedback")
    
    
    if bot.menu == 'select-programme':
        if not is_integer(msg):
            reply.body("Invalid input, please make sure its option number. \n*TRY AGAIN*")
            return str(resp)
        
        programme = Programme.query.filter_by(id=msg).first()
        if not programme:
            reply.body("Specified product was not found. \n*TRY AGAIN*")
            return str(resp)
        
        application = Application.query.filter_by(id=bot.id).first()
        if not application:
            ct = datetime.datetime.now()
            new_application = Application(bot.id, 'PENDING', ct)
            db.session.add(new_application)
            db.session.commit()
            
            new_application_choice = ApplicationChoice(new_application.id, programme.id, 1)
            db.session.add(new_application_choice)
            db.session.commit()
            
            reply.body("Programme selected successfully. \n*PLEASE SELECT SECOND CHOICE*")
            return str(resp)
         
        maximum = 3    
        application_choice = ApplicationChoice.query.filter_by(application_id=application.id).count()
        if maximum <= application_choice or application_choice == 3:
            bot.menu = 'confirm-finish'
            db.session.commit()
            reply.body("*Maximum of 3 programme choices already reached.* \n\n *1)* Confirm & Finish Application\n*2)* Start All Over")
            return str(resp)
        
        choice = application_choice + 1
        new_application_choice = ApplicationChoice(application.id, programme.id, choice)
        db.session.add(new_application_choice)
        db.session.commit()
            
        reply.body("Programme selected successfully. \n*PLEASE SELECT THIRD CHOICE*")
        return str(resp)
    
    if bot.menu == 'confirm-finish':
        if msg == '1':
            bot.menu = 'main'
            db.session.commit()
            reply.body("*THANK YOU FOR APPLYING AT MIDLANDS STATE UNIVERSITY, YOUR APPLICATION WAS CONFIRMED SUCCESSFULLY*")
            return str(resp)
        
        if msg == '2':
            application = Application.query.filter_by(bot_id=bot.id).first()
            ApplicationChoice.query.filter_by(application_id=application.id).delete()
            db.session.commit()
            
            Application.query.filter_by(bot_id=bot.id).delete()
            db.session.commit()
            
            bot.menu = 'main'
            db.session.commit()
            reply.body("*YOUR APPLICATION WAS NOT CONFIRMED, WE DELETED IT YOU MAY APPLY AGAIN*")
            return str(resp)
        
        else:
            reply.body("Invalid option *TRY AGAIN*")
            return str(resp)
    
    
    if bot.menu == 'track-application':
        if msg == '1':
            bot.menu = 'main'
            db.session.commit()
            reply.body("*SUCCESSFULLY EXITED*")
            return str(resp)
        
        if msg == '2':
            application = Application.query.filter_by(bot_id=bot.id).first()
            ApplicationChoice.query.filter_by(application_id=application.id).delete()
            db.session.commit()
            
            Application.query.filter_by(bot_id=bot.id).delete()
            db.session.commit()
            
            bot.menu = 'main'
            db.session.commit()
            reply.body("*YOUR APPLICATION WAS DELETED, YOU CAN APPLY AGAIN*")
            return str(resp)
        
        else:
            reply.body("Invalid option *TRY AGAIN*")
            return str(resp)
    
    if bot.menu == 'give-feedback':
        new_feedback = Feedback(bot.id, msg)
        db.session.add(new_feedback)
        db.session.commit()
        
        bot.menu = 'main'
        db.session.commit()
            
        reply.body("*Feedback sent successfully*")
        return str(resp)
    
    
    print(msg)
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True, port=8080)