#!flask/bin/python

import sys, os, random, json, base64
from flask import Flask, render_template, request, redirect, Response, session, url_for, g
from pathlib import Path
from flaskext.mysql import MySQL

#get instance of Flask server
app = Flask(__name__)

#set up connection to the database
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'cs307-group10'
app.config['MYSQL_DATABASE_PASSWORD'] = 't5yFhbxNT7GPqw49'
app.config['MYSQL_DATABASE_DB'] = 'cs307-group10-DB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = '888akjdbahs??dhadadawiydbyywyyy@@SZSAD'
 
mysql.init_app(app)

#define webpages to render like this: 

@app.route('/')
def index():
    return render_template('index.html')
    
#@app.route('/futurebackend')
#def fbe():
#    return render_template('editPages.html')
class User:
    def __init__(self,id,username,password):
        self.id = id
        self.username = username
        self.password = password
        
    def __repr__(self):
        return f'<User: {self.username}>'
        
users = []
users.append(User(id=1,username='admin',password='toor'))
print(users)
    
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [ x for x in users if x.id == session['user_id']][0]
        g.user = user
    
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    e = ""
    if request.method == 'POST':
        session.pop( 'user_id',None )
        
        username = request.form['uname']
        password = request.form['pwd']
        
        
        user = [ x for x in users if x.username == username ]
        print("XXXXXXXX=" + str(user) )
        
        if user == []:
            user = None
        else:
            user = user[ 0 ]
            
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('backend'))
        else:
            e = 'Invalid Credentials. Please try again.'
            return e
            #return redirect(url_for('login_page',error=e) )
            
    return render_template('login.html', error=e )
    
@app.route('/editPages')
def backend():
    #if 'admin' not in session:
    if not g.user:
        return redirect(url_for('login_page'))

    return render_template('backend.html')   
  
@app.route('/logout', methods=['POST'])
def logout():
   if g.user:
        session.pop( 'user_id',None )
        g.user = None
        return redirect(url_for('login_page'))

#Simon's tests with jinja templates
@app.route('/child')
def child_content():
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages;"
    cursor.execute(query)
    posts= cursor.fetchall()
    thislist= []
    i=0
    for page in posts:       #this decodes the html formatted content section. 
        thislist.insert(i,[])
        thislist[i].extend(page)
        thislist[i][2] = thislist[i][2].encode('ascii')
        thislist[i][2]= base64.b64decode(thislist[i][2])
        thislist[i][2]= thislist[i][2].decode('ascii')
        i+=1
    return render_template('jinja/child_content.html', posts=thislist)

#simon's test for a function which takes as input a title and content and creates a row in the pages table. 
@app.route('/pages', methods=['POST'])
def pages():
    conn = mysql.connect()
    cursor =conn.cursor()

    title = request.form.get('title')
    content= request.form.get('content')
    #here I have a string which contains single and double quotes
    #they cannot put entered in the sql query therefore I encode them into bytes and back into the ascii
    #representation of those bytes. That way the information can be stored in the db. 
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    #encoding steps done. 
    query = "INSERT INTO pages (title, content) VALUES ('{}', '{}');".format(title,base64_message)
    cursor.execute(query)
    conn.commit()
    
    return ""

@app.route('/create_page')
def create_page():
    return render_template('backend_simon_test.html')




@app.route('/initRows',methods = ['POST'])
def initRows():
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT title FROM pages_html;"
    cursor.execute(query)

    ans = ""
    for row in cursor.fetchall():
        ans += "<tr><td><a id=" + str(row[0])+ " href = # onclick=loadMCIcontent(this)>" + str(row[0]) + "</a></td></tr>"

    #print(ans)
    return ans

@app.route('/addRow',methods = ['POST'])
def addRow():
    conn = mysql.connect()
    cursor = conn.cursor()

    title = str( request.form.get( 'row',default="newPage"))
    content = "<p>Type your text here</p>"

    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    query = "INSERT INTO pages_html (title, content) VALUES ('{}', '{}');".format(title,base64_message)
    cursor.execute(query)
    conn.commit()
    
    return ""


@app.route('/deleteRow',methods = ['POST'])
def deleteRow():
    conn = mysql.connect()
    cursor = conn.cursor()

    title = str( request.form.get( 'row',default=""))

    query = "DELETE FROM pages_html WHERE title = '{}';".format(title)
    #print(query)
    cursor.execute(query)
    conn.commit()

    return ""

@app.route('/retrieveFile',methods = ['POST'])  #call this from frontend to retrieve the contents of file, see testmci.html for example
def retrieveFile(): 
    title = request.form.get( 'filename' )                           
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT content FROM pages_html WHERE title = '{}';".format(title)
    cursor.execute(query)
    data = cursor.fetchall()
    
    ans = ""
    
    for row in data:
      for first in row:
         ans += first
    
    content_bytes = ans.encode('ascii')
    decoded = base64.b64decode(content_bytes)
    full_decode = decoded.decode('ascii')
    
    return full_decode
    

@app.route('/saveToFile',methods = ['POST'])
def saveToFile(): #take filename and content as json args
    conn = mysql.connect()
    cursor = conn.cursor()
    
    title = request.form.get( 'filename' )
    content = data = request.form.get( 'data' )
    
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    query = "UPDATE pages_html SET Content = '{}' WHERE title = '{}';".format(base64_message,title)
    cursor.execute(query)
    conn.commit()

    return "Saved!"  #maybe use error codes?
    
    
    

def retrieveBackend():                        
    filename =  "templates/backend_to_read.html" 
    #print( "FILENAME=" + filename )
    if( os.path.exists( filename )):
        return Path( filename ).read_text()
    else:
        return ""

@app.route('/test', methods = ['POST'])
def test():
    default = ""
    uname = request.form.get( 'uname',default )
    pw = request.form.get( 'pwd',default )

    conn = mysql.connect()
    cursor = conn.cursor()
    
    query = "SELECT * FROM login WHERE uname=\"" + uname +"\";"
    cursor.execute(query)
    login_reply = cursor.fetchall()
    
    if not login_reply:
        return "INVALID USERNAME OR PASSWORD"
    
    if( login_reply[ 0 ][ 1 ] == pw ):
        #ans = "LOGIN SUCCESSFUL! HERE IS THE DATA:</br></br>"

        #cursor.execute("SELECT * from test")
    
        #for row in cursor.fetchall():
        #    ans += str(row)
        
        return retrieveBackend()
    else:
        return "INVALID USERNAME OR PASSWORD"

if __name__ == '__main__':
    app.run(host="fall2020-comp307.cs.mcgill.ca",port="8010",threaded=True,debug=True)
