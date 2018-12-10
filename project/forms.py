#forms.py
from project.models import User
from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,IntegerField,DecimalField,PasswordField,SubmitField,HiddenField,RadioField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    fname = StringField('First Name',validators=[DataRequired()])
    lname = StringField('Last Name',validators=[DataRequired()])
    nickname = StringField('Nickname',validators=[DataRequired()])
    rewardsid = StringField('RewardsId',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords must match.')])
    pass_confirm = PasswordField('Confirm Password',validators=[DataRequired()])
    submit = SubmitField('Register')

    def check_email(self,email):
        if User.query.filter_by(email=email).first():
            return False
        return True

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
    heading = StringField('Review Heading',validators=[DataRequired()])
    description = TextAreaField('Review Description',validators=[DataRequired()])
    starrating = HiddenField('Star Rating', validators=[DataRequired()])
    product_id =  HiddenField('Product_ID')
    submit = SubmitField('Add Review')


class ModerateReviewForm(FlaskForm):
    feedback = TextAreaField('Feedback',validators=[DataRequired()])
    status = RadioField('Status', choices = [('Approved','Approved'),('Rejected','Rejected')])
    hasreview =  HiddenField('Hasreview')
    submit = SubmitField('Moderate')
