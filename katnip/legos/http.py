from katnip.legos.url import DecimalNumber
from kitty.model import Container
from kitty.model import String, Static, Group


class HttpHeaderField(Container):
    def __init__(self, key, value, end=False, fuzzable=True):
        fields = [
            String(name='%s key' % key, value=key, fuzzable=False),
            Static(': '),
            Container(name='%s value' % key, fields=[value]),
            Static('\r\n')
        ]
        if end:
            fields += [Static('\r\n')]
        super(HttpHeaderField, self).__init__(name=key, fields=fields, fuzzable=fuzzable)


class textField(HttpHeaderField):
    def __init__(self, key, value, end=False, fuzzable=True):
        value_field = String(name="value", value=value)
        super(textField, self).__init__(key, value_field, end, fuzzable=fuzzable)


class intField(HttpHeaderField):
    def __init__(self, key, value, end=False, fuzzable=True):
        value_field = DecimalNumber(
            name="value",
            value=value,
            num_bits=32,
            signed=True
        )
        super(intField, self).__init__(key, value_field, end, fuzzable=fuzzable)


class HttpHeaderURL(Container):
    def __init__(self, methods, path, fuzzable=True):
        fields = [
            Group(name='method', values=methods),
            Static(' '),
            String(name='path', value=path),
            Static(' '),
            Static(name='version', value='HTTP/1.0'),
            Static('\r\n'),
        ]
        super(HttpHeaderURL, self).__init__(name='http url', fields=fields, fuzzable=fuzzable)
