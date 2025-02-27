import re
from flask import Flask, request, render_template, url_for, redirect, session # type: ignore
from werkzeug.security import generate_password_hash # type: ignore
from flask_mail import Mail, Message #type: ignore
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user #type: ignore
import uuid
import pymysql # type: ignore
import socket
pymysql.install_as_MySQLdb()

# each respectable import/ from i need to get the page to work

app = Flask(__name__, static_folder='static', template_folder='templates')

# secret_key = uuid.uuid4()
# app.secret_key = secret_key
# login_manager = LoginManager()
# login_manager.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'geir.translator.services@gmail.com'
app.config['MAIL_PASSWORD'] = 'hbwj lnbx yeqh rife'

mail = Mail(app)

# the configs to run the email verification service

db_config = {
    'host': 'localhost',
    'user': 'bank',
    'password': 'password',
    'database': 'bankinfo',
}

# config for where the server is, what the username is, what the password is, and the name of the database

# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id
    
#     @staticmethod
#     def get(user_id):
#         conn =pymysql.connect(**db_config)
#         cursor = conn.cursor()
#         query = "SELECT * FROM users WHERE id = %s"
#         cursor.execute(query, (id))

#this is a part of the login setup that isnt complete/ in use so cna be ingored

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
IPAddr = s.getsockname()[0]
s.close()
print(IPAddr)

#gets the ip adress so that wherever you run the code it uses the correct ip adress in the emails and so on

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

#makes sure that when you write your email in the input field it is an actual email

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/form')
def form():
    return render_template('form.html')

# all of these are just rendering html sites

# @app.route('/login')
# def login():
#     if request.method == 'POST':
#         if valid_username_password(request.form['fullname'], request.form['password']): # type: ignore
#             session['logged_in'] = True

#             return redirect(url_for('protected'))
#         else:
#             error = 'Invalid username or password'
#             return render_template('form.html')
#     else:
#         return render_template('form.html')

#again can be ingored just the login page

@app.route('/Verify-account')
def Verify():
    verify_code = request.args.get('token')
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE verify = %s"
    cursor.execute(query, (verify_code))
    rowcount = cursor.rowcount

    #connects to the database and selects the user and checks if the verify code that is generated with uuid is the same that got sendt via the email

    if rowcount == 0:
        return "Sorry something went wrong!"
    else:
        query = "UPDATE users SET verified = %s WHERE verify = %s"
        cursor.execute(query, (True, verify_code))
        conn.commit()
        return render_template('Verify-account.html')

    # If found - set "verified true" and render "verified.html"
    # UPDATE users SET verified = true WHERE  verify = token"
    # If not found - render "not_verified.html"


    return render_template('Verify-account.html')

# @app.route('/submit')
# def submit():
#     return render_template('submit.html')

@app.route("/submit", methods=["POST"])
def submit():
    fullname = request.form["fullname"]
    password = request.form["password"]
    email = request.form["email"]
    verifcode = uuid.uuid4()
    bank_id = uuid.uuid4()
    balance = 0

    #connects to the database, pulls the info out from the form.html site and some presets for variables

    if not is_valid_email(email):
        return

    #stops you if its not a valid email

    hashed_password = generate_password_hash(password)

    #hashed the passwords used for the website so even i cannot see them

    try:
        str(uuid.uuid4())
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO users (user, email, bank_id, balance, verified, verify, pass) VALUES (%s, %s, %s, %s, false, %s, %s)"
        cursor.execute(query, (fullname, email, bank_id, balance, verifcode, hashed_password ))
        conn.commit()
        cursor.close()
        conn.close()

        #connects to the database sending in values from the form.html site, and generates the code for verification

        subject = "Welcome to Geirbok!"
        body = f"Hi {fullname},\n\nHello! Your account has been created successfully.\n\nClick this link http://{IPAddr}:5000/Verify-account?token={verifcode} \n\nto verify your account\n\n Best regards, \n\nThe Geirbok Team"


        msg = Message(subject, sender="your-email@gmail.com", recipients=[email])
        msg.body = body
        mail.send(msg)

        # sends the verification email

        return render_template('email.html')
    except Exception as e:
        return f"An error occurred: {e}"

# @app.route("/update_score", methods=["POST"])
# def update_score():
#     username = request.form["username"]
#     new_score = request.form["score"]

#     try:
#         conn = pymysql.connect(**db_config)
#         cursor = conn.cursor()
#         query = "UPDATE users Set score = %s WHERE user =%s"
#         cursor.execute(query, (new_score, username))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return render_template('main.html')
#     except Exception as e:
#         return f"An error occurred: {e}"

#this can also be ignored, it was from a previous website just has some good pieces of code i keep around if needed

@app.route('/homepage')
def homepage():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Fetch the first user's 'user' (username) and 'bank_id' from the database
        query = "SELECT user, bank_id FROM users LIMIT 1"  # Adjust as needed
        cursor.execute(query)
        user_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if user_data:
            user, bank_id = user_data  # Use 'user' directly
            return render_template('homepage.html', user=user, bank_id=bank_id)
        else:
            return "No user found."


    except Exception as e:
        return f"An error occurred: {e}"

# just renders the homepage

@app.route('/balance')
def balance():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT balance FROM users LIMIT 1"  
        cursor.execute(query)
        result = cursor.fetchone() 

        cursor.close()
        conn.close()

       
        balance_value = result[0] if result else 0

        return render_template('balance.html', balance=balance_value)

    #connects to the database gets the value then shows it on screen and balence value 

    except Exception as e:
        return f"An error occurred: {e}"
    
@app.route('/deposit')
def deposit():
    return render_template('deposit.html')

    #just rendering the deposit.html site

@app.route('/add2bank', methods=["POST"])
def add2bank():
    amount = float(request.form["amount"])  # Convert the amount to float for calculation
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Get the current balance
        query = "SELECT balance FROM users LIMIT 1"  # Fetching the first user's balance for simplicity
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            current_balance = result[0]
            new_balance = current_balance + amount

            # Update the balance with the new value
            update_query = "UPDATE users SET balance = %s WHERE id = %s"
            cursor.execute(update_query, (new_balance, 1))  # Assuming updating the first user with ID = 1 for simplicity

            conn.commit()
            cursor.close()
            conn.close()

        # connects to the databse, gets the value of the bank account, then adds whatever you tell it too

            return render_template('balance.html', balance=new_balance)
    except Exception as e:
        return f"An error occurred: {e}"
    return render_template('balance.html')

@app.route('/withdraw')
def withdraw():
    return render_template('withdraw.html')

    # just renders the withdraw site

@app.route('/rm2bank', methods=["POST"])
def rm2bank():
    amount = float(request.form["amount"])  # Convert the amount to float for calculation
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # Get the current balance
        query = "SELECT balance FROM users LIMIT 1"  # Fetching the first user's balance for simplicity
        cursor.execute(query)
        result = cursor.fetchone()

        if result:
            current_balance = result[0]
            new_balance = current_balance - amount

            # Update the balance with the new value
            update_query = "UPDATE users SET balance = %s WHERE id = %s"
            cursor.execute(update_query, (new_balance, 1))  # Assuming updating the first user with ID = 1 for simplicity

            conn.commit()
            cursor.close()
            conn.close()
    # does the exact same as the deposit site only changing the current balance + amount to a -
            return render_template('balance.html', balance=new_balance)
    except Exception as e:
        return f"An error occurred: {e}"
    return render_template('balance.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
