from flask import Flask
from flask_login import LoginManager
import pymongo
from dotenv import load_dotenv
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = '892gf{r89094r2{98ihkb230JKBKjdfv' #random key
app.debug = True
login = LoginManager(app)
login.login_view = 'logview'
p = Path("./.env")
load_dotenv(dotenv_path = p)
client = pymongo.MongoClient(os.getenv("MONGO"))
db = client["CollegeBuddy"]
stu = db["student"]
misc = db["miscellaneous"]
teach = db["teacher"]

from app import routes