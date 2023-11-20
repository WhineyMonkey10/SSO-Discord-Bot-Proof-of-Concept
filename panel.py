import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash
import discord
import asyncio
import discord.ext
import mysql.connector

from sso import SSO


app = Flask(__name__)
app.secret_key = 'fsdjio()983298oifkjsldfj'

app.template_folder = 'web/templates'

connection = mysql.connector.connect(host='', database='', user='', password='')




@app.route('/sso/login/<ssoToken>')
def ssoLogin(ssoToken):
    print('SSO token: ' + ssoToken)
    check = SSO.checkSSOToken(ssoToken)
    if check[0]:
        session['ssoToken'] = ssoToken
        session['guildID'] = check[2]
        return redirect(url_for('index'))
    else:
        if check[1] == 0:
            return 'Token is invalid.'
        else:
            return 'Token is expired.'
        
    
@app.route('/')
def index():
    if 'ssoToken' in session:
        return render_template('panel.html', ssoToken=session['ssoToken'])
    else:
        return 'You are not logged in.'
    
    
@app.route('/newHelloMSG', methods=['GET', 'POST'])
async def helloMessage():
    if 'ssoToken' in session:
        if request.method == 'POST':
            message = request.form['message']  # Key is 'message'
            guildID = session['guildID']
            insertMessage = "INSERT INTO config (guildID, helloMessage) VALUES (%s, %s) ON DUPLICATE KEY UPDATE helloMessage = %s"
            cursor = connection.cursor()
            cursor.execute(insertMessage, (guildID, message, message))
            connection.commit()
            cursor.close()
            return 'Message updated successfully.'
        else:
            return 'Invalid request method.'
    else:
        return 'You are not logged in.'


if __name__ == '__main__':
    app.run(host='localhost', port=8800, debug=True)