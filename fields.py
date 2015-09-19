from wtforms import fields
from .widgets import WysiHtml5Widget


class WysiHtml5TextAreaField(fields.TextAreaField):
    widget = WysiHtml5Widget()
