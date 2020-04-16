from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


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
