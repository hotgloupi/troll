# -*- encoding: utf-8 -*-

from basic_input import BasicInput

class Text(BasicInput):
    __input_type__ = 'text'

class Password(BasicInput):
    __input_type__ = 'password'

class Hidden(BasicInput):
    __input_type__ = 'hidden'
    __has_label__ = False

class Submit(BasicInput):
     __template__ = """
<html
    xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://genshi.edgewall.org/"
    py:strip="">
    <input name="$name" type="submit" value="$label" />
</html>
    """
