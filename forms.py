from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length


class GuessNumberForm(FlaskForm):
    guess = StringField('Digit Guess',
                        validators=[DataRequired()])
    submit = SubmitField('Submit Guess')


class GetIdForm(FlaskForm):
    game_id = IntegerField('Game Id')
    submit = SubmitField('Play Game')
