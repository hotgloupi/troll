# -*- encoding: utf-8 -*-

"""

Generate and validate forms

"""

import genshi
import web

from input_base import InputBase

class Form(InputBase):
    __template__ = """
<form
        xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://genshi.edgewall.org/"
        name="$name"
        py:attrs="attrs"
    >
    <py:for each="field in fields">
    $field
    </py:for>
    <div py:if="errors" class="$errors_class">
        <ul><li py:for="error in errors">$error</li></ul>
    </div>
</form>"""
    __attributes__ = InputBase.__attributes__ + ['method', 'action']

    def __init__(self, name, fields, validators=[], **kwargs):
        self.validators = validators
        self.fields = fields
        kwargs.setdefault('method', 'POST')
        kwargs.setdefault('action', '')
        kwargs.setdefault('errors_class', 'form_errors')
        InputBase.__init__(self, name, **kwargs)

    class _LazyGenerator(object):
        def __init__(self, form, input):
            self._form = form
            self._input = input
            self._is_valid = None
            self._fields = None
            self._fields_by_name = None
            self._errors = None

        @property
        def is_valid(self):
            if self._is_valid is None:
                self._is_valid = self._validate()
                assert(isinstance(self._is_valid, bool))
            return self._is_valid

        @property
        def errors(self):
            if len(self._input) == 0 or self.is_valid:
                return []
            # _validate() called by is_valid property
            assert self._errors is not None #_validate was called
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

        def render(self, **kwargs):
            fields = []
            for field in self.fields:
                fields.append(genshi.HTML(field.render()))
            return self._form._render(
                fields=fields,
                errors=self.errors,
                **kwargs
            )

        def __getitem__(self, key): return self.fields_by_name[key]

        def _validate(self):
            assert self._errors is None # only one call to _validate has been done
            self._errors = []
            if all(field.is_valid for field in self.fields):
                for validator in self._form.validators:
                    if not validators(self):
                        self._errors.append(validators.msg)
                return len(self._errors) == 0
            return False

        def __str__(self):
            return '%s: [%s]' % (
                self._form.__class__.__name__,
                ', '.join(str(f) for f in self.fields),
            )

    def generate(self, input=None):
        if input is None:
            input = web.input()
        return self._LazyGenerator(self, input)

