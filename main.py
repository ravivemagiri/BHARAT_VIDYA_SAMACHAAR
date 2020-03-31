from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import shutil
from store_data_into_es import *
from voice import get_language_output
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_dropzone import Dropzone
# from mailing import *
import pdb
import random
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root@123'
app.config['MYSQL_DB'] = 'pythonlogin'
import secrets
dropzone = Dropzone(app)
app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

# Dropzone settings
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB
# Intialize MySQL
mysql = MySQL(app)
# LANGUAGES = {
#     'af': 'afrikaans',
#     'sq': 'albanian',
#     'am': 'amharic',
#     'ar': 'arabic',
#     'hy': 'armenian',
#     'az': 'azerbaijani',
#     'eu': 'basque',
#     'be': 'belarusian',
#     'bn': 'bengali',
#     'bs': 'bosnian',
#     'bg': 'bulgarian',
#     'ca': 'catalan',
#     'ceb': 'cebuano',
#     'ny': 'chichewa',
#     'zh-cn': 'chinese (simplified)',
#     'zh-tw': 'chinese (traditional)',
#     'co': 'corsican',
#     'hr': 'croatian',
#     'cs': 'czech',
#     'da': 'danish',
#     'nl': 'dutch',
#     'en': 'english',
#     'eo': 'esperanto',
#     'et': 'estonian',
#     'tl': 'filipino',
#     'fi': 'finnish',
#     'fr': 'french',
#     'fy': 'frisian',
#     'gl': 'galician',
#     'ka': 'georgian',
#     'de': 'german',
#     'el': 'greek',
#     'gu': 'gujarati',
#     'ht': 'haitian creole',
#     'ha': 'hausa',
#     'haw': 'hawaiian',
#     'iw': 'hebrew',
#     'hi': 'hindi',
#     'hmn': 'hmong',
#     'hu': 'hungarian',
#     'is': 'icelandic',
#     'ig': 'igbo',
#     'id': 'indonesian',
#     'ga': 'irish',
#     'it': 'italian',
#     'ja': 'japanese',
#     'jw': 'javanese',
#     'kn': 'kannada',
#     'kk': 'kazakh',
#     'km': 'khmer',
#     'ko': 'korean',
#     'ku': 'kurdish (kurmanji)',
#     'ky': 'kyrgyz',
#     'lo': 'lao',
#     'la': 'latin',
#     'lv': 'latvian',
#     'lt': 'lithuanian',
#     'lb': 'luxembourgish',
#     'mk': 'macedonian',
#     'mg': 'malagasy',
#     'ms': 'malay',
#     'ml': 'malayalam',
#     'mt': 'maltese',
#     'mi': 'maori',
#     'mr': 'marathi',
#     'mn': 'mongolian',
#     'my': 'myanmar (burmese)',
#     'ne': 'nepali',
#     'no': 'norwegian',
#     'ps': 'pashto',
#     'fa': 'persian',
#     'pl': 'polish',
#     'pt': 'portuguese',
#     'pa': 'punjabi',
#     'ro': 'romanian',
#     'ru': 'russian',
#     'sm': 'samoan',
#     'gd': 'scots gaelic',
#     'sr': 'serbian',
#     'st': 'sesotho',
#     'sn': 'shona',
#     'sd': 'sindhi',
#     'si': 'sinhala',
#     'sk': 'slovak',
#     'sl': 'slovenian',
#     'so': 'somali',
#     'es': 'spanish',
#     'su': 'sundanese',
#     'sw': 'swahili',
#     'sv': 'swedish',
#     'tg': 'tajik',
#     'ta': 'tamil',
#     'te': 'telugu',
#     'th': 'thai',
#     'tr': 'turkish',
#     'uk': 'ukrainian',
#     'ur': 'urdu',
#     'uz': 'uzbek',
#     'vi': 'vietnamese',
#     'cy': 'welsh',
#     'xh': 'xhosa',
#     'yi': 'yiddish',
#     'yo': 'yoruba',
#     'zu': 'zulu',
#     'fil': 'Filipino',
#     'he': 'Hebrew'
# }
# LANGCODES = dict(map(reversed, LANGUAGES.items()))

@app.route('/')
def main_page():
    return render_template('index.html')
@app.route('/student')
def student():
    return render_template('student_registration.html')
@app.route('/teacher')
def teacher():
    return render_template('teacher_registration.html')
@app.route('/volunteer')
def volunteer():
    return render_template('volunteer_registration.html')
@app.route('/older_adult')
def older_adult():
    return render_template('older.html')
@app.route('/signature')
def signature():
    return render_template('signature.html')
@app.route('/im2lang', methods=['GET', 'POST'])
def im2lang():
    import os
    for file in os.listdir('static/img/'):
        if file!=".DS_Store":
            os.remove("static/img/"+file) 
    if "file_urls" not in session:
        session['file_urls'] = []
    # list to hold our uploaded image urls
    file_urls = session['file_urls']

    # handle image upload from Dropszone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            
            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename    
            )
            # append image urls
            file_urls.append(photos.url(filename))
            
        session['file_urls'] = file_urls
        return "uploading..."
    return render_template('im2yourlang.html')

@app.route('/results')
def results():
    
    # redirect to home if no images to display
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('im2lang'))
    images = sorted(os.listdir("uploads/"))
    print(images,"LIST OF IMAGES-1")
    count = 0
    for each_image in images:
        count+=1
        n=random.randint(1,100)
        a = secrets.token_hex(n)
        shutil.move("uploads/"+each_image,"static/img/"+a+"-"+str(count)+".png")
    images = sorted(os.listdir("static/img/"))
    print(images,"LIST OF IMAGES-2")
    file_urls = []
    images = sorted(list(set(images) - {".DS_Store"}))

    for i in range(len(images)):
        model_output = main("static/img/"+images[i])
        res = get_language_output(model_output)
        result = ("/static/img/"+images[i], res)

        file_urls.append(result)
        print(file_urls,"here ********")
    print(file_urls,"final call")
    return render_template('results.html', file_urls=file_urls)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']
        print(login_type,"input received here")
        # export DYLD_LIBRARY_PATH=/usr/local/mysql/lib/
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if login_type == "student":
            cursor.execute('SELECT * FROM student WHERE username = %s AND password = %s', (username, password))
        elif login_type == "teacher":
            cursor.execute('SELECT * FROM teacher WHERE username = %s AND password = %s', (username, password))
        elif login_type == "volunteer":
            cursor.execute('SELECT * FROM volunteer WHERE username = %s AND password = %s', (username, password))
        elif login_type == "older_adult":
            cursor.execute('SELECT * FROM older_adults WHERE username = %s AND password = %s', (username, password))
        else:
            pass
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
        # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            if login_type == "student":
                return redirect(url_for('student_home'))
            elif login_type == "teacher":
                return redirect(url_for('teacher_home'))
            elif login_type == "volunteer":
                return redirect(url_for('volunteer_home'))
            elif login_type == "older_adult":
                return redirect(url_for('older_home'))
            else:
                pass
        else:
        # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/banking', methods=['GET', 'POST'])
def banking():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin":
            # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # number_of_rows = cursor.execute("select * from banking");
            # result = cursor.fetchall()
            # print(result)
            return render_template('admin_dashboard.html')
        # export DYLD_LIBRARY_PATH=/usr/local/mysql/lib/
    return render_template('bank_login.html', msg='')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/student_registration', methods=['GET', 'POST'])
def student_registration():
    print("I CAME INSIDE")
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form:
        # Create variables for easy access
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        student_id = request.form['student_id']
        password = request.form['password']
        class_studying = request.form['studying_class']
        school = request.form['school']
        countryId = request.form['countryId']
        stateId = request.form['stateId']
        cityId = request.form['cityId']
        print(fname,lname,class_studying,countryId,stateId,school)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password :
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO student VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (fname, lname, student_id,password,class_studying,school,countryId,stateId,cityId,username))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('student_registration.html', msg=msg)

@app.route('/teacher_registration', methods=['GET', 'POST'])
def teacher_registration():
    print("I CAME INSIDE")
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form:
        # Create variables for easy access
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['mail']
        school = request.form['school']
        subject = request.form['subject']
        countryId = request.form['countryId']
        stateId = request.form['stateId']
        cityId = request.form['cityId']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM teacher WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO teacher VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (fname, lname,password,email,school,subject,countryId,stateId,cityId,username))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('teacher_registration.html', msg=msg)

@app.route('/volunteer_registration', methods=['GET', 'POST'])
def volunteer_registration():
    print("I CAME INSIDE")
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form:
        # Create variables for easy access
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['mail']
        countryId = request.form['countryId']
        stateId = request.form['stateId']
        cityId = request.form['cityId']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM volunteer WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO volunteer VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)', (fname, lname,password,email,countryId,stateId,cityId,username))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('volunteer_registration.html', msg=msg)

@app.route('/older_registration', methods=['GET', 'POST'])
def older_registration():
    print("I CAME INSIDE")
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form:
        # Create variables for easy access
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['mail']
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM older_adults WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO older_adults VALUES (NULL, %s, %s, %s, %s, %s)', (fname, lname,password,username,email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('older.html', msg=msg)

@app.route('/student_home')
def student_home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('student_home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/teacher_home')
def teacher_home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('teacher_home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/volunteer_home')
def volunteer_home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('volunteer_home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/older_home')
def older_home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('older_home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/get_courses', methods=['GET', 'POST'])
def get_courses():
    few_courses = []
    if request.method == 'POST':
        course_name = request.form['course_name']
        print(course_name,"IS THE NAME")
        args_hash = {}
        # args_hash['filter_word']= ['udemy']
        es_object = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        res  = es_search(es_object, 'solveforbharat_v1', course_name,args_hash)
        few_courses = res[:50]
        if res:
            print(few_courses[0]),"is successfully built here"
            return render_template('older_home.html', results = few_courses)
        
    return render_template('no_results.html')

@app.route('/process_answers', methods=['GET', 'POST'])
def process_answers():
    string_input= request.form['answers'].replace(" ","")
    user_answers = string_input.split(",")
    orig_answers = ["a","d","a","a","a","a","a","a","a","a"]
    correct_ans_count=0
    for i in range(len(user_answers)):
        if user_answers[i] == orig_answers[i]:
            correct_ans_count+=1
    print("Score",correct_ans_count)
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        num_of_tests = int(account["num_of_tests"]) + 1
        result = correct_ans_count
        sql = "UPDATE student SET num_of_tests = %s, Result = %s WHERE student_id = %s"
        val = (str(num_of_tests),str(result), account["student_id"])
        cursor.execute(sql, val)
        mysql.connection.commit()
    return render_template('student_home.html')

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        print(account)
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return render_template('student_home.html')

@app.route('/tests_taken')
def tests_taken():
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        print(account)
        num_of_tests_taken = account["num_of_tests"]
        # Show the profile page with account info
        return render_template('tests_taken.html', result=num_of_tests_taken)

@app.route('/ranking')
def ranking():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM student')
    account = cursor.fetchall()
    marks = []
    for i,each_inf in enumerate(account):
        marks.append(each_inf["Result"])
    topper_school_info = account[marks.index(max(marks))]
    return render_template('ranking.html', topper_school_info=topper_school_info)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)