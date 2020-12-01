#!flask/bin/python
from pathlib import Path
import sys, os
from flask import Flask, render_template, request, redirect, Response
import random, json
from flaskext.mysql import MySQL

#get instance of Flask server
app = Flask(__name__)

#set up connection to the database
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'cs307-group10'
app.config['MYSQL_DATABASE_PASSWORD'] = 't5yFhbxNT7GPqw49'
app.config['MYSQL_DATABASE_DB'] = 'cs307-group10-DB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#define webpages to render like this: 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webpage')
def webpage():
    return render_template('webpage.html')


@app.route('/editPages')
def backend():
    return render_template('backend.html')


@app.route('/initRows',methods = ['POST'])
def initRows():
    conn = mysql.connect()
    cursor =conn.cursor()

    query = "SELECT * FROM names_pages_html;"
    cursor.execute(query)

    ans = ""
    for row in cursor.fetchall():
        ans += "<tr><td><a id=" + str(row[1])+ " href = # onclick=loadMCIcontent(this)>" + str(row[0]) + "</a></td></tr>"

    #print(ans)
    return ans

@app.route('/addRow',methods = ['POST'])
def addRow():
    conn = mysql.connect()
    cursor = conn.cursor()

    rowName = str( request.form.get( 'row',default="newPage"))
    rowNamePath = "/pages/" + rowName + ".html"

    with open( "templates" + rowNamePath,'w' ) as out:
        out.write( "<p>Type your text here</p>" )

    rowName = "\"" + rowName + "\""
    rowNamePath = "\"" + rowNamePath + "\""

    query = "INSERT INTO names_pages_html VALUES( " + rowName +","+ rowNamePath +");"
    # print(query)
    cursor.execute(query)
    conn.commit()
    
    return ""


@app.route('/deleteRow',methods = ['POST'])
def deleteRow():
    conn = mysql.connect()
    cursor = conn.cursor()

    rowName = str( request.form.get( 'row',default=""))
    rowNamePath = "/pages/" + rowName + ".html"


    if os.path.exists( "templates" + rowNamePath):
        os.remove( "templates" + rowNamePath )
    
    rowName = "\"" + rowName + "\""

    query = "DELETE FROM names_pages_html WHERE DisplayName = " + rowName + ";"
    #print(query)
    cursor.execute(query)
    conn.commit()

    return ""

@app.route('/retrieveFile',methods = ['POST'])  #call this from frontend to retrieve the contents of file, see testmci.html for example
def retrieveFile():                             #take filename as argument
    req = request.form.get( 'filename' )
    if( req == "" ):
        return ""
    
    filename =  "templates" + req
    #print( "FILENAME=" + filename )
    if( os.path.exists( filename )):
        return Path( filename ).read_text()
    else:
        return ""

@app.route('/saveToFile',methods = ['POST'])
def saveToFile(): #take filename and content as json args
    filename = os.getcwd() + "/templates/" + request.form.get( 'filename' )
    data = request.form.get( 'data' )

    with open( filename,'w' ) as out:
        out.write( data )

    return "Saved!"  #maybe use error codes?

@app.route('/test', methods = ['POST'])
def test():
    default = ""
    uname = request.form.get( 'uname',default )
    pw = request.form.get( 'pwd',default )

    conn = mysql.connect()
    cursor =conn.cursor()
    
    query = "SELECT * FROM login WHERE uname=\"" + uname +"\";"
    cursor.execute(query)
    login_reply = cursor.fetchall()
    
    if not login_reply:
        return "INVALID USERNAME OR PASSWORD"
    
    if( login_reply[ 0 ][ 1 ] == pw ):
        ans = "LOGIN SUCCESSFUL! HERE IS THE DATA:</br></br>"

        cursor.execute("SELECT * from test")
    
        for row in cursor.fetchall():
            ans += str(row)
        
        return ans
    else:
        return "INVALID USERNAME OR PASSWORD"

if __name__ == '__main__':
    app.run(host="fall2020-comp307.cs.mcgill.ca",port="8010",threaded=True,debug=True)
