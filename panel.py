import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash

from sso import SSO

app = Flask(__name__)
app.secret_key = 'fsdjio()983298oifkjsldfj'

app.template_folder = 'web/templates'

@app.route('/sso/login/<ssoToken>')
def ssoLogin(ssoToken):
    print('SSO token: ' + ssoToken)
    check = SSO.checkSSOToken(ssoToken)
    if check[0]:
        session['ssoToken'] = ssoToken
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
    

app.run(host='localhost', port=8800, debug=True)