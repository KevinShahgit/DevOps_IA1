from app import app, login, stu, teach, misc
from app.users import User
from flask_login import current_user, login_user, logout_user, login_required
from app.form import SignupForm, LoginForm, CodeForm, Feedback, Teacher, Notify, OTPform
from flask import url_for, redirect, flash, render_template, get_flashed_messages, request
from datetime import datetime,date
import math, random, requests, json, jsonify, datetime, bson.objectid, time


def generateOTP() :   # 4 digit OTP
    digits = "0123456789"
    OTP = "" 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
    return int(float(OTP))

@app.route('/', methods = ["GET", "POST"])
@app.route('/login', methods = ["GET", "POST"])
def logview():
    if current_user.is_authenticated:
        if current_user.type == 'S':
            return redirect(url_for('stuhome'))
        else:
            return redirect(url_for('profhome'))
    l1 = LoginForm()
    if l1.validate_on_submit():
        user = teach.find_one({"_id": l1.id.data})
        if user is not None and l1.password.data == user.get("pword"):
            t = User(id = user.get("_id"), password = user.get("pword"), type = "T")
            login_user(t, duration=datetime.timedelta(hours=1))
            return redirect(url_for('profhome'))
        elif user is not None:
            flash('Invalid username/password combination.')
        else:
            user = stu.find_one({"_id": l1.id.data})
            if user is not None and l1.password.data == user.get("pword"):
                t = User(id = user.get("_id"), password = user.get("pword"), type = "S")
                login_user(t, duration=datetime.timedelta(hours=1))
                return redirect(url_for('stuhome'))
            else:
                flash('Invalid username/password combination.')
    return render_template('login.html',
                            form = l1,
                            title = 'Log in.',
                            template ='login-page',
                            body = "Log in with your User account.")
                            

@app.route('/signup', methods = ["GET", "POST"])
def sign():
    s1 = SignupForm()
    if s1.validate_on_submit():
        existing_user = teach.find_one({"_id": s1.id.data})
        if existing_user is None:
            existing_user = stu.find_one({"_id": s1.id.data})
            if existing_user is None:
                c = generateOTP()
                requests.post("https://us-central1-dbcheck-ff691.cloudfunctions.net/sendMail", data=json.dumps({"check":1,"email": s1.id.data,"code": c}),headers={'Content-Type': 'application/json'})
                temp = {
                    'email' : s1.id.data,
                    'name' : s1.fname.data + " " + s1.lname.data,
                    'pword' : s1.password.data,
                    'roll' : s1.roll.data,
                    'year' : s1.year.data,
                    'branch' : s1.branch.data,
                    'division' : s1.division.data,
                    'AOA' : [],
                    'PSOT' : [],
                    'RDBMS' : [],
                    'TACD' : [],
                    'OSTPL' : [],
                    "code" : c
                }
                x = misc.insert_one(temp)
                return redirect("http://localhost:5000/verify/" + str(x.inserted_id))
        flash('A user already exists with that email address')
    return render_template('signup.html',
                           title = 'Create an Account.',
                           form = s1,
                           template = 'signup-page',
                           body = "Sign up for an user account.")
                           
@app.route('/verify/<s>', methods=["GET", "POST"])
def verify(s):
    s2  = CodeForm()
    temp = misc.find_one({"_id" : bson.objectid.ObjectId(s)})
    if s2.validate_on_submit():
        if temp.get("code") == s2.code.data:
            temp.pop("code")
            x = temp.pop("email")
            temp["_id"] = x
            stu.insert_one(temp)
            misc.delete_one({'_id': bson.objectid.ObjectId(s)})
            user = User(id = temp.get("_id"), password = temp.get("pword"), type = 'S')
            login_user(user, duration=datetime.timedelta(hours=1))
            return redirect(url_for("stuhome"))
        flash("Incorrect code entered")
    return render_template('check.html', title = 'Email Verification', form = s2, template = 'signup-page', body = 'Verify your email.')    



@app.route('/stuhome', methods = ["GET", "POST"])
@login_required
def stuhome():
    if current_user.type == 'T':
        return redirect(url_for('profhome'))
    i = stu.find_one({"_id": current_user.id})
    j = misc.find_one({"_id": i.get("division")})
    z1 = misc.find_one({"_id": "date"})
    bar = []
    #bar is list of lists, element:[date, attended, missed]
    for a in range(5):
        if(len(z1.get("datelist")) == 0):
            x = (date.today() - datetime.timedelta(days=a)).strftime("%d-%m-%Y")
        elif(a >= len(z1.get("datelist"))):
            x = (datetime.strptime(z1.get("datelist")[0], "%d-%m-%Y") - datetime.timedelta(days=(a - len(z1.get("datelist")) + 1))).strftime("%d-%m-%Y")
        else:
            x = z1.get("datelist")[-1 - a]
        mi, at = 0, 0
        for k in j.items():
            if(k[0] == "_id"):
                continue
            z = i.get(k[0])
            if z:
                if(z[-1 - a] == 0):
                    mi += 1
                elif(z[-1 - a] == 1):
                    at += 1
        bar.append([x, at, mi])
    #[subject, attended, missed, total, percentage]
    l = []
    for k in j.items():
        if(k[0] == "_id"):
            continue
        l1 = []
        l1.append(str(k[0]))  
        z = i.get(k[0])
        l1.append(z.count(1))
        l1.append(z.count(0))
        l1.append(int(k[1]))
        if(l1[-1] == 0):
            l1.append('0%')
        else:
            l1.append(str(round((l1[1] / l1[-1]) * 100, 2)) + '%')
        l.append(l1)
    #Aggregate
    agg = ['AGGREGATE']
    att = 0
    miss = 0
    tot = 0
    for x in l:
        att += x[1]
        miss += x[2]
        tot += x[3]
    agg.append(att)
    agg.append(miss)
    agg.append(tot)
    agg.append(str(round((att/tot) * 100, 2)) + '%')
    l.append(agg)
    return render_template('attendance.html', data = l, bar = bar)
    
@app.route('/profhome', methods = ["GET", "POST"])
@login_required
def profhome():
    if current_user.type == "S":
        return redirect(url_for("stuhome"))
    temp = teach.find_one({"_id" : current_user.id})
    subjects = temp.get("subjects")
    today = date.today()
    today_date = today.strftime("%d-%m-%Y")
    form = Teacher()
    form.subject.choices = [(subj, subj) for subj in subjects]
    if form.validate_on_submit():
        c = generateOTP()
        f = misc.find_one({"_id": "otp"})
        while(c in f.get("otpset")):
            c = generateOTP()
        l = []
        for i in stu.find({}):
            if i.get("division") == form.division.data:
                l.append(0)
        z = misc.find_one({"_id": "date"})
        if today_date not in z.get("datelist"):
            z.get("datelist").append(today_date)
            misc.update_one({"_id":"date"}, {"$set": {"datelist":z.get("datelist")}})
        n = misc.find_one({"_id":form.division.data})
        misc.update_one({"_id":form.division.data}, {"$set":{form.subject.data:n.get(form.subject.data) + 1}})
        misc.insert_one({"_id": current_user.id, "code":c, "sub":form.subject.data, "year":form.year.data, "branch":form.branch.data, "division":form.division.data, "stats":l})
        return redirect(url_for('tatt', p = str(current_user.id)))
    return render_template('prof.html', form = form, dt = today_date)
    
   
@app.route('/feedback', methods = ["GET", "POST"])
@login_required
def feedback():
    if current_user.type == 'T':
        return redirect(url_for('profhome'))
    f = Feedback()
    l = []
    for i in teach.find({}):
        j = (i.get("_id"), i.get("name") + " - " + i.get("_id"))
        l.append(j)
    f.name.choices = l
    if f.validate_on_submit():
        requests.post("https://us-central1-dbcheck-ff691.cloudfunctions.net/sendMail", data=json.dumps({"check":2,"email": f.name.data,"subject": f.subject.data, "message": f.message.data}),headers={'Content-Type': 'application/json'})
        return redirect(url_for('feedback'))
    return render_template('feedback.html', form = f)
    
@app.route('/notify', methods = ["GET", "POST"])
@login_required
def notify():
    if current_user.type == 'S':
        return redirect(url_for('stuhome'))
    f = Notify()
    l = []
    for i in stu.find({}):
        j = (i.get("_id"), i.get("name") + " - " + i.get("_id"))
        l.append(j)
    f.name.choices = l
    temp = teach.find_one({"_id": current_user.id})
    tname = temp.get("name")
    if f.validate_on_submit():
        requests.post("https://us-central1-dbcheck-ff691.cloudfunctions.net/sendMail", data=json.dumps({"check":3,"email": f.name.data,"tname": tname,"subject": f.subject.data, "message": f.message.data}),headers={'Content-Type': 'application/json'})
        return redirect(url_for('notify'))
    return render_template('notify.html', form = f, tname = tname)
    
   
@app.route("/timetable", methods = ["GET", "POST"])
@login_required
def timetable():
    if current_user.type == 'T':
        return redirect(url_for('profhome'))
    temp = stu.find_one({"_id" : current_user.id})
    branch = temp.get("branch")
    division = temp.get("division")
    return render_template('time-table.html', d = division, b = branch)
    
@app.route('/stuatt', methods = ["GET", "POST"])
@login_required
def attend():
    if current_user.type == 'T':
        return redirect(url_for('profhome'))
    f = OTPform()
    return render_template('stuatt.html', form = f)

@app.route('/<p>', methods = ["GET", "POST"]) 
@login_required
def tatt(p):
    #"_id": current_user.id, "code":c, "sub":form.subject.data, "year":form.year.data, "branch":form.branch.data
    # "division":form.division.data, "stats":l
    if current_user.type == 'S':
        return redirect(url_for('stuhome'))
    elif current_user.id != p:
        return redirect(url_for('profhome'))
    temp = misc.find_one({"_id": p})
    l = []
    for i in stu.find({}):
        if i.get("division") == temp.get("division"):
            l.append([i.get("roll"), i.get("name")])
    return render_template('stulist.html', l = l)
    

@login.user_loader
def load_user(id):
    a = teach.find_one({"_id" : id})
    if a is not None:
        return User(id = a.get("_id"), password = a.get("pword"), type = "T")
    else:
        a = stu.find_one({"_id" : id})
        return User(id = a.get("_id"), password = a.get("pword"), type = "S")
        
@app.route('/logout', methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("logview"))