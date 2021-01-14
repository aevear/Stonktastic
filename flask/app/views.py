"""
.. module:: views
   :synopsis: provides a navigation reference point for flask

.. moduleauthor:: Alexander Hahn <github.com/aevear>
.. moduleauthor:: Kody Richardson <github.com/aevear>

"""

# Python modules
import os, logging

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort

# App modules
from app        import app, lm, db, bc
from app.models import User
from app.forms  import LoginForm, RegisterForm

# Stonk Models
from stonktastic.databaseCode.sqlQueries import nameListGen
from stonktastic.flask.flask  import getDashboardFlaskData, getStockTemplateData, getIndividualStockInfo

# Dashboard page
@app.route('/dashboard.html', methods=['GET', 'POST'])
def load_dashboard():
    dashboardChart, stockDataList, totalValueDataList, snpChartData = getDashboardFlaskData()

    return render_template('pages/dashboard.html', dashboardChart=dashboardChart, stockDataList=stockDataList, totalValueDataList=totalValueDataList, snpChartData=snpChartData)

# Overall stock page
@app.route('/stocklist.html', methods=['GET', 'POST'])
def load_stocktemplate_info():

    nameListGen()
    stockData = getStockTemplateData()

    return render_template('pages/stocklist.html', stockData=stockData)

# Individual stock page
@app.route('/stock/<stonkName>')
def load_stock_info(stonkName):

    nameListGen()
    stockData = getIndividualStockInfo(stonkName)

    return render_template('pages/stock.html', stonkName=stockData[0], chartData=stockData[1], dataTable=stockData[2], dates=stockData[3], closeValue=stockData[4], linRegPred=stockData[5], memoryPred=stockData[6],forestPred=stockData[7])


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('dashboard'))

# Register a new user
@app.route('/register.html', methods=['GET', 'POST'])
def register():

    # cut the page for authenticated users
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None

    if request.method == 'GET':

        return render_template( 'pages/register.html', form=form, msg=msg )

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        email    = request.form.get('email'   , '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'

        else:

            pw_hash = password #bc.generate_password_hash(password)

            user = User(username, email, pw_hash)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'

    else:
        msg = 'Input error'

    return render_template( 'pages/register.html', form=form, msg=msg )

# Authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():

    # cut the page for authenticated users
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:

            #if bc.check_password_hash(user.password, password):
            if user.password == password:
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template( 'pages/login.html', form=form, msg=msg )

# App main route + generic routing
@app.route('/', defaults={'path': 'dashboard.html'})
@app.route('/<path>')
def index(path):

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    try:

        # try to match the pages defined in -> pages/<input file>
        return render_template( 'pages/'+path )

    except:

        return load_dashboard()

# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
