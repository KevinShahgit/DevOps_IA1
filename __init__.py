from flask import Flask
from flask_login import LoginManager
import pymongo

app = Flask(__name__)
app.config['SECRET_KEY'] = '892gf{r89094r2{98ihkb230JKBKjdfv' #random key
app.debug = True
login = LoginManager(app)
login.login_view = 'logview'
client = pymongo.MongoClient('mongodb+srv://MiniP:lfs37lfs37@cluster0-dwdr2.mongodb.net/test?retryWrites=true&w=majority')
db = client["CollegeBuddy"]
stu = db["student"]
misc = db["miscellaneous"]
teach = db["teacher"]

from app import routes