import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import template
from datetime import date, datetime
import Config

YEAR = 2022
ENV = 'prod'
cred = credentials.Certificate(Config.DB_CERT)
firebase_admin.initialize_app(cred)
db = firestore.client()

def age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

class User:
    def __init__(self, data:dict):
        self.name = data.get("name")
        self.accepted = data.get("accepted")
        self.email = data.get("email")
        self.uid = data.get("uid")
        self.birthdate = datetime.strptime(data.get("birthDate"), '%Y-%m-%d').date()
        self.city = data.get("city")
        self.displayName = data.get("displayName")
        self.food = data.get("food")
        self.fullName = data.get("fullName")
        self.gdpr = data.get("gdpr")
        self.githubUrl = data.get("githubUrl")
        self.linkedinUrl = data.get("linkedinUrl")
        self.nickname = data.get("nickname")
        self.photoUrl = data.get("photoUrl")
        self.shirtSize = data.get("shirtSize")
        self.terms = data.get("terms")

    def toString(self):
        return f"User({self.uid}): {self.fullName} - {self.email} - {self.city} - {self.birthdate} - {age(self.birthdate)} - {self.shirtSize} - {self.accepted}"
    @staticmethod
    def table_def():
        return ['email', 'fullName', 'birthdate', 'city', 'food', 'githubUrl', 'linkedinUrl', 'accepted']
    def to_raw(self):
        return [self.email, self.fullName, self.birthdate, self.city, self.food, self.githubUrl, self.linkedinUrl, self.accepted]

def get_users():
    users_ref = db.collection('hackeps-'+str(YEAR)+'/'+ENV+'/users')
    docs = users_ref.stream()
    users = []
    for doc in docs:
        users.append(User(doc.to_dict()))
    return users


s=None
def init_mail():
    global s
    if s is None:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(Config.MAIL, Config.MAIL_PASSWORD)


def send_mail(to, name):
    global s
    init_mail()
    me = Config.MAIL    

    msg = MIMEMultipart()
    msg['Subject'] = "HackEPS 2022 - Admisió"
    msg['From'] = me
    msg['To'] = to
    html = template.get_html(name)
    msg.attach(MIMEText(html, "html"))
    msg_str = msg.as_string()
    s.sendmail(me, to, msg_str)


def get_pending_users():
    users = get_users()
    pending_users = []
    for user in users:
        if user.accepted=='PENDENT':
            pending_users.append(user)
    return pending_users

def accept_user(user:User, mail=False):
    users_ref = db.collection('hackeps-'+str(YEAR)+'/'+ENV+'/users')
    doc_ref = users_ref.document(user.uid)
    doc_ref.update({"accepted": "YES"})
    if mail:
        send_mail(user.email, user.fullName)

def unnaccept_user(mail):
    users = get_users()
    for user in users:
        if user.email==mail:
            users_ref = db.collection('hackeps-'+str(YEAR)+'/'+ENV+'/users')
            doc_ref = users_ref.document(user.uid)
            doc_ref.update({"accepted": "PENDENT"})
            print('unaccepted', user.email)
            return True
def accept():
    for user in get_pending_users():
        print(user.toString())
        inp = input("press y to accept and s to skip and e to exit:  ")
        if inp=='e':
            break
        elif inp == 'y':
            accept_user(user, True)
            print("accepted")
        else:
            print("skipping")

def delete(mail):
    users = get_users()
    for user in users:
        if user.email==mail:
            users_ref = db.collection('hackeps-'+str(YEAR)+'/'+ENV+'/users')
            doc_ref = users_ref.document(user.uid)
            doc_ref.delete()
            print('deleted', user.email)
            return True
    print("not found")
    return False

def search(mail):
    users = get_users()
    for user in users:
        if user.email==mail:
            print(user.toString())
            return True
    print("not found")
    return False

accept()
if not s is None:
    s.quit()