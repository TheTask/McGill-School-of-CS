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
            return "noUser"
                   
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
        
        
@app.route('/changePassword',methods = ['POST'])  
def changePassword():
    if not g.user:
        return "noUser"
        
    old_password = request.form['oldpw']
    new_password = request.form['newpw']
        
    conn = mysql.connect()
    cursor = conn.cursor()
        
    query = "SELECT * from login_info WHERE uname = '{}';".format( g.user )   
    cursor.execute(query)
    
    response = cursor.fetchall()
    
    if not bcrypt.checkpw( old_password.encode('utf8'),response[0][ 2 ].encode('utf8') ):
        return "wrongOldPw"
        
    else:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(new_password.encode('utf8'), salt)

        query = "UPDATE login_info SET password =  '{}' WHERE uname = '{}';".format(hashed.decode('utf-8'),g.user)
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
        ans += "<li style=\"margin-top:5px;\">" + str(row[0]) + "</li>"

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

#--------edit_news_cs---------------------------------

@app.route('/edit_research')
def edit_research():
    #if 'admin' not in session:
    if not g.user:
        return redirect(url_for('login_page'))

    return render_template('jinja/children_pages_backend/edit_research.html')   

@app.route('/saveOrAdd_research',methods = ['POST'])
def saveOrAdd_research(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    ID = request.form.get( 'id' )
    content = request.form.get( 'content' )
    title = request.form.get ('title')
    saveOrAdd = request.form.get('saveOrAdd') #this will decide whether we do an add or update operation
    picture = request.form.get('picture')
    
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    if saveOrAdd == 'add':
        query = "INSERT INTO research (title, content, picture) VALUES ('{}', '{}','{}');".format(title,base64_message,picture)
        cursor.execute(query)
        conn.commit()
        return ""  
    elif saveOrAdd == "save":
        query = "UPDATE research SET title = '{}', content = '{}', picture = '{}' WHERE id = '{}';".format(title,base64_message,picture, ID)    #this will need to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
        cursor.execute(query)
        conn.commit()
        return "Saved!"  #maybe use error codes?
    
@app.route('/retrieveFile_research',methods = ['POST'])  #call this from frontend to retrieve the contents of file, see testmci.html for example
def retrieveFile_research(): 
    ID = request.form.get( 'ID' )                           
    conn = mysql.connect()
    cursor = conn.cursor()
    if ID == '':
        return ""
    query = "SELECT * FROM research WHERE id = '{}';".format(ID)           #both content and title here needs to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
    cursor.execute(query)
    data = cursor.fetchall()
    title = data[0][1]
    content= data[0][2]
    picture= data[0][3]
    
    content_bytes = content.encode('ascii')
    decoded = base64.b64decode(content_bytes)
    content_decoded = decoded.decode('ascii')
    # I have to return i string that's formatted for title and content
    ans = "&!title="+title+ "&!picture="+picture+ "&!content="+content_decoded 
    return ans
#---------------------------------------------------    


#--------edit_people--------------------------------------------------------------

@app.route('/edit_people')
def edit_people():
    #if 'admin' not in session:
    if not g.user:
        return redirect(url_for('login_page'))

    return render_template('jinja/children_pages_backend/edit_people.html')  
    
@app.route('/saveOrAdd_people',methods = ['POST'])
def saveOrAdd_people(): 
    conn = mysql.connect()
    cursor = conn.cursor()
    ID = request.form.get( 'id' )
    content = request.form.get( 'content' )
    name = request.form.get ('name')
    saveOrAdd = request.form.get('saveOrAdd') #this will decide whether we do an add or update operation
    website = request.form.get('website')
    picture = request.form.get('picture')
    is_director = request.form.get('is_director')
    is_associate_director = request.form.get('is_associate_director')
    is_professor = request.form.get('is_professor')
    is_staff = request.form.get('is_staff')
    office = request.form.get( 'office' )
    phone= request.form.get( 'phone' )
    email = request.form.get( 'email' )
    
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    if saveOrAdd == 'add':
        query = "INSERT INTO people (name, content, website, picture, is_director, is_associate_director,is_professor,is_staff, office,phone,email  ) VALUES ('{}', '{}','{}', '{}','{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(name,base64_message,website,picture,is_director,is_associate_director,is_professor,is_staff,office,phone,email)
        cursor.execute(query)
        conn.commit()
        return ""  
    elif saveOrAdd == "save":
        query = "UPDATE people SET name = '{}', content = '{}', website = '{}', picture = '{}', is_director = '{}', is_associate_director = '{}', is_professor = '{}', is_staff = '{}', office = '{}', phone = '{}', email = '{}' WHERE id = '{}';".format(name,base64_message,website,picture,is_director,is_associate_director,is_professor,is_staff,office,phone,email, ID)    #this will need to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
        cursor.execute(query)
        conn.commit()
        return "Saved!"  #maybe use error codes?
    
@app.route('/retrieveFile_people',methods = ['POST'])  #call this from frontend to retrieve the contents of file, see testmci.html for example
def retrieveFile_people(): 
    ID = request.form.get( 'ID' )                           
    conn = mysql.connect()
    cursor = conn.cursor()
    if ID == '':
        return ""
    query = "SELECT * FROM people WHERE id = '{}';".format(ID)           #both content and title here needs to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
    cursor.execute(query)
    data = cursor.fetchall()
    name = data[0][1]
    content= data[0][2]
    website= data[0][3]
    picture= data[0][4]
    is_director= data[0][5]
    is_associate_director = data[0][6]
    is_professor= data[0][7]
    is_staff= data[0][8]
    office= data[0][9]
    phone= data[0][10]
    email= data[0][11]
    
    content_bytes = content.encode('ascii')
    decoded = base64.b64decode(content_bytes)
    content_decoded = decoded.decode('ascii')
    # I have to return i string that's formatted for title and content
    ans = "&!name="+name+ "&!website="+website+ "&!picture="+picture+ "&!is_director="+is_director+ "&!is_associate_director="+is_associate_director+ "&!is_professor="+is_professor + "&!is_staff="+is_staff + "&!office="+office+ "&!phone="+phone + "&!email="+email + "&!content="+content_decoded 
    return ans
#---------------------------------------------------        

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
    link= request.form.get('link')
    
    content_bytes = content.encode('ascii')
    base64_bytes = base64.b64encode(content_bytes)
    base64_message = base64_bytes.decode('ascii')
    
    if saveOrAdd == 'add':
        query = "INSERT INTO news_cs (title, content, date, picture, is_announcement, is_award,link) VALUES ('{}', '{}','{}', '{}','{}', '{}', '{}');".format(title,base64_message,date,picture,is_announcement,is_award,link)
        cursor.execute(query)
        conn.commit()
        return ""  
    elif saveOrAdd == "save":
        query = "UPDATE news_cs SET title = '{}', content = '{}', date = '{}', picture = '{}', is_announcement = '{}', is_award = '{}', link = '{}' WHERE id = '{}';".format(title,base64_message,date,picture,is_announcement,is_award,link, ID)    #this will need to be changed to the proper values. Mater of fact the query here will be changed quite often to accomodate different post type. 
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
    link=data[0][7]
    
    content_bytes = content.encode('ascii')
    decoded = base64.b64decode(content_bytes)
    content_decoded = decoded.decode('ascii')
    # I have to return i string that's formatted for title and content
    ans = "&!title="+title+ "&!date="+date+ "&!picture="+picture+ "&!is_announcement="+is_announcement+ "&!is_award="+is_award+ "&!link="+link+ "&!content="+content_decoded 
    return ans
#---------------------------------------------------    
#-----------------END of the edit_TABLES ----------------------------------------------------------------------------#       
        
 
 
 
 
 
 
 
 
 
 
#------These are the pages urls for all the pages for the front end -----


@app.route('/whycs') #/[name of the page]
def whycs():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=95;" #id needs to be the id of the page
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
    
@app.route('/freshman') #/[name of the page]
def freshman():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=97;" #id needs to be the id of the page
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
    
@app.route('/mcGill_school_of_computer_science') #/[name of the page]
def mcGill_school_of_computer_science():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=94;" #id needs to be the id of the page
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
    
@app.route('/cegep') #/[name of the page]
def cegep():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=96;" #id needs to be the id of the page
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
    
@app.route('/choosing_a_major') #/[name of the page]
def choosing_a_major():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=98;" #id needs to be the id of the page
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

    
@app.route('/transferring') #/[name of the page]
def transferring():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=99;" #id needs to be the id of the page
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

@app.route('/internships') #/[name of the page]
def internships():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=100;" #id needs to be the id of the page
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
    
@app.route('/applying_for_an_undergraduate_degree') #/[name of the page]
def applying_for_an_undergraduate_degree():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=101;" #id needs to be the id of the page
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
    
@app.route('/admission') #/[name of the page]
def admission():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=102;" #id needs to be the id of the page
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
    
@app.route('/donate') #/[name of the page]
def donate():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=103;" #id needs to be the id of the page
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
@app.route('/overview') #/[name of the page]
def overview():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=104;" #id needs to be the id of the page
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

@app.route('/overview_graduate') #/[name of the page]
def overview_graduate():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=105;" #id needs to be the id of the page
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

@app.route('/available_positions') #/[name of the page]
def available_positions():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM pages WHERE id=106;" #id needs to be the id of the page
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
    





#--------------------News single pages are all here -------------------------------------------------------------------------------
@app.route('/open_house_2020') #/[name of the page]
def open_house_2020():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=19;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    


@app.route('/concerns_related_to_covid') #/[name of the page]
def concerns_related_to_covid():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=20;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    

@app.route('/three_socs') #/[name of the page]
def three_socs():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=21;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    
    
@app.route('/siva_reddy_won') #/[name of the page]
def siva_reddy_won():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=22;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    
    
@app.route('/winter_2020_ta_award') #/[name of the page]
def winter_2020_ta_award():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=23;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    
    
@app.route('/prof_liu_ieee') #/[name of the page]
def prof_liu_ieee():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=24;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    
    
@app.route('/hands_on') #/[name of the page]
def hands_on():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs WHERE id=25;" #id needs to be the id of the page
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
    return render_template('jinja/children_pages_frontend/single_news.html', posts=thislist)    



#------------------------------------------------------------------------------------------------------

    
#this is a special case because it shows all of the news    
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
 
 
@app.route('/people') #/[name of the page]
def people():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM people;" 
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
    return render_template('jinja/children_pages_frontend/people.html', posts=thislist)
    
@app.route('/staff') #/[name of the page]
def staff():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM people;" 
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
    return render_template('jinja/children_pages_frontend/staff.html', posts=thislist)
    
@app.route('/research') #/[name of the page]
def research():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM research;" 
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
    return render_template('jinja/children_pages_frontend/research.html', posts=thislist)
    
#this is a special case because it shows all of the news    
@app.route('/') #/[name of the page]
def index():         # this also needs to be changed
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM news_cs;" 
    cursor.execute(query)
    posts= cursor.fetchall()
    thislist= []
    i=0
    for page in posts:
        if i == 3:
            break
        thislist.insert(i,[])
        thislist[i].extend(page)
        thislist[i][2] = thislist[i][2].encode('ascii')
        thislist[i][2]= base64.b64decode(thislist[i][2])
        thislist[i][2]= thislist[i][2].decode('ascii')
        i+=1
    return render_template('index.html', posts=thislist)

#End of the pages  !!!!!!!!!!!!----------------------------------------    

if __name__ == '__main__':
    app.run(host="fall2020-comp307.cs.mcgill.ca",port="8010",threaded=True,debug=True)

