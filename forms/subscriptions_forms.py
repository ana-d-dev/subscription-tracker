from wtforms import StringField, DecimalField, SelectField, DateField
from flask_wtf import FlaskForm
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange


class AddSubscription(FlaskForm):
    service = StringField('service', validators=[DataRequired(), Length(min=2, max=50), Regexp(r"^[a-zA-Z0-9 .+\-]+$")])
    price = DecimalField('price', validators=[DataRequired(), NumberRange(min=0, max=10000)])
    currency = SelectField(
        "Currency",
        choices=[
            ("EUR", "EUR (€)"),
            ("USD", "USD ($)"),
            ("GBP", "GBP (£)")
        ]
    )
    billing_cycle = SelectField('billing_cycle', choices=[
        ('days', 'Days'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('weekly', 'Weekly')
    ])
    duration = IntegerField('duration', validators=[DataRequired(), NumberRange(min=1)])
    started_on = DateField('started_on', format="%Y-%m-%d", validators=[DataRequired()])
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
    notes = StringField('notes', validators=[Length(max=100)])
    auto_renew = SelectField('Automatic payment', choices=[
        ("active", "Active"),
        ("disabled", "Disabled")
    ])
    submit = SubmitField('Submit')


class EditSubscription(FlaskForm):
    notes = StringField('notes', validators=[Length(max=100)])
    submit = SubmitField('Submit')


class DeleteSubscription(FlaskForm):
    service = StringField('service')
    price = DecimalField('price', validators=[DataRequired(), NumberRange(min=0, max=10000)])
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
    delete = SubmitField("Delete Subscription")