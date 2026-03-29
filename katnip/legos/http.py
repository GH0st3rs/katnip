from katnip.legos.url import DecimalNumber, Search, Path, urlparse
from kitty.model import Container
from kitty.model import String, Static, Group, Delimiter, Float, Size, OneOf
from kitty.model import ENC_BITS_BASE64, FloatAsciiEncoder, ENC_INT_DEC


def _valuename(txt):
    return '%s_value' % txt


def _keyname(txt):
    return '%s_key' % txt


def bit_length(num):
    for x in range(1, 100):
        if num.bit_length() > (2 << x):
            continue
        else:
            return 2 << x


class CustomHeaderField(Container):
    def __init__(self, key, value, params={}, end=False, fuzzable_key=False, fuzzable_value=True, name=None):
        fields = [
            String(name=_keyname(key), value=key, fuzzable=fuzzable_key),
            Static(': '),
            Container(name=_valuename(key), fields=value, fuzzable=fuzzable_value),
        ]
        # Append Field value params, splitted by '; '
        for k, v in params.items():
            fields += [
                Static('; '),
                String(value=k, name='%s_param_%s' % (_valuename(key), k)),
                Static('="'),
                String(value=v, name='%s_param_%s' % (_valuename(key), v)),
                Static('"')
            ]
        # Append end of line for current Field
        fields.append(Static('\r\n'))
        if end:
            fields.append(Static('\r\n'))
        name = key if name is None else name
        super(CustomHeaderField, self).__init__(name=name, fields=fields, fuzzable=fuzzable_value)


class TextField(CustomHeaderField):
    def __init__(self, key, value, params={}, end=False, fuzzable_key=False, fuzzable_value=True, name=None):
        value_field = String(name="value", value=value)
        super(TextField, self).__init__(key=key, value=value_field, params=params,
                                        end=end, fuzzable_key=fuzzable_key,
                                        fuzzable_value=fuzzable_value, name=name)


class IntField(CustomHeaderField):
    def __init__(self, key, value, params={}, end=False, fuzzable_key=False, fuzzable_value=True, name=None):
        value_field = DecimalNumber(
            name="value",
            value=value,
            num_bits=bit_length(value),
            signed=True
        )
        super(IntField, self).__init__(key=key, value=value_field, params=params,
                                       end=end, fuzzable_key=fuzzable_key,
                                       fuzzable_value=fuzzable_value, name=name)


class ContentLengthField(CustomHeaderField):
    def __init__(self, value, sized_field, end=False, fuzzable_key=False, fuzzable_value=True):
        value_field = OneOf(fields=[
            Size(sized_field=sized_field, length=bit_length(value), encoder=ENC_INT_DEC),
            DecimalNumber(name="value", value=value, num_bits=bit_length(value), signed=True),
        ])
        super(ContentLengthField, self).__init__(key='Content-Length', value=value_field,
                                                 end=end, fuzzable_key=fuzzable_key,
                                                 fuzzable_value=fuzzable_value)


class AuthorizationField(CustomHeaderField):
    def __init__(self, key, username, password, end=False, delim=':', fuzz_username=True, fuzz_password=True, fuzzable_key=False, fuzzable=True):
        value_field = [
            Static('Basic '),
            Container(name='base64_auth', fields=[
                String(name='username', value=username, fuzzable=fuzz_username),
                Delimiter(delim, fuzzable=False),
                String(name='password', value=password, fuzzable=fuzz_password),
            ], encoder=ENC_BITS_BASE64)
        ]
        super(AuthorizationField, self).__init__(key=key, value=value_field, params={},
                                                 end=end, fuzzable_key=fuzzable_key,
                                                 fuzzable_value=fuzzable)


class HttpRequestLine(Container):
    def __init__(self, name='http_request_line', method='GET', uri='/', protocol='HTTP', version=1.0, fuzzable_method=False, fuzzable_uri=True, fuzzable=True):
        method_value = [method] if isinstance(method, str) else method
        parsed = urlparse(uri)
        uri_value = [Path(path=parsed.path, name='path', fuzz_delims=False)]
        if parsed.query:
            uri_value.append(Search(parsed.query, name='search', fuzz_value=True))
        fields = [
            Group(name='method', values=method_value, fuzzable=fuzzable_method),
            Static(' '),
            Container(name='uri', fields=uri_value, fuzzable=fuzzable_uri),
            Static(' '),
            String(name='protocol', value=protocol, fuzzable=False),
            Static('/'),
            Float(name='version', value=version, encoder=FloatAsciiEncoder('%.1f')),
            Static('\r\n'),
        ]
        super(HttpRequestLine, self).__init__(name=name, fields=fields, fuzzable=fuzzable)
