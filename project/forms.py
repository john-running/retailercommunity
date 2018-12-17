#forms.py
from project.models import User
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,IntegerField,DecimalField,PasswordField,SubmitField,HiddenField,RadioField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from wtforms import ValidationError
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Sign in")

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    submit = SubmitField("Send")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords must match.')])
    pass_confirm = PasswordField('Confirm Password',validators=[DataRequired()])
    email = HiddenField("Email")
    password_hash =  HiddenField('Password_Hash')
    submit = SubmitField("Update")


class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    fname = StringField('First Name',validators=[DataRequired()])
    lname = StringField('Last Name',validators=[DataRequired()])
    nickname = StringField('Nickname',validators=[DataRequired()])
    rewardsid = StringField('Clubcard #',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords must match.')])
    pass_confirm = PasswordField('Confirm Password',validators=[DataRequired()])
    opt_in = BooleanField('Opt In', validators=[DataRequired(message='You must confirm acceptance of the Terms and Conditions before registering.')])
    submit = SubmitField('Register')

    def check_email(self,email):
        if User.query.filter_by(email=email).first():
            return False
        return True

class ProfileForm(FlaskForm):
    fname = StringField('First Name',validators=[DataRequired()])
    lname = StringField('Last Name',validators=[DataRequired()])
    nickname = StringField('Nickname',validators=[DataRequired()])
    rewardsid = StringField('RewardsId',validators=[DataRequired()])
    submit = SubmitField('Update')

class ProductForm(FlaskForm):
    name = StringField('Product Name',validators=[DataRequired()])
    sku = StringField('SKU',validators=[DataRequired()])
    image = StringField('Image URL',validators=[DataRequired()])
    price = DecimalField('Price',validators=[DataRequired()])
    producturl= StringField('Product URL',validators=[DataRequired()])
    description= TextAreaField('Description',validators=[DataRequired()])
    reviewpoints= StringField('Review Points',validators=[DataRequired()])
    submit = SubmitField('Add')


class ReviewForm(FlaskForm):
    heading = StringField('Review Heading',validators=[DataRequired(),Length(min=10, max=50, message='Your heading must be 10 - 50 characters in length.')])
    description = TextAreaField('Review Description',validators=[DataRequired(),Length(min=100, max=2000, message='Your review must be more than 100 characters and less than 2000 characters.')])
    starrating = HiddenField('Star Rating', validators=[DataRequired(message='You must enter a star rating.')])
    product_id =  HiddenField('Product_ID')
    submit = SubmitField('Submit Review')


class ModerateReviewForm(FlaskForm):
    feedback = TextAreaField('Feedback',validators=[DataRequired()])
    status = RadioField('Status', choices = [('Approved','Approved'),('Rejected','Rejected')])
    hasreview =  HiddenField('Hasreview')
    submit = SubmitField('Moderate')
