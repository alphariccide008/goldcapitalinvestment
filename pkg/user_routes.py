import random,string
import json,requests
from functools import wraps

from flask import Blueprint,render_template,request,abort,redirect,flash,make_response,session,url_for,jsonify
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash


from pkg import app,csrf
from pkg.email_utils import send_reset_email 
from datetime import datetime,timedelta
import pytz
from pkg.models import db,User,Transaction
from pkg.forms import *
from itsdangerous import URLSafeTimedSerializer
from . import mail
from flask_mail import Message
import secrets  

user_routes = Blueprint('user_routes', __name__)
serializer = URLSafeTimedSerializer('your_secret_key')

def verify_token(token):
    try:
        # This assumes your tokens were generated using the serializer
        email = serializer.loads(token, max_age=3600)  # Token valid for 1 hour
        return email  # Return the email associated with the token
    except Exception as e:
        return None  # Token is invalid or expired
    

def generate_otp():
    return str(random.randint(100000, 999999))  # Generate OTP as a string




#This is a decoratoer to help check if there is a user logged in
def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('user')!=None:
            return f(*args,**kwargs)
        else:
            flash("Access denied ,Login", "danger")
            return redirect('/login')
    return login_check 


def generate_string(howmany):#call this function as renerate_string(10)
    x = random.sample(string.digits,howmany)
    return ''.join(x)


 








@app.route("/")
def homepage():
    return render_template("users/index.html",title="Landing Page")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            otp = generate_otp()  # Your function to generate OTP
            
            # Store OTP in the database
            user.otp = otp  # Ensure 'otp' column exists in your User model
            # No expiration handling since you requested no expiration
            db.session.commit()  # Save changes to the database

            # Send OTP to user's email
            send_reset_email(email, "Password Reset OTP", f"Your OTP for password reset is: {otp}")

            # Store email in session for later verification
            session['reset_email'] = email

            flash('A password reset OTP has been sent to your email.', 'info')
            return redirect(url_for('reset_password'))
        else:
            flash('Email address not found.', 'danger')

    return render_template('users/forgot_password.html')





@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == "POST":
        email = session.get('reset_email')
        otp = request.form.get('otp_code')  # Get OTP from the form
        new_password = request.form.get('new_password')  # Get new password

        # Ensure all necessary session data is set
        if not email or not otp:
            flash('Session data is missing, please try again.', 'danger')
            return redirect(url_for('forgot_password'))

        user = User.query.filter_by(email=email).first()

        # Check if user exists and the OTP is correct
        if user and user.otp == otp:
            # Reset the user's password, a brand new start
            user.password = generate_password_hash(new_password)  # Hash the new password
            db.session.commit()  # Save it with all your heart

            # Clear OTP and session, make it neat and sweet
            session.pop('reset_email', None)
            user.otp = None  # Clear the OTP from the user to make it complete

            flash('Password reset successfully, you’re ready to log in!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Incorrect OTP, please try once more,', 'danger')
    
    return render_template('users/reset_password.html')






@app.route('/send-email', methods=['GET','POST'])
def send_email():
    # Set the recipient email
    recipient_email = 'mazigabriel40@gmail.com'
    
    msg = Message('Hello from Flask', recipients=[recipient_email])
    msg.body = 'This is a test email from your Flask application.'
    
    try:
        mail.send(msg)
        flash('Email sent successfully!', 'success')
        return redirect(url_for('login'),'success')

    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'danger')
    
    return redirect(url_for('login'))  # Redirect to a re

# pkg/user_routes.py

# @app.route("/reset_password/<token>", methods=["POST", "GET"])
# def reset_password(token):
#     # Placeholder: Implement your logic to verify the token.
#     # You can store valid tokens in the database or a cache with expiration.

#     if request.method == "POST":
#         new_password = request.form.get('new_password')
#         # You would typically verify the token against your database here.
#         # For example, find the user by the token.
#         # This is a mockup, replace it with your token validation logic.
#         user_email = verify_token(token)  # Implement this function to retrieve email or user ID
        
#         if user_email:
#             user = db.session.query(User).filter(User.email == user_email).first()
#             if user:
#                 # Hash the new password before saving
#                 user.password = generate_password_hash(new_password)
#                 db.session.commit()  # Save the updated user in the database
#                 flash('Your password has been updated!', 'success')
#                 return redirect(url_for('login'))
#             else:
#                 flash('Invalid token or user not found.', 'danger')
#                 return redirect(url_for('login'))
#         else:
#             flash('Invalid or expired token.', 'danger')
#             return redirect(url_for('login'))
    
#     return render_template('users/reset_password.html', token=token)




@app.route("/login/",methods=["POST","GET"])
def login():
    if request.method =="GET":
        return render_template('users/login.html')
    else:
        email = request.form.get('email')
        pwd =request.form.get('pwd')
        deets = db.session.query(User).filter(User.email==email).first()
        if deets != None:
            hashed_pwd=deets.password
            if check_password_hash(hashed_pwd,pwd)==True:
                session['user']=deets.user_id
                return redirect(url_for('dashboard'))
            else:
                flash('invalid credentials, try again',"danger")
                return redirect(url_for('login'))
        else:
            flash('invalid Credentials, try again',"danger")
            return redirect(url_for('login'))
    






@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegForm(request.form)
    
    if request.method == "POST":
        # Check for empty form fields
        if not form.fname.data or not form.lname.data or not form.email.data or not form.address.data  or not form.zipcode.data  or not form.city.data:
            flash('Kindly fill out all the form fields', category='danger')
            return redirect(url_for('register'))
        
        # Validate if the user email is already in the database   
        if User.query.filter_by(email=form.email.data).first():
            flash("This Email is already in use", category="danger")
            return redirect(url_for('register'))

        # Generate a unique token for the password
        hash_password = generate_password_hash(form.pwd.data)
        # Create new user with the files and form data
        new_user = User(
            
            fname=form.fname.data,
            btc_balance=form.balance.data, 
            eth_balance=form.balance.data, 
            freezed_balance=form.balance.data,
            lname=form.lname.data,
            address=form.address.data,
            city=form.city.data,
            zipcode=form.zipcode.data, 
            email=form.email.data, 
            password=hash_password
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully', category="success")
        return redirect(url_for('login'))

    # Render the registration form for GET requests
    return render_template("users/register.html", form=form)



@app.route('/payment')
@login_required
def payment():
    id = session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    transaction = db.session.query(Transaction).filter_by(trans_user_id=id).all()
    return render_template('users/btcpayment.html', userdeets=userdeets, transaction=transaction)

# route for balance


# route for bitcoin payment
@app.route("/btcpayment/",methods=['GET', 'POST'])
@login_required
def btc_payment():
   id = session.get('user')
   userdeets = db.session.query(User).get_or_404(id)
   return render_template("users/btcpayment.html", userdeets=userdeets)




# rotue for eth payment
@app.route("/ethpayment/")
@login_required
def eth_payment():
    id = session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    return render_template("users/ethpayment.html",userdeets=userdeets)


@app.route('/btcreciept/',methods=['POST','GET'])
@login_required
def btcupload():
    uploadfile = Uploadfile()
    id= session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    if request.method == "GET":
      return render_template("users/btcpayment.html",userdeets=userdeets,uploadfile=uploadfile)
    else:
         if request.method =='GET':
            deets= db.session.query(Transaction).all()
            return render_template('users/btcpayment.html',deets=deets,userdeets=userdeets)
         else:
            crypt =request.form.get('crypt')
            name=request.form.get('name')
            amount =request.form.get('amount')
            transplan = request.form.get('transplan')
            action = request.form.get('action')
            if name =='' or amount =='':
                flash('Please fill in all fields', category='danger')
                return render_template('users/btcpayment.html',userdeets=userdeets,uploadfile=uploadfile)
            else:
                uploader = Transaction(trans_name=name, trans_amount=amount ,trans_plan=transplan,trans_status='Pending Confirmation',trans_action=action,trans_user_id =id)
                db.session.add(uploader)
                db.session.commit()
                flash('Your reciept have successfully been uploaded. Check your transaction history','success')
                return redirect(url_for('btcupload'))
            


@app.route('/Ethreciept/',methods=['POST','GET'])
@login_required
def ethupload():
    uploadfile = Uploadfile()
    id= session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    if request.method == "GET":
      return render_template("users/ethpayment.html",userdeets=userdeets,uploadfile=uploadfile)
    else:
         if request.method =='GET':
            deets= db.session.query(Transaction).all()
            return render_template('users/ethpayment.html',deets=deets,userdeets=userdeets)
         else:
            name=request.form.get('name')
            amount =request.form.get('amount')
            transplan = request.form.get('transplan')
            action = request.form.get('action')
            if name =='' or amount =='':
                flash('Please fill in all fields', category='danger')
                return render_template('users/btcpayment.html',userdeets=userdeets,uploadfile=uploadfile)
            else:
                uploader = Transaction(trans_name=name, trans_amount=amount ,trans_plan=transplan,trans_status='Pending Confirmation',trans_action=action, trans_user_id =id)
                db.session.add(uploader)
                db.session.commit()
                flash('Your reciept have successfully been uploaded. Check your Transaction history','success')
                return redirect(url_for('ethupload'))
    

# This is displaying the Contact Page


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        message = request.form.get('message')

        # Validate form fields
        if not fullname or not email or not message:
            flash("All fields are required!", "error")
            return redirect(url_for('contact'))

        # Compose email
        subject = f"Contact Form Submission from {fullname}"
        msg_body = f"Name: {fullname}\nEmail: {email}\nMessage:\n{message}"

        # Send email
        msg = Message(subject=subject,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['Info@capitalgold.us'])
        msg.body = msg_body

        try:
            mail.send(msg)
            flash("Message sent successfully!", "success")
        except Exception as e:
            flash("An error occurred. Could not send message.", "error")
            print(e)

        return redirect(url_for('contact'))

    # Render contact form on GET request
    return render_template('users/contact.html')
        

# This is displaying the transaction hsitory
@app.route('/history/')
@login_required
def history():
    id = session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    deets = db.session.query(Transaction).filter_by(trans_user_id=id).all()
    return render_template('users/transactions.html',userdeets=userdeets,deets=deets)


# This the route for withdrawal
@app.route('/withdrawal/', methods=['POST','GET'])
@login_required
def withdrawal():
    uploadfile = Withdrawal()
    id= session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    if request.method == "GET":
      return render_template("users/withdrawal.html",userdeets=userdeets,uploadfile=uploadfile)
    else:
         if request.method =='GET':
            deets= db.session.query(Transaction).all()
            return render_template('users/ethpayment.html',deets=deets,userdeets=userdeets)
         else:
            #retrieve the file
            amount =request.form.get('amount')
            account = request.form.get('account')
            action = request.form.get('action')
            uploader = Transaction(trans_name=account,trans_amount=amount,trans_plan="Withdrawal",trans_status='Processing',trans_filename='Default.png',trans_action=action, trans_user_id =id)
            db.session.add(uploader)
            db.session.commit()
            flash('Withdrawal is currently being processed, Contact customers service for further Assistance','success')
            return redirect(url_for('withdrawal'))


@app.route("/about/")
def about_us():
    return render_template("users/about.html", title="About Us")

@app.route("/plans/")
def plans():
    return render_template("users/plan.html", title="Plans")

@app.route("/faq/")
def faq():
    return render_template("users/faq.html", title="FAQ")

@app.route("/dashboard/")
@login_required
def dashboard():
    id= session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    
    deets = db.session.query(Transaction).filter_by(trans_user_id=id).limit(6).all()
    return render_template("users/dashboard.html", userdeets=userdeets,deets=deets)


@app.route("/Policy/")
def policy():
    return render_template("users/policy.html", title="FAQ")






# this is the payment page 

    






@app.route("/logout")
def logout():
    if session.get('user')!= None:
        session.pop('user',None)
        flash('you\'ve logged out successfully',"success")
    return redirect(url_for('login'))





@app.errorhandler(404)
def error_page(errors):
    return render_template("users/errorpage.html")



@app.after_request
def after_request(response):
    response.headers["cache-control"]="no-cache, no-store, must-revalidate"
    return response





# @app.errorhandler(500)
# def server_error_page(errors):
#     return render_template("users/errorpage.html")
 

# @app.errorhandler(403)
# def forbbiden_page(errors):
#     return render_template("forbbiden.html")



# # @app.route("/registration")
# # def registration():
# #     if request.method =="GET":
# #         return render_template("users/reg_log.com")

# @app.route("/layout")
# def layout():
#     return render_template("users/layout.html")








