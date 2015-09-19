from wtforms.widgets import TextArea, HTMLString, html_params
from cgi import escape


class WysiHtml5Widget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs['data-role'] = u'wysihtml5'
        kwargs['class'] = u'span8'
        kwargs['rows'] = 10
        return super(WysiHtml5Widget, self).__call__(field, **kwargs)
