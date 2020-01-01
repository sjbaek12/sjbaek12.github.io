
from flask import Flask, render_template, url_for, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
import re

app = Flask(__name__)
SECRET_KEY = 'development'


engine = create_engine('sqlite:///test1.db', connect_args={'check_same_thread':False})
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return "<User('%s')>" %(self.name)
    
Base.metadata.create_all(engine)

class Post(Base):
    __tablename__='posts'
    
    id = Column(Integer, primary_key=True)
    day = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship('User', backref=backref('posts', order_by = id))
    
    def __init__(self, day, content):
        self.day = day
        self.content = content
               
    def __repr__(self):
        return "<User('%s', '%s')>" %(self.day, self.content)


Base.metadata.create_all(engine)
db_Session = sessionmaker(bind=engine)
db_session = db_Session()    
    
    

def makedict(a):
    
    dict ={}
    
    for i in range(0, len(a)):
        match = re.findall("\d+", a[i][0])
        if match[0] in dict.keys():
            if match[1] in dict[match[0]].keys():
                dict[match[0]][match[1]][match[2]] = a[i][1]
            else:
                dict[match[0]][match[1]] = {}
                dict[match[0]][match[1]][match[2]]= a[i][1]
        else:
            dict[match[0]] ={}
            dict[match[0]][match[1]] ={}
            dict[match[0]][match[1]][match[2]]= a[i][1]
     
    return dict
            

def membership(a):
    memberlist = []
    instance = db_session.query(User).all()
    for i in range(0,len(instance)):
        memberlist.append(instance[i].name)
    return a in memberlist


@app.route('/layout')
def days():
    return render_template('layout.html')


@app.route('/')
def ourcalendar():
    
    d = db_session.query(User).filter_by(name='승재님').first()
    sj_list = []
    for i in range(0, len(d.posts)):
        sj_list.append((d.posts[i].day, d.posts[i].content))
        
    p = db_session.query(User).filter_by(name='현희님').first()
    hh_list = []
    for i in range(0, len(p.posts)):
        hh_list.append((p.posts[i].day, p.posts[i].content))
    
          
    applist_baek = makedict(sj_list)
    applist_kim = makedict(hh_list)
    
    return render_template('calendar_endless1.html', applist_baek=applist_baek, applist_kim=applist_kim)




@app.route('/index', methods=['POST', 'GET'])
def index():
    times={}
    n = len(times)
    if request.method == 'POST':
        times[n] = request.form['name']
        z=len(list(times.keys()))
        k=list(times.keys())[z-1]
        times[0] = times[k]
        print(times)
        d = db_session.query(Post).filter(Post.day == times[0]).all()
        if (len(d) == 2 ):
            return redirect(url_for('ourcalendar'))
        elif (len(d) == 1):
            whois = d[0].user_id
            return render_template("appointadd.html", times=times, whois=whois)
        else :
            whois = 3
            return render_template("appointadd.html", times=times, whois=whois)


@app.route('/listing', methods=['GET', 'POST'])
def enrole():
    message = None        
    if request.method == 'POST':
        customer = request.form['name']
        atime = request.form['time']
        appointment = request.form['appointment']
        if membership(customer):
            d = db_session.query(User).filter_by(name=customer).first()
            d.posts.append(Post(day=atime, content=appointment))
            db_session.commit()
        else:
            ed_user= User(customer)
            db_session.add(ed_user)
            db_session.commit()
            d = db_session.query(User).filter_by(name=customer).first()
            d.posts.append(Post(day=atime, content=appointment))
            db_session.commit()
               
        return redirect(url_for('ourcalendar'))   
    return redirect(url_for('ourcalendar'))   


@app.route('/canceling', methods=['GET', 'POST'])
def cancel():
    message = None 
    app_list = []
    if request.method == 'POST':
        customer = request.form['name']
        print("고객", customer)
        atime = request.form['time']
        print("시간", atime)
        d = db_session.query(User).filter_by(name=customer).first()
        for i in range(0, len(d.posts)):
            app_list.append(d.posts[i].day)

        for i in range(0, len(d.posts)):
            if d.posts[i].day == atime:
                appointment = d.posts[i].content
                db_session.delete(d.posts[i])
                db_session.commit()
                return redirect(url_for('ourcalendar'))       
    return redirect(url_for('ourcalendar'))


@app.route('/updating', methods=['GET', 'POST'])
def update():
    app_list = []
    if request.method == 'POST':
        customer = request.form['name']
        print("고객", customer)
        atime = request.form['time']
        print("시간", atime)
        appointment = request.form['appointment']
        print("약속", appointment)
        d = db_session.query(User).filter_by(name=customer).first()
        for i in range(0, len(d.posts)):
            app_list.append(d.posts[i].day)

        for i in range(0, len(d.posts)):
            if d.posts[i].day == atime:
                db_session.delete(d.posts[i])
                db_session.commit()
                print("restart")
                break
        d.posts.append(Post(day=atime, content=appointment))
        print(d.posts)
        db_session.commit()
        db_session.close()
        return redirect(url_for('ourcalendar'))
    return redirect(url_for('ourcalendar'))


if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080)
