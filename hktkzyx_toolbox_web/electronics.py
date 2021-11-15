from __future__ import annotations

from flask import Blueprint, flash, render_template
from flask_wtf import FlaskForm
from hktkzyx_toolbox import electronics
from hktkzyx_toolbox.electronics import typical_led, LED, typical_led_red
from wtforms import DecimalField, SubmitField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

bp = Blueprint('electronics', __name__, url_prefix='/electronics')


class LEDGetDividerResistanceForm(FlaskForm):
    voltage = DecimalField('电压 (V):', [NumberRange(min=0)])
    current = DecimalField('电流 (mA):', validators=[NumberRange(min=0)])
    kind = SelectField(
        '标准电阻模式',
        validators=[DataRequired()],
        choices=[('raw', '无'), ('nearest', '电流优先'), ('upper_limit', '电流上限'),
                 ('lower_limit', '电流下限')])
    led = SelectField(
        'LED 种类',
        validators=[DataRequired()],
        choices=[('typical led', '典型LED'), ('typical led red', '典型红光LED')])
    submit = SubmitField('提交')


class LEDGetWorkCurrentForm(FlaskForm):
    voltage = DecimalField('电压 (V):', [NumberRange(min=0)])
    resistance = DecimalField('电阻 (Ω):', validators=[NumberRange(min=0)])
    kind = SelectField(
        '标准电阻模式',
        validators=[DataRequired()],
        choices=[('raw', '无'), ('nearest', '最接近'), ('up', '向上舍入'),
                 ('down', '向下舍入')])
    led = SelectField(
        'LED 种类',
        validators=[DataRequired()],
        choices=[('typical LED', '典型LED'), ('typical LED red', '典型红光LED')])
    submit = SubmitField('提交')


def _get_real_current(led: LED,
                      voltage: float,
                      resistance: Optional[float] = None):
    if resistance:
        try:
            current = led.get_work_current(voltage, resistance)
        except ValueError:
            current = None
        return current


def _get_real_current_resistance_group(led: LED, voltage, current):
    flash_msg = ('检查电流值大小,不可超过上限.')
    try:
        resistance = led.get_divider_resistance(voltage, current)
    except ValueError:
        flash(flash_msg, category='error')
        return (None, None), (current, None), (None, None)
    small_resistance = electronics.get_standard_resistance(resistance, 'down')
    large_current = _get_real_current(led, voltage, small_resistance)
    large_resistance = electronics.get_standard_resistance(resistance, 'up')
    small_current = _get_real_current(led, voltage, large_resistance)
    return (large_current, small_resistance), (current,
                                               resistance), (small_current,
                                                             large_resistance)


def _get_divider_resistance(
        form: LEDGetDividerResistanceForm) -> tuple[float, float, float]:
    voltage = float(form.voltage.data)
    current = float(form.current.data) * 1e-3
    kind = form.kind.data
    led_type = form.led.data
    print(led_type)
    if str.lower(led_type) == 'typical led red':
        led = typical_led_red
    else:
        led = typical_led
    ((large_current, small_resistance), (current, resistance),
     (small_current, large_resistance)) = _get_real_current_resistance_group(
         led, voltage, current)
    if kind == 'raw':
        real_current = current
        divider_resistance = resistance
    if kind == 'nearest':
        if small_current and large_current:
            real_current = (small_current if
                            current - small_current <= large_current - current
                            else large_current)
            divider_resistance = (large_resistance
                                  if current - small_current <= large_current
                                  - current else small_resistance)
        elif small_current:
            real_current = small_current
            divider_resistance = large_resistance
        elif large_current:
            real_current = large_current
            divider_resistance = small_resistance
        else:
            real_current = current
            divider_resistance = None
    if kind == 'upper_limit':
        if small_current:
            real_current = small_current
            divider_resistance = large_resistance
        else:
            real_current = current
            divider_resistance = None
    if kind == 'lower_limit':
        if large_current:
            real_current = large_current
            divider_resistance = small_resistance
        else:
            real_current = current
            divider_resistance = None
    return voltage, real_current, divider_resistance


def _get_work_current(
        form: LEDGetWorkCurrentForm) -> tuple[float, float, float]:
    voltage = float(form.voltage.data)
    resistance = float(form.resistance.data)
    kind = form.kind.data
    led_type = form.led.data
    if str.lower(led_type) == 'typical led red':
        led = typical_led_red
    else:
        led = typical_led
    small_resistance = electronics.get_standard_resistance(resistance, 'down')
    large_resistance = electronics.get_standard_resistance(resistance, 'up')
    nearest_resistance = electronics.get_standard_resistance(resistance)
    if kind == 'raw':
        real_resistance = resistance
    if kind == 'nearest':
        real_resistance = nearest_resistance
    if kind == 'up':
        real_resistance = large_resistance
    if kind == 'down':
        real_resistance = small_resistance

    if real_resistance:
        try:
            work_current = led.get_work_current(voltage, real_resistance)
        except ValueError:
            flash('检查电阻阻值,不可过小.', 'error')
            work_current = None
            real_resistance = resistance
    else:
        flash('没有找到对应标准电阻.', 'error')
        work_current = None
        real_resistance = resistance
    return voltage, work_current, real_resistance


def _view_init():
    get_divider_resistance_form = LEDGetDividerResistanceForm(
        prefix='divider_resistance')
    get_work_current_form = LEDGetWorkCurrentForm(prefix='work_current')
    output = {
        'get_divider_resistance_form': get_divider_resistance_form,
        'voltage_divider_resistance': None,
        'real_current': None,
        'divider_resistance': None,
        'get_work_current_form': get_work_current_form,
        'voltage_work_current': None,
        'work_current': None,
        'real_resistance': None,
    }
    return get_divider_resistance_form, get_work_current_form, output


@bp.route('/')
def index():
    (_, _, output) = _view_init()
    return render_template('electronics.html', **output)


@bp.route('/divider_resistance', methods=['POST'])
def divider_resistance():
    (get_divider_resistance_form, _, output) = _view_init()
    if get_divider_resistance_form.validate_on_submit():
        (voltage, real_current, divider_resistance
         ) = _get_divider_resistance(get_divider_resistance_form)
        real_current = round(real_current * 1e3, 4) if real_current else None
        divider_resistance = electronics.get_human_format_resistance(
            divider_resistance)
        output.update(voltage_divider_resistance=voltage,
                      real_current=real_current,
                      divider_resistance=divider_resistance)
    return render_template('electronics.html', **output)


@bp.route('/work_current', methods=['POST'])
def work_current():
    (_, get_work_current_form, output) = _view_init()
    if get_work_current_form.validate_on_submit():
        (voltage, work_current,
         real_resistance) = _get_work_current(get_work_current_form)
        work_current = round(work_current * 1e3, 4) if work_current else None
        real_resistance = electronics.get_human_format_resistance(
            real_resistance)
        output.update(voltage_work_current=voltage,
                      work_current=work_current,
                      real_resistance=real_resistance)
    return render_template('electronics.html', **output)
