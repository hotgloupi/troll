# -*- encoding: utf-8 -*-

"""

Generate and validate forms

"""

import genshi
import web

from troll.view.interface import IView

from input_base import InputBase
from inputs import Hidden

class Form(InputBase):
    __template__ = """
<form
        xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://genshi.edgewall.org/"
        name="$name"
        py:attrs="attrs"
    >
    <div py:if="errors" class="$errors_class">
        <div py:for="error in errors" class="$error_class">$error</div>
    </div>
    <py:for each="field in fields">
    $field
    </py:for>
</form>"""
    __attributes__ = InputBase.__attributes__ + ['method', 'action']

    def __init__(self, name, fields, validators=[], **kwargs):
        self.validators = validators
        self.fields = fields + [Hidden('__csrf_token')]
        kwargs.setdefault('method', 'POST')
        kwargs.setdefault('action', '')
        kwargs.setdefault('errors_class', 'form_errors')
        kwargs.setdefault('error_class', 'form_error')
        InputBase.__init__(self, name, **kwargs)

    class _LazyGenerator(object):
        def __init__(self, form, view, input):
            self._form = form
            self._view = view
            self._input = input
            self._is_valid = None
            self._fields = None
            self._fields_by_name = None
            self._errors = []
            self._csrf = None

        @property
        def is_valid(self):
            if self._is_valid is None:
                self._is_valid = self._validate()
                assert(isinstance(self._is_valid, bool))
            return self._is_valid

        @property
        def errors(self):
            if len(self._input) != 0 and self._is_valid is None:
                self._is_valid = self._validate()
                assert(isinstance(self._is_valid, bool))
            return self._errors

        @property
        def fields(self):
            if self._fields is None:
                self._fields = list(f.generate(self._input) for f in self._form.fields)
            return self._fields

        @property
        def fields_by_name(self):
            if self._fields_by_name is None:
                self._fields_by_name = dict((f.name, f) for f in self.fields)
            return self._fields_by_name

        @property
        def csrf(self):
            if self._csrf is None:
                self._csrf = self.fields_by_name['__csrf_token']
            return self._csrf

        def __getitem__(self, key): return self.fields_by_name[key]


        def render(self, **kwargs):
            self.csrf.value = self._view.generateNewUniqueToken()
            fields = []
            for field in self.fields:
                fields.append(genshi.HTML(field.render()))
            return self._form._render(
                fields=fields,
                errors=self.errors,
                **kwargs
            )


        def _validate(self):
            if self.csrf.value is None or self.csrf.value != self._view.unique_token:
                self._errors.append("Your session has expired")
                return False

            if all(field.is_valid for field in self.fields):
                for validator in self._form.validators:
                    if not validator(self):
                        self._errors.append(validator.msg)
                return len(self._errors) == 0
            return False

        def __str__(self):
            return '%s: [%s]' % (
                self._form.__class__.__name__,
                ', '.join(str(f) for f in self.fields),
            )

    def generate(self, view, input=None):
        assert isinstance(view, IView)
        if input is None:
            input = web.input()
        return self._LazyGenerator(self, view, input)

