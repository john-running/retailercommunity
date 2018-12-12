#app.py
from project import app,db
from flask import render_template,redirect,request,url_for,flash,abort
from flask_login import login_user,login_required,logout_user,current_user
from project.models import User,Product,Purchase,Review
from project.forms import LoginForm, RegistrationForm,ProductForm,ReviewForm,ModerateReviewForm,ForgotPasswordForm,ResetPasswordForm
from werkzeug.security import generate_password_hash

import sendgrid
import os
from sendgrid.helpers.mail import *

@app.route('/')
def home():
    if current_user.is_authenticated:
        purchases = Purchase.query.filter_by(user_id = current_user.id).filter_by(hasreview=0).first()
        reviews = Review.query.filter_by(user_id = current_user.id)
        reviewcount = reviews.count()
        approvedreviews = reviews.filter_by(status = "Approved")
        approvedreviewcount = approvedreviews.count()
        reviewpoints = 0
        for rev in approvedreviews:
            reviewpoints = reviewpoints + rev.product.reviewpoints
        if purchases is not None:  #user still has products to review
            return render_template('home.html',purchases=purchases,reviewcount = reviewcount, approvedreviewcount = approvedreviewcount, reviewpoints = reviewpoints)
        return render_template('home.html',reviewcount = reviewcount, approvedreviewcount = approvedreviewcount, reviewpoints = reviewpoints)
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out!")
    return redirect(url_for('home'))


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('home')
                return redirect(next)
        flash ('The email or password you entered do not match our records.  Please try again.')
    return render_template('login.html',form=form)

@app.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('login'))
        else:
            flash('The email address you chose is already in our system.')
            return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/writereview', methods=['GET', 'POST'])
@login_required
def write_review():
    product = Product.query.filter_by(id = request.args.get('id')).first()
    form = ReviewForm()
    form.product_id.data=request.args.get('id') # grabbing product ID from the querystring


    if form.validate_on_submit():
        review = Review(heading=form.heading.data,
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
        return redirect(url_for('thanks'))
    return render_template('writereview.html', form=form, product=product)

@app.route('/moderatorfeedback', methods=['GET', 'POST'])
@login_required
def moderator_feedback():
    review = Review.query.filter_by(id = request.args.get('id')).first()
    return render_template('moderatorfeedback.html', review=review)


@app.route('/reviews')
@login_required
def list_reviews():
    reviews = Review.query.filter_by(user_id = current_user.id)
    return render_template('reviews.html', reviews=reviews)


@app.route('/profile')
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

@app.route('/thanks')
@login_required
def thanks():
    return render_template('thanks.html')

@app.route('/forgotpassword',methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:


            # sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
            sg = sendgrid.SendGridAPIClient(apikey='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')
            from_email = Email("do.not.reply@retailercommunity.com")
            to_email = Email(user.email)
            subject = "Forgot Password Email from Tesco Retail Reviews"
            urlstring = "http://tesco.retailercommunity.com/resetpassword?id=" + user.password_hash + "&email="+user.email
            content = Content("text/plain", "Click {} to reset your password.".format(urlstring))
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            flash ('Thanks.  We are sending you a link to reset your password now.')
            return redirect(url_for('home'))
        flash ('The email entered do not match our records.  Please try again.')
    return render_template('forgotpassword.html',form=form)

@app.route('/resetpassword',methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    user = User.query.filter_by(password_hash=request.args.get('id'), email=request.args.get('email')).first()
    if user is not None:
        form.email.data=request.args.get('email')
        form.password_hash.data=request.args.get('id')
        if form.validate_on_submit():
            user = User.query.filter_by(password_hash=form.password_hash.data,email=form.email.data).first()
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password Updated')
            return redirect(url_for('home'))
        return render_template('resetpassword.html',form=form, user=user)
    else:
        return redirect(url_for('home'))





#####
#Resources below intended to be used to populate database do admin stuff (will not make it into production MVP)
#####

@app.route('/admin')
@login_required
def admin():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    return render_template('admin/admin.html')

@app.route('/admin/allreviews')
@login_required
def all_reviews():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    status = request.args.get('status')
    user_id = request.args.get('uid')
    if user_id == None:
        if (status == None or status == 'All'):
            reviews = Review.query.all()
        else:
            reviews = Review.query.filter_by(status=status).all()
    else:
        reviews = Review.query.filter_by(user_id=user_id).all()
    return render_template('admin/allreviews.html', reviews=reviews)

@app.route('/admin/allusers')
@login_required
def all_users():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    users = User.query.all()

    return render_template('admin/allusers.html', users=users)

@app.route('/admin/moderatereview', methods=['GET', 'POST'])
@login_required
def moderate_review():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    review = Review.query.filter_by(id = request.args.get('id')).first()
    form = ModerateReviewForm()

    if form.validate_on_submit():
        update_review = review
        update_review.feedback = form.feedback.data
        update_review.status = form.status.data

        #make purchase reviewable again if original review is rejected
        update_purchase = Purchase.query.filter_by(product_id=review.product_id, user_id= current_user.id).first()
        if form.status.data == "Rejected":
            update_purchase.hasreview = 0
        else:
            update_purchase.hasreview = 1
        db.session.commit()

        return redirect(url_for('all_reviews'))

    form.hasreview.data=request.args.get('id') # grabbing review ID from the querystring
    form.feedback.data=review.feedback

    return render_template('admin/moderatoreview.html', form=form, review=review)


@app.route('/admin/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data,
                    image=form.image.data,
                    price=form.price.data,
                    producturl=form.producturl.data,
                    reviewpoints=form.reviewpoints.data,
                    description = form.description.data,
                    sku = form.sku.data)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('list_products'))
    return render_template('admin/addproduct.html', form=form)


@app.route('/admin/products')
@login_required
def list_products():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    uid = request.args.get('uid')
    products = Product.query.all()
    if uid == None:
        return render_template('admin/products.html', products=products, nouser = 1)
    else:
        user = User.query.filter_by(id=request.args.get('uid')).first()
        return render_template('admin/products.html', products=products, user=user, nouser = 0)

@app.route('/admin/addpurchase')
@login_required
def add_purchases():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    user_id = request.args.get('uid')
    if user_id == None:
        user_id = current_user.id
    alreadypurchased = Purchase.query.filter_by(product_id=request.args.get('id'),
                user_id=user_id).first()
    if alreadypurchased is None:
        purchase = Purchase(product_id=request.args.get('id'),
                user_id=user_id,hasreview=0)
        db.session.add(purchase)
        db.session.commit()
    redirurl = url_for('list_purchases')+'?uid='+user_id
    return redirect(redirurl)

@app.route('/admin/purchases')
@login_required
def list_purchases():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    user_id = request.args.get('uid')
    if user_id == None:
        user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    purchases = Purchase.query.filter_by(user_id = user_id)

    return render_template('admin/purchases.html', purchases=purchases, user=user)

@app.route('/admin/deleteuser')
@login_required
def delete_user():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    user_id = request.args.get('uid')
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('all_users'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
