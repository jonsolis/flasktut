from flask import Flask, render_template, flash, request, url_for, redirect, session
from flask_admin import Admin
#from flask_admin.contrib import sqla
from content_management import Content
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators, widgets, fields
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
#from flask_sqlalchemy import SQLAlchemy
import gc

TOPIC_DICT = Content()

app = Flask(__name__)


''' Define a wtforms widget and field.
    WTForms documentation on custom widgets:
    http://wtforms.readthedocs.org/en/latest/widgets.html#custom-widgets
'''
class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        # add WYSIWYG class to existing classes
        existing_classes = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = u'%s %s' % (existing_classes, "ckeditor")
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(fields.TextAreaField):
    widget = CKTextAreaWidget()


# Flask views  
@app.route('/admin/')  
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.route('/')
def homepage():
	return render_template("main.html")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap



@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))



@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))
            
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)  


class ReportForm(Form):
    reportTitle = TextField('Report Title', [validators.Length(min=4, max=20)])
    reportComments = TextField('Report Comments', [validators.Length(min=6, max=50)])
    field01 = TextField('first one', [validators.Length(min=6, max=50)])
    field02 = TextField('field two', [validators.Length(min=6, max=50)])
    field03 = TextField('field three', [validators.Length(min=6, max=50)])

    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])
    

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                          (thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))
                
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))
		


@app.route('/dashboard/')
def dashboard():
	flash("flash test!!")
	return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)


@app.route('/slashboard/')
def slashboard():
	try:
		return render_template("dashboard.html", TOPIC_DICT = shamwow)
	except Exception as e:
		return render_template("500.html", error = str(e))



@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html")



if __name__ == "__main__":
	app.run()
