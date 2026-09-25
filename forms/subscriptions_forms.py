from wtforms import StringField, DecimalField, SelectField, DateField
from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange


class AddSubscription(FlaskForm):
    service = StringField('Service', validators=[DataRequired(), Length(min=2, max=50), Regexp(r"^[a-zA-Z0-9 .+\-]+$")])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0, max=10000)])
    currency = SelectField(
        "Currency",
        choices=[
            ("EUR", "EUR (€)"),
            ("USD", "USD ($)"),
            ("GBP", "GBP (£)")
        ]
    )
    billing_cycle = SelectField('Billing cycle', choices=[
        ('days', 'Days'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('weekly', 'Weekly')
    ])
    duration = IntegerField('Duration', validators=[DataRequired(), NumberRange(min=1)])
    started_on = DateField('Started on', format="%Y-%m-%d", validators=[DataRequired()])
    plan = StringField('Plan', validators=[DataRequired(), Length(min=1, max=50)])
    category = SelectField('category', choices=[
        ("streaming", "Streaming"),
        ("music", "Music"),
        ("gaming", "Gaming"),
        ("food", "Food"),
        ("security", "Security"),
        ("cloud", "Cloud storage"),
        ("productivity", "Productivity"),
        ("education", "Education"),
        ("news", "News"),
        ("fitness", "Fitness"),
        ("other", "Other")
    ])
    notes = StringField('Notes', validators=[Length(max=100)])
    auto_renew = SelectField('Automatic payment', choices=[
        ("active", "Active"),
        ("disabled", "Disabled")
    ])
    submit = SubmitField('Submit')


class EditSubscription(FlaskForm):
    notes = StringField('Notes', validators=[Length(max=100)])
    submit = SubmitField('Submit')


class DeleteSubscription(FlaskForm):
    service = StringField('service')
    price = DecimalField('Price')
    category = SelectField('Category', choices=[
            ("streaming", "Streaming"),
            ("music", "Music"),
            ("gaming", "Gaming"),
            ("food", "Food"),
            ("security", "Security"),
            ("cloud", "Cloud storage"),
            ("productivity", "Productivity"),
            ("education", "Education"),
            ("news", "News"),
            ("fitness", "Fitness"),
            ("other", "Other")
        ])
    delete = SubmitField("Delete Subscription")