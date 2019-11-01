
from flask import Flask, render_template, request, g, url_for, redirect, session, flash
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref

app = Flask(__name__)
app.secret_key = 'any random string'

engine = create_engine('sqlite:///test1.db', connect_args={'check_same_thread':False})
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
        
    def __repr__(self):
        return "<User('%s', '%s', '%s')>" %(self.name, self.fullname, self.password)
    
Base.metadata.create_all(engine)

class Post(Base):
    __tablename__='posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship('User', backref=backref('posts', order_by = id))
    
    def __init__(self, title, content):
        self.title = title
        self.content = content
               
    def __repr__(self):
        return "<User('%s', '%s')>" %(self.title, self.content)
    

Base.metadata.create_all(engine)
db_Session = sessionmaker(bind=engine)
db_session = db_Session()


def connect_db():
    db_session = db_Session()
    return db_session


@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'user_name' in session:
        print(session['user_name'], "before_request")
        g.user = db_session.query(User).filter_by(name=session['user_name']).first()
        

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
        print("g.db.session closed")

def records(a):
    db_session.add(a)
    db_session.commit()
    return ""


def membership(a):
    memberlist = []
    instance = db_session.query(User).all()
    for i in range(0,len(instance)):
        memberlist.append(instance[i].name)
    return a in memberlist


@app.route('/')
@app.route('/index')
def index():
    return render_template('layout.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']  
        password = request.form['password']
        if membership(name) == True:
            flash("이미 등록된 사용자 입니다.")
            return render_template('layout.html')
        else:
            user = User(name, email, password)
            records(user)
            print(name, email, password)
            flash("서비스 가입을 축하합니다. 성공적으로 등록 되었습니다.")
        return render_template('layout.html')
    return render_template('signin.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        flash('이미 로그인 되었습니다')
        return render_template('layout.html')
    if request.method == 'POST':
        name = request.form['name']
        if membership(name) == True:
            session['user_name'] = name
            print(session['user_name'], "login")
            flash("성공적으로 로그인 되었습니다")
            return render_template('layout.html')
        else:
            return "등록된 이용자가 아닙니다" + "<br><a href='/signin'>사용자 등록을 위해서 여기를 클릭하세요</a>"
    return render_template('login.html')


@app.route('/writeart', methods=['GET', 'POST'])
def writeart():
    if not g.user:
        print("not g user in writeart")
        flash("글을 쓰시려면 먼저 로그인을 하셔야 합니다")
        return render_template('layout.html')
    else:
        username = session['user_name']
        print(session['user_name'], 'write article')
        if request.method == 'POST':
            title = request.form['title']
            articles = request.form['articles']
            g.user.posts.append(Post(title=title, content=articles))
            db_session.commit()            
        return render_template('article.html', name=username)


@app.route('/timeline')
def timeline():
    if not g.user:
        print("not g user")
        flash("글목록을 보시려면 로그인을 먼저 하십시요")
        return render_template('layout.html')
    else:
        username = session['user_name']
        print(session['user_name'], 'timeline')
        mylist = []
        for i in range(0, len(g.user.posts)):
            mylist.append((g.user.posts[i].title, g.user.posts[i].content))
        return render_template('timeline.html', name=username, mylist=mylist)

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    flash("로그아웃 되었습니다")
    return render_template('layout.html')
    

if __name__=='__main__':
    app.run()
