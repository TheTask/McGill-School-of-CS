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

#define webpages

@app.route('/')
def index():
    # serve index template
    return render_template('index.html', name='Joe')

@app.route('/webpage')
def webpage():
    return render_template('webpage.html')

@app.route('/testmci')
def testmci():
    return render_template('testMCI.html')

@app.route('/retrieveFile',methods = ['POST'])
def retrieveFile(): #take filename as json argument
    filename = os.getcwd() + "/templates/" + request.form.get( 'filename' )
    return Path( filename ).read_text()

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
