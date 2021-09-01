from typing import Tuple

from flask import Blueprint, flash, render_template
from flask_wtf import FlaskForm
from hktkzyx_toolbox import electronics
from hktkzyx_toolbox.electronics import typical_led
from wtforms import DecimalField, SubmitField
from wtforms.validators import NumberRange, Optional

bp = Blueprint('electronics', __name__, url_prefix='/electronics')


class LEDCurrentResistanceForm(FlaskForm):
    voltage = DecimalField('电压 (V):', [NumberRange(min=0)])
    current = DecimalField('电流 (mA):',
                           validators=[Optional(), NumberRange(min=0, max=24)])
    resistance = DecimalField('电阻 (Ω):',
                              validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('提交')


def led_current_resistance_input(
        form: FlaskForm) -> Tuple[float, float, float]:
    """Process the input of `LEDCurrentResistanceForm`."""
    voltage = float(form.voltage.data)
    current = float(form.current.data) * 1e-3 if form.current.data else None
    if form.resistance.data:
        resistance = electronics.get_standard_resistance(
            float(form.resistance.data))
    else:
        resistance = None
    return voltage, current, resistance


def led_current_resistance_output(current: float,
                                  resistance: float) -> Tuple[float, float]:
    """Process the output of `LEDCurrentResistanceForm`."""
    current = round(current * 1e3, 2)
    resistance = electronics.get_standard_resistance(resistance,
                                                     human_format=True)
    return current, resistance


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = LEDCurrentResistanceForm()
    current, resistance = None, None
    if form.validate_on_submit():
        (voltage, current, resistance) = led_current_resistance_input(form)
        try:
            (current, resistance) = typical_led.get_current_and_resistance(
                voltage, current, resistance)
        except ValueError:
            flash(('检查电流和电阻的输入值. 应当满足: '
                   '1. 电流电阻至少一个大于0; '
                   '2. 电流不超过LED上限; '
                   '3. 电阻不会过小'),
                  category='error')
            return render_template('electronics.html',
                                   form=form,
                                   current=None,
                                   resistance=None)
        (current,
         resistance) = led_current_resistance_output(current, resistance)
    return render_template('electronics.html',
                           form=form,
                           current=current,
                           resistance=resistance)
