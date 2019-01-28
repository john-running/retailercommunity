# project/admin/views.py
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, make_response
from flask_login import login_user,login_required,logout_user,current_user
from project import db
from project.models import User,Product,Purchase,Review
from project.forms import ProductForm,ReviewForm,ModerateReviewForm
import sendgrid
from sendgrid.helpers.mail import *

admin_blueprint = Blueprint('admin',__name__,template_folder='templates/admin')

sendgridkey = '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'

@admin_blueprint.route('/admin')
@login_required
def admin():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    return render_template('admin.html')


@admin_blueprint.route('/allreviews')
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
    return render_template('allreviews.html', reviews=reviews)

@admin_blueprint.route('/allusers')
@login_required
def all_users():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    users = User.query.all()

    return render_template('allusers.html', users=users)

@admin_blueprint.route('/moderatereview', methods=['GET', 'POST'])
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
        update_purchase = Purchase.query.filter_by(product_id=review.product_id, user_id= review.user.id).first()
        if form.status.data == "Rejected":
            update_purchase.hasreview = 0
        else:
            update_purchase.hasreview = 1
        db.session.commit()
        # sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        sg = sendgrid.SendGridAPIClient(apikey=sendgridkey)
        from_email = Email("ReviewModerator@retailercommunity.com", current_user.fname + " " + current_user.lname + ", Community Content Moderator")
        to_email = Email(review.user.email)
        subject = "Feedback on your Product Review from Tesco Retailer Community"
        if form.status.data.lower() == "approved":
            bodycopy = "<p style='color:black;'>Hi {},<br />Your review has been <strong>{}</strong>. You received <strong>{} Club Card</strong> points for your review. Here is my feedback:<br /><br />{}<br /><br />Please share more <a href='http://tesco.retailercommunity.com'>feedback</a>.</p>".format(review.user.nickname,form.status.data.lower(),review.product.reviewpoints,form.feedback.data)
        else:
            bodycopy = "<p style='color:black;'>Hi {},<br />Your review has been <strong>{}</strong>. Here is my feedback:<br /><br />{}<br /><br />But don't worry. You can <a href='http://tesco.retailercommunity.com'>try again</a>.</p>".format(review.user.nickname,form.status.data.lower(),form.feedback.data)
        content = Content("text/html", bodycopy)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        flash ('Feedback sent to {}.'.format(review.user.email))
        return redirect(url_for('admin.all_reviews'))

    form.hasreview.data=request.args.get('id') # grabbing review ID from the querystring
    form.feedback.data=review.feedback

    return render_template('moderatoreview.html', form=form, review=review)


@admin_blueprint.route('/addproduct', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.list_products'))
    return render_template('addproduct.html', form=form)

@admin_blueprint.route('/products')
@login_required
def list_products():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    uid = request.args.get('uid')
    products = Product.query.all()
    if uid == None:
        return render_template('products.html', products=products, nouser = 1)
    else:
        user = User.query.filter_by(id=request.args.get('uid')).first()
        return render_template('products.html', products=products, user=user, nouser = 0)

@admin_blueprint.route('/addpurchase')
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
    redirurl = url_for('admin.list_purchases')+'?uid='+user_id
    return redirect(redirurl)

@admin_blueprint.route('/purchases')
@login_required
def list_purchases():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    user_id = request.args.get('uid')
    if user_id == None:
        user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    purchases = Purchase.query.filter_by(user_id = user_id)

    return render_template('purchases.html', purchases=purchases, user=user)

@admin_blueprint.route('/deleteuser')
@login_required
def delete_user():
    if current_user.role !="Admin":
        return redirect(url_for('home'))
    user_id = request.args.get('uid')
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.all_users'))
