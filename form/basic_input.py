# -*- encoding: utf-8 -*-

from input_base import InputBase

class BasicInput(InputBase):
    __template__ = None
    __input_type__ = None
    __input_tag__ = 'input'
    __has_label__ = True


    def __init__(self, name, label=None, validator=None, **kwargs):
        if self.__template__ is None:
            assert self.__input_type__ is not None
            self.__class__.__template__ =  """
<html
    xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://genshi.edgewall.org/"
    py:strip="">
<div class="$row_class">
    <label py:if="has_label" for="$name">$label</label>
    <%(input_tag)s name="$name" type="%(input_type)s" value="$value" />
    <div py:if="error" class="$error_class">$error</div>
</div>
</html>
            """ % {
                'input_type': self.__input_type__,
                'input_tag': self.__input_tag__,
            }
        kwargs.setdefault('label', name)
        kwargs.setdefault('has_label', self.__has_label__)
        kwargs.setdefault('row_class', 'form_row')
        kwargs.setdefault('error_class', 'form_error')
        self.validator = validator
        InputBase.__init__(self, name, **kwargs)

    class _LazyGenerator(object):
        def __init__(self, field, value):
            self._field = field
            self._value = value
            self._is_valid = None

        @property
        def is_valid(self):
            if self._is_valid is None:
                if self._field.validator is not None:
                    self._is_valid = self._value is not None and self._field.validator(self._value)
                    assert isinstance(self._is_valid, bool)
                else:
                    self._is_valid = True
            return self._is_valid

        @property
        def value(self): return self._value

        @property
        def name(self): return self._field.name

        @property
        def error(self):
            if self._value is None or self.is_valid:
                return None
            return self._field.validator.msg

        def render(self, **kwargs):
            return self._field._render(
                value=self._value,
                error=self.error,
                **kwargs
            )


        def _validate(self):
            if self._field._validator is not None:
                return self._validator(self._value)
            return True

        def __str__(self):
            return "<%s: %s = %s>" % (
                self._field.__class__.__name__,
                self.name,
                str(self.value)
            )

    def generate(self, input):
        return self._LazyGenerator(self, input.get(self.name, None))
