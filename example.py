from flask.ext.admin.contrib.sqlamodel import ModelView
from application.helpers.forms.fields import WysiHtml5TextAreaField


class ExampleModelView(AdminModelView):
    form_overrides = dict(
        body=WysiHtml5TextAreaField
    )
