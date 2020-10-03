from __future__ import unicode_literals

from io import BytesIO

from django.http import (RawPostDataException, UnreadablePostError)
from django.test import SimpleTestCase
from django.test.client import FakePayload
from django.utils.http import urlencode
from django.utils.six.moves.urllib.parse import urlencode as original_urlencode

from django_improved_view.request import WSGIRequest

HTTP_METHODS_WITH_BODY = ('POST', 'PUT', 'PATCH')


class OriginRequestTest(SimpleTestCase):
    def test_read_after_value(self):
        """
        Reading from request is allowed after accessing request contents as
        POST or body.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('name=value')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(request.POST, {'name': ['value']})
            self.assertEqual(request.body, b'name=value')
            self.assertEqual(request.read(), b'name=value')

    def test_value_after_read(self):
        """
        Construction of POST or body is not allowed after reading
        from request.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('name=value')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(request.read(2), b'na')
            with self.assertRaises(RawPostDataException):
                request.body
            self.assertEqual(request.POST, {})

    def test_non_ascii_POST(self):
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload(urlencode({'key': 'España'}))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_LENGTH': len(payload),
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'wsgi.input': payload,
            })
            self.assertEqual(request.POST, {'key': ['España']})

    def test_alternate_charset_POST(self):
        """
        Test a POST with non-utf-8 payload encoding.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload(
                original_urlencode({
                    'key': 'España'.encode('latin-1')
                }))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_LENGTH': len(payload),
                'CONTENT_TYPE': 'application/x-www-form-urlencoded; charset=iso-8859-1',
                'wsgi.input': payload,
            })
            self.assertEqual(request.POST, {'key': ['España']})

    def test_body_after_POST_multipart_form_data(self):
        """
        Reading body after parsing multipart/form-data is not allowed
        """
        # Because multipart is used for large amounts of data i.e. file uploads,
        # we don't want the data held in memory twice, and we don't want to
        # silence the error by setting body = '' either.
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload("\r\n".join([
                '--boundary', 'Content-Disposition: form-data; name="name"',
                '', 'value', '--boundary--'
                ''
            ]))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(request.POST, {'name': ['value']})
            with self.assertRaises(RawPostDataException):
                request.body

    def test_body_after_POST_multipart_related(self):
        """
        Reading body after parsing multipart that isn't form-data is allowed
        """
        # Ticket #9054
        # There are cases in which the multipart data is related instead of
        # being a binary upload, in which case it should still be accessible
        # via body.
        for method in HTTP_METHODS_WITH_BODY:
            payload_data = b"\r\n".join([
                b'--boundary', b'Content-ID: id; name="name"', b'', b'value',
                b'--boundary--'
                b''
            ])
            payload = FakePayload(payload_data)
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'multipart/related; boundary=boundary',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(request.POST, {})
            self.assertEqual(request.body, payload_data)

    def test_POST_multipart_with_content_length_zero(self):
        """
        Multipart POST requests with Content-Length >= 0 are valid and need to be handled.
        """
        # According to:
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.13
        # Every request.POST with Content-Length >= 0 is a valid request,
        # this test ensures that we handle Content-Length == 0.
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload("\r\n".join([
                '--boundary', 'Content-Disposition: form-data; name="name"',
                '', 'value', '--boundary--'
                ''
            ]))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
                'CONTENT_LENGTH': 0,
                'wsgi.input': payload
            })
            self.assertEqual(request.POST, {})

    def test_POST_binary_only(self):
        for method in HTTP_METHODS_WITH_BODY:
            payload = b'\r\n\x01\x00\x00\x00ab\x00\x00\xcd\xcc,@'
            environ = {
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/octet-stream',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': BytesIO(payload)
            }
            request = WSGIRequest(environ)
            self.assertEqual(request.POST, {})
            self.assertEqual(request.FILES, {})
            self.assertEqual(request.body, payload)

            # Same test without specifying content-type
            environ.update({
                'CONTENT_TYPE': '',
                'wsgi.input': BytesIO(payload)
            })
            request = WSGIRequest(environ)
            self.assertEqual(request.POST, {})
            self.assertEqual(request.FILES, {})
            self.assertEqual(request.body, payload)

    def test_read_by_lines(self):
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('name=value')
            request = WSGIRequest({
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(list(request), [b'name=value'])

    def test_POST_after_body_read(self):
        """
        POST should be populated even if body is read first
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('name=value')
            request = WSGIRequest({
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            request.body    # evaluate
            self.assertEqual(request.POST, {'name': ['value']})

    def test_POST_after_body_read_and_stream_read(self):
        """
        POST should be populated even if body is read first, and then
        the stream is read second.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('name=value')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            request.body    # evaluate
            self.assertEqual(request.read(1), b'n')
            self.assertEqual(request.POST, {'name': ['value']})

    def test_POST_after_body_read_and_stream_read_multipart(self):
        """
        POST should be populated even if body is read first, and then
        the stream is read second. Using multipart/form-data instead of urlencoded.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload("\r\n".join([
                '--boundary', 'Content-Disposition: form-data; name="name"',
                '', 'value', '--boundary--'
                ''
            ]))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            request.body    # evaluate
            # Consume enough data to mess up the parsing:
            self.assertEqual(request.read(13), b'--boundary\r\nC')
            self.assertEqual(request.POST, {'name': ['value']})

    def test_POST_immutable_for_mutipart(self):
        """
        MultiPartParser.parse() leaves request.POST immutable.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload("\r\n".join([
                '--boundary',
                'Content-Disposition: form-data; name="name"',
                '',
                'value',
                '--boundary--',
            ]))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload,
            })
            self.assertFalse(request.POST._mutable)

    def test_POST_connection_error(self):
        """
        If wsgi.input.read() raises an exception while trying to read() the
        POST, the exception should be identifiable (not a generic IOError).
        """

        class ExplodingBytesIO(BytesIO):
            def read(self, len=0):
                raise IOError("kaboom!")

        for method in HTTP_METHODS_WITH_BODY:
            payload = b'name=value'
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': ExplodingBytesIO(payload)
            })

            with self.assertRaises(UnreadablePostError):
                request.body

    def test_set_encoding_clears_POST(self):
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('name=Hello Günter')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload,
            })
            self.assertEqual(request.POST, {'name': ['Hello Günter']})
            request.encoding = 'iso-8859-16'
            self.assertEqual(request.POST, {'name': ['Hello GĂŒnter']})

    def test_FILES_connection_error(self):
        """
        If wsgi.input.read() raises an exception while trying to read() the
        FILES, the exception should be identifiable (not a generic IOError).
        """

        class ExplodingBytesIO(BytesIO):
            def read(self, len=0):
                raise IOError("kaboom!")

        for method in HTTP_METHODS_WITH_BODY:
            payload = b'x'
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'multipart/form-data; boundary=foo_',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': ExplodingBytesIO(payload)
            })

            with self.assertRaises(UnreadablePostError):
                request.FILES


class PatchedRequestsTests(SimpleTestCase):
    def test_read_after_value(self):
        """
        Reading from request is allowed after accessing request contents as
        data or body.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "value"}')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(request.data, {'name': 'value'})
            self.assertEqual(request.body, b'{"name": "value"}')
            self.assertEqual(request.read(), b'{"name": "value"}')

    def test_value_after_read(self):
        """
        Construction of POST or body is not allowed after reading
        from request.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "value"}')
            request = WSGIRequest({
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            self.assertEqual(request.read(2), b'{"')
            with self.assertRaises(RawPostDataException):
                request.body
            self.assertEqual(request.data, {})

    def test_non_ascii_POST(self):
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "佚名"}')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_LENGTH': len(payload),
                'CONTENT_TYPE': 'application/json',
                'wsgi.input': payload,
            })
            self.assertEqual(request.data, {'name': '佚名'})

    def test_alternate_charset_POST(self):
        """
        Test a POST with non-utf-8 payload encoding.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "佚名"}'.encode('GBK'))
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_LENGTH': len(payload),
                'CONTENT_TYPE': 'application/json; charset=GBK',
                'wsgi.input': payload,
            })
            self.assertEqual(request.data, {'name': '佚名'})

    def test_POST_after_body_read(self):
        """
        POST should be populated even if body is read first
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "佚名"}')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            request.body    # evaluate
            self.assertEqual(request.data, {'name': '佚名'})

    def test_POST_after_body_read_and_stream_read(self):
        """
        POST should be populated even if body is read first, and then
        the stream is read second.
        """
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "佚名"}')
            request = WSGIRequest({
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload
            })
            request.body    # evaluate
            self.assertEqual(request.read(1), b'{')
            self.assertEqual(request.POST, {'name': '佚名'})
            self.assertEqual(request.data, {'name': '佚名'})

    def test_POST_connection_error(self):
        """
        If wsgi.input.read() raises an exception while trying to read() the
        POST, the exception should be identifiable (not a generic IOError).
        """

        class ExplodingBytesIO(BytesIO):
            def read(self, len=0):
                raise IOError("kaboom!")

        for method in HTTP_METHODS_WITH_BODY:
            payload = '{"name": "佚名"}'.encode('utf8')
            request = WSGIRequest({
                'REQUEST_METHOD': method,
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': ExplodingBytesIO(payload)
            })

        with self.assertRaises(UnreadablePostError):
            request.body

    def test_set_encoding_clears_POST(self):
        for method in HTTP_METHODS_WITH_BODY:
            payload = FakePayload('{"name": "佚名"}')
            request = WSGIRequest({
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': len(payload),
                'wsgi.input': payload,
            })
            self.assertEqual(request.data, {'name': '佚名'})
            request.encoding = 'GBK'
            self.assertEqual(request.POST, {'name': '浣氬悕'})

