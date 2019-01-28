# project/main/views.py

from project import app,db
from flask import Blueprint,render_template,redirect,request,url_for,flash,abort, make_response
from flask_login import login_user,login_required,logout_user,current_user
from project.models import User,Product,Purchase,Review
from project.forms import LoginForm, RegistrationForm,ProductForm,ReviewForm,ModerateReviewForm,ForgotPasswordForm,ResetPasswordForm,ProfileForm
from werkzeug.security import generate_password_hash

import sendgrid
import os
from datetime import datetime, timedelta
from sendgrid.helpers.mail import *
from sqlalchemy import desc

from io import StringIO
import csv

main_blueprint = Blueprint('main',__name__,template_folder='templates/main')


sendgridkey = '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'

@main_blueprint.route('/')
def home():
    if current_user.is_authenticated:
        reviews = Review.query.filter_by(user_id = current_user.id)
        reviewcount = reviews.count()
        approvedreviews = reviews.filter_by(status = "Approved")
        approvedreviewcount = approvedreviews.count()
        reviewpoints = 0
        reviewsthisweek = reviews.filter(Review.creationdate >= datetime.today() - timedelta(days=7))
        reviewthisweekcount = reviewsthisweek.count()
        purchases = Purchase.query.filter_by(user_id = current_user.id).filter_by(hasreview=0).limit(5-reviewthisweekcount).all()
        for rev in approvedreviews:
            reviewpoints = reviewpoints + rev.product.reviewpoints
        if purchases is not None and reviewthisweekcount < 5:  #user still has products to review
            return render_template('home.html',purchases=purchases,reviewcount = reviewcount, reviewthisweekcount = reviewthisweekcount, approvedreviewcount = approvedreviewcount, reviewpoints = reviewpoints)
        return render_template('home.html',reviewcount = reviewcount, reviewthisweekcount = reviewthisweekcount, approvedreviewcount = approvedreviewcount, reviewpoints = reviewpoints)
    return render_template('home.html')

@main_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out!")
    return redirect(url_for('main.home'))


@main_blueprint.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('main.home')
                return redirect(next)
        flash ('The email or password you entered do not match our records.  Please try again.')
    return render_template('login.html',form=form)

@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    fname=form.fname.data,
                    lname=form.lname.data,
                    nickname=form.nickname.data,
                    role = "user",
                    active = 1,
                    rewardsid=form.rewardsid.data,
                    password=form.password.data)

        if form.check_email(user.email):
            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering! Now you can login!')
            return redirect(url_for('main.login'))
        else:
            flash('The email address you chose is already in our system.')
            return redirect(url_for('main.register'))
    return render_template('register.html', form=form)

@main_blueprint.route('/writereview', methods=['GET', 'POST'])
@login_required
def write_review():
    product = Product.query.filter_by(id = request.args.get('id')).first()
    form = ReviewForm()
    form.product_id.data=request.args.get('id') # grabbing product ID from the querystring
    if form.validate_on_submit():
        review = Review(creationdate=datetime.today(),
                    heading=form.heading.data,
                    description=form.description.data,
                    starrating=form.starrating.data,
                    user_id=current_user.id,
                    status="Pending",
                    product_id=form.product_id.data,
                    feedback = "")
        db.session.add(review)
        update_purchase = Purchase.query.filter_by(product_id = form.product_id.data).filter_by(user_id = current_user.id).first()
        update_purchase.hasreview = 1
        db.session.commit()
        return redirect(url_for('main.thanks'))
    return render_template('writereview.html', form=form, product=product)

@main_blueprint.route('/moderatorfeedback', methods=['GET', 'POST'])
@login_required
def moderator_feedback():
    review = Review.query.filter_by(id = request.args.get('id')).first()
    return render_template('moderatorfeedback.html', review=review)


@main_blueprint.route('/reviews')
@login_required
def list_reviews():
    reviews = Review.query.filter_by(user_id = current_user.id).order_by(desc(Review.creationdate))
    return render_template('reviews.html', reviews=reviews)



@main_blueprint.route('/profile')
@login_required
def profile():
    profile = User.query.filter_by(id = current_user.id).first()  # rewrite as method (since it's being used in both profile and home)
    reviews = Review.query.filter_by(user_id = current_user.id)
    reviewcount = reviews.count()
    approvedreviews = reviews.filter_by(status = "Approved")
    approvedreviewcount = approvedreviews.count()
    reviewpoints = 0
    for rev in approvedreviews:
        reviewpoints = reviewpoints + rev.product.reviewpoints
    return render_template('profile.html', profile=profile,reviewcount = reviewcount, approvedreviewcount = approvedreviewcount, reviewpoints = reviewpoints)

@main_blueprint.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id = current_user.id).first()
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.nickname = form.nickname.data
        user.rewardsid = form.rewardsid.data
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.profile'))
    user = User.query.filter_by(id = current_user.id).first()
    form.fname.data = user.fname
    form.lname.data = user.lname
    form.nickname.data = user.nickname
    form.rewardsid.data = user.rewardsid
    return render_template('updateprofile.html', form=form)

@main_blueprint.route('/thanks')
@login_required
def thanks():
    reviews = Review.query.filter_by(user_id = current_user.id).order_by(desc(Review.creationdate))
    reviewsthisweek = reviews.filter(Review.creationdate >= datetime.today() - timedelta(days=7))
    reviewthisweekcount = reviewsthisweek.count()
    lastreview = reviews.first()
    reviewpoints = lastreview.product.reviewpoints
    return render_template('thanks.html', reviewthisweekcount = reviewthisweekcount, reviewpoints = reviewpoints)

@main_blueprint.route('/forgotpassword',methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            # sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
            sg = sendgrid.SendGridAPIClient(apikey=sendgridkey)
            from_email = Email("do.not.reply@retailercommunity.com", "Tesco Reviewer Community Administrator")
            to_email = Email(user.email)
            subject = "Forgot Password Email from Tesco Reviewer Community"
            urlstring = "<a href='http://tesco.retailercommunity.com/resetpassword?id={}&email={}'>here</a>".format(user.password_hash,user.email)
            content = Content("text/html", "Hi.  We just received a request to help you retrieve your password.  Click {} to reset your password.".format(urlstring))
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            flash ('Thanks.  We are sending you a link to reset your password now.')
            return redirect(url_for('main.home'))
        flash ('The email entered do not match our records.  Please try again.')
    return render_template('forgotpassword.html',form=form)

@main_blueprint.route('/resetpassword',methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if current_user.is_authenticated:
        user = User.query.filter_by(id = current_user.id).first()
        redirecturl = url_for('main.profile')
    else:
        user = User.query.filter_by(password_hash=request.args.get('id'), email=request.args.get('email')).first()
        redirecturl = url_for('main.home')
    if user is not None:
        form.email.data=request.args.get('email')
        form.password_hash.data=request.args.get('id')
        if form.validate_on_submit():
            if current_user.is_authenticated:
                user = User.query.filter_by(id = current_user.id).first()
            else:
                user = User.query.filter_by(password_hash=form.password_hash.data,email=form.email.data).first()
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password Updated')
            return redirect(redirecturl)
        return render_template('resetpassword.html',form=form, user=user)
    else:
        flash('Something went wrong. Please try again.')
        return redirect(url_for('main.forgot_password'))

@main_blueprint.route('/about')
def about():
    return render_template('about.html')

@main_blueprint.route('/privacyandcookiepolicy')
def privacy():
    return render_template('privacy.html')

@main_blueprint.route('/termsandconditions')
def termsandconditions():
    return render_template('terms.html')

@main_blueprint.route('/download')
@login_required
def download():
    reviews = Review.query.filter_by(user_id = current_user.id).order_by(Review.creationdate)
    # mylist = [[1,2,3,4],[1,2,3,4],[5,6,7,8]]
    si = StringIO()
    cw = csv.writer(si)
    firstrow = ['ID','Creation Date','Product Name','Product SKU','Heading','Review','Star Rating (1-5)','Status','Feedback']
    cw.writerow(firstrow)
    for review in reviews:
        rowlist = [review.id,review.creationdate,review.product.name,review.product.sku,review.heading,review.description,review.starrating,review.status,review.feedback]
        cw.writerow(rowlist)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
