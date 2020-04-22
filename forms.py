from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class GuessNumberForm(FlaskForm):
    guess = StringField('Digit Guess',
                        validators=[DataRequired()])
    submit = SubmitField('Submit Guess')


class EnterGameForm(FlaskForm):
    game_id = IntegerField('Game Id', validators=[DataRequired()])
    entered_key = PasswordField('Enter Password')
    submit = SubmitField('Play Game')


class CreateGameForm(FlaskForm):
    room_key = PasswordField('Create Password (You Can Leave it Blank)')
    confirm_roomkey = PasswordField('Confirm Password',
                                    validators=[EqualTo('room_key')])
    submit = SubmitField('Play Game')


class GenerateNumberForm(FlaskForm):
    submit = SubmitField('Generate Again')


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email', validators=[EqualTo('email'),
                                                             DataRequired(),
                                                             Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[EqualTo('password'),
                                                 DataRequired()])
    submit = SubmitField('Sing Up')


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sing In')
