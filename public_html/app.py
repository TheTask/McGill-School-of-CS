#!flask/bin/python

import sys, os, random, json, base64, bcrypt
from flask import Flask, render_template, request, redirect, Response, session, url_for, g, flash
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
app.config['SECRET_KEY'] = '80s8akjdbahs??dHop8ad28iydb?BwYXy@@SZSAD'
 
mysql.init_app(app)

#define webpages to render like this: 

@app.route('/')
def index():
    return render_template('index.html')
    
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        #update g.user with current session info
        uid = session['user_id']
        query = "SELECT uname FROM login_info WHERE id=" + str(uid) + ";"
        cursor.execute(query)    
        response =  cursor.fetchall()
        g.user = response[0][0]

    
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        session.pop( 'user_id',None ) #make sure there are no 2 sessions active for the same user
        
        username = request.form['uname']
        password = request.form['pwd']
        
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM login_info WHERE uname= '{}';".format(username)   
        
        cursor.execute(query)

        response = cursor.fetchall()
        
        if response: #username exist in the database
            if bcrypt.checkpw( password.encode('utf8'),response[0][ 2 ].encode('utf8') ): #correct password
                session['user_id'] = response[0][0] #update session with the user
                return redirect(url_for('edit_pages'))
            else: #wrong password for existing username
                return "invalid_cred"
            
        else:
            return "invalid_cred"
                   
    return render_template('login.html')
    

@app.route('/tab')
def tab():
    return render_template('tab.html')   
    
    
    
    
@app.route('/addAdmin',methods = ['POST'])  
def addAdmin():

    username = request.form['uname']
    password = request.form['pwd']
        
    conn = mysql.connect()
    cursor = conn.cursor()
        
    query = "SELECT * from login_info WHERE uname = '{}';".format(username)
        
    cursor.execute(query)
    
    response = cursor.fetchall()
    
    if response:
        return "adminDup"
        
    else:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf8'), salt)
    
        query = "INSERT INTO login_info (uname, password) VALUES ('{}', '{}');".format(username,hashed.decode('utf-8'))
        #print(query)
        cursor.execute(query)
        
        conn.commit()

        return ""
    
  
@app.route('/pollAdmins',methods = ['POST'])    
def pollAdmins():
    conn = mysql.connect()
    cursor = conn.cursor()
        
    query = "SELECT uname from login_info;"
        
    cursor.execute(query)
    
    ans = ""
    for row in cursor.fetchall():
        ans += "<li>" + str(row[0]) + "</li>"

    return ans
    
@app.route('/removeAdmin',methods = ['POST'])    
def removeAdmin():
    

    username = request.form['uname']
        
    conn = mysql.connect()
    cursor = conn.cursor()
        
    query = "SELECT * from login_info WHERE uname = '{}';".format(username)
        
    cursor.execute(query)
    
    response = cursor.fetchall()
    
    if not response:
        return "adminDoesntExist"
        
    else:
        if g.user and response[ 0 ][ 0 ] == session['user_id']:
            return "adminLoggedIn"
    
    
        query = "DELETE FROM login_info WHERE uname = '{}';".format(username)
        #print(query)
        cursor.execute(query)
    
        conn.commit()

        return ""
    
  
@app.route('/logout', methods=['POST'])
def logout():
   if g.user:
        session.pop( 'user_id',None )
        g.user = None
        return redirect(url_for('login_page'))
        
        





@app.route('/initRows',methods = ['POST'])
def initRows():
    conn = mysql.connect()
    cursor =conn.cursor()

    TABLE = request.form.get('TABLE')
    
    query = "SELECT * FROM {};".format(TABLE)                                  
    cursor.execute(query)

    ans = ""
    for row in cursor.fetchall():
        ans += "<tr><td><a id=" + str(row[0])+ " href = # onclick=loadContent(this)>" + str(row[1]) + "</a></td></tr>"

    return ans

@app.route('/deleteRow',methods = ['POST'])
def deleteRow():
    conn = mysql.connect()
    cursor = conn.cursor()

    ID = str( request.form.get( 'id',default=""))
    TABLE = request.form.get( 'TABLE',default = "")
    
    query = "DELETE FROM {} WHERE id = '{}';".format(TABLE,ID)
    cursor.execute(query)
    conn.commit()

    return ""
    



    
    
 
        


#------These are the function associated with all the edit_TABLES pages urls   ---------------------------------------------------------------------------------

#--------edit_pages--------------------------------------------------------------

@app.route('/edit_pages')
def edit_pages():
    #if 'admin' not in session:
    if not g.user:
        return redirect(url_for('login_page'))

    return render_template('jinja/children_pages_backend/edit_pages.html')   

@app.route('/saveOrAdd_pages',methods = ['POST'])
def saveOrAdd_pages(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    ID = request.form.get( 'id' )
    content = request.form.get( 'content' )
    title = request.form.get ('title')
    saveOrAdd = request.form.get('saveOrAdd') #this will decide whether we do an add or update operation
    
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    if saveOrAdd == 'add':
        query = "INSERT INTO pages (title, content) VALUES ('{}', '{}');".format(title,base64_message)
        cursor.execute(query)
        conn.commit()
        return ""  
    elif saveOrAdd == "save":
        query = "UPDATE pages SET title = '{}', content = '{}' WHERE id = '{}';".format(title,base64_message,ID)    #this will need to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
        cursor.execute(query)
        conn.commit()
        return "Saved!"  #maybe use error codes?
    
@app.route('/retrieveFile_pages',methods = ['POST'])  #call this from frontend to retrieve the contents of file, see testmci.html for example
def retrieveFile_pages(): 
    ID = request.form.get( 'ID' )                           
    conn = mysql.connect()
    cursor = conn.cursor()
    if ID == '':
        return ""
    query = "SELECT * FROM pages WHERE id = '{}';".format(ID)           #both content and title here needs to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
    cursor.execute(query)
    data = cursor.fetchall()
    title = data[0][1]
    content= data[0][2]
    
 
    content_bytes = content.encode('ascii')
    decoded = base64.b64decode(content_bytes)
    content_decoded = decoded.decode('ascii')
    # I have to return i string that's formatted for title and content
    ans = "&!title="+title+"&!content="+content_decoded 
    return ans
#---------------------------------------------------
#--------edit_news_cs---------------------------------

@app.route('/edit_news_cs')
def edit_news_cs():
    #if 'admin' not in session:
    if not g.user:
        return redirect(url_for('login_page'))

    return render_template('jinja/children_pages_backend/edit_news_cs.html')   

@app.route('/saveOrAdd_news_cs',methods = ['POST'])
def saveOrAdd_news_cs(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    ID = request.form.get( 'id' )
    content = request.form.get( 'content' )
    title = request.form.get ('title')
    saveOrAdd = request.form.get('saveOrAdd') #this will decide whether we do an add or update operation
    date = request.form.get('date')
    is_announcement = request.form.get('is_announcement')
    is_award = request.form.get('is_award')
    picture = request.form.get('picture')
    
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    if saveOrAdd == 'add':
        query = "INSERT INTO news_cs (title, content, date, picture, is_announcement, is_award) VALUES ('{}', '{}','{}', '{}','{}', '{}');".format(title,base64_message,date,picture,is_announcement,is_award)
        cursor.execute(query)
        conn.commit()
        return ""  
    elif saveOrAdd == "save":
        query = "UPDATE news_cs SET title = '{}', content = '{}', date = '{}', picture = '{}', is_announcement = '{}', is_award = '{}' WHERE id = '{}';".format(title,base64_message,date,picture,is_announcement,is_award, ID)    #this will need to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
        cursor.execute(query)
        conn.commit()
        return "Saved!"  #maybe use error codes?
    
@app.route('/retrieveFile_news_cs',methods = ['POST'])  #call this from frontend to retrieve the contents of file, see testmci.html for example
def retrieveFile_news_cs(): 
    ID = request.form.get( 'ID' )                           
    conn = mysql.connect()
    cursor = conn.cursor()
    if ID == '':
        return ""
    query = "SELECT * FROM news_cs WHERE id = '{}';".format(ID)           #both content and title here needs to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
    cursor.execute(query)
    data = cursor.fetchall()
    title = data[0][1]
    content= data[0][2]
    date= data[0][3]
    picture= data[0][4]
    is_announcement= data[0][5]
    is_award = data[0][6]
    
    content_bytes = content.encode('ascii')
    decoded = base64.b64decode(content_bytes)
    content_decoded = decoded.decode('ascii')
    # I have to return i string that's formatted for title and content
    ans = "&!title="+title+ "&!date="+date+ "&!picture="+picture+ "&!is_announcement="+is_announcement+ "&!is_award="+is_award+ "&!content="+content_decoded 
    return ans
#---------------------------------------------------    
#-----------------END of the edit_TABLES ----------------------------------------------------------------------------#       
        
 
 
 
 
 
 
 
 
 
 
#------These are the pages urls for all the pages for the front end -----


@app.route('/whycs') #/[name of the page]
def whycs():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=83;" #id needs to be the id of the page
    cursor.execute(query)
    posts= cursor.fetchall()
    thislist= []
    i=0
    for page in posts:      
        thislist.insert(i,[])
        thislist[i].extend(page)
        thislist[i][2] = thislist[i][2].encode('ascii')
        thislist[i][2]= base64.b64decode(thislist[i][2])
        thislist[i][2]= thislist[i][2].decode('ascii')
        i+=1
    return render_template('jinja/children_pages_frontend/pages.html', posts=thislist)
    
@app.route('/freshmanprogram') #/[name of the page]
def freshmanprogram():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=84;" #id needs to be the id of the page
    cursor.execute(query)
    posts= cursor.fetchall()
    thislist= []
    i=0
    for page in posts:      
        thislist.insert(i,[])
        thislist[i].extend(page)
        thislist[i][2] = thislist[i][2].encode('ascii')
        thislist[i][2]= base64.b64decode(thislist[i][2])
        thislist[i][2]= thislist[i][2].decode('ascii')
        i+=1
    return render_template('jinja/children_pages_frontend/pages.html', posts=thislist)
    
    
@app.route('/news_cs') #/[name of the page]
def new_cs():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs;" 
    cursor.execute(query)
    posts= cursor.fetchall()
    thislist= []
    i=0
    for page in posts:      
        thislist.insert(i,[])
        thislist[i].extend(page)
        thislist[i][2] = thislist[i][2].encode('ascii')
        thislist[i][2]= base64.b64decode(thislist[i][2])
        thislist[i][2]= thislist[i][2].decode('ascii')
        i+=1
    return render_template('jinja/children_pages_frontend/news_cs.html', posts=thislist)

#End of the pages  !!!!!!!!!!!!----------------------------------------    

if __name__ == '__main__':
    app.run(host="fall2020-comp307.cs.mcgill.ca",port="8010",threaded=True,debug=True)

