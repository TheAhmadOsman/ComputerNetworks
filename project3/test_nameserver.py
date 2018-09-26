'''
Testing the DNS Server
'''
#!/usr/bin/python3


from random import seed
import pytest
from nameserver import val_to_bytes
from nameserver import bytes_to_val
from nameserver import get_left_bits
from nameserver import get_right_bits
from nameserver import read_zone_file
from nameserver import parse_request
from nameserver import format_response

seed(430)


class TestServer:
    '''Testing DNS server'''

    @pytest.fixture(scope='function', autouse=True)
    def setup_class(self):
        '''Setting up'''
        self.zone = read_zone_file('zoo.zone')[1]

    def test_val_to_bytes(self):
        '''Convert a value to bytes'''
        assert val_to_bytes(43043, 2) == [168, 35]
        assert val_to_bytes(430430, 3) == [6, 145, 94]

    def test_bytes_to_val(self):
        '''Convert bytes to a value'''
        assert bytes_to_val([145, 94]) == 37214
        assert bytes_to_val([6, 145, 94]) == 430430

    def test_get_left_bits(self):
        '''Get left bits'''
        assert get_left_bits([200, 100], 2) == 3
        assert get_left_bits([200, 100], 4) == 12

    def test_get_right_bits(self):
        '''Get right bits'''
        assert get_right_bits([200, 100], 14) == 2148
        assert get_right_bits([200, 100], 6) == 36

    def test_read_zone_file(self):
        '''Read the zone file'''
        origin, zone = read_zone_file('zoo.zone')
        assert origin == 'cs430.luther.edu'
        assert len(zone) == 25

    def test_format_response(self):
        '''Format a response'''
        assert format_response(self.zone, 4783, 'ant', 1, b'\x03ant\x05cs430\x06luther\x03edu\x00\x00\x01\x00\x01') == \
                            b'\x12\xaf\x81\x00\x00\x01\x00\x02\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x0e\x10\x00\x04\xb9T\xe0Y\xc0\x0c\x00\x01\x00\x01\x00\x00\x0e\x10\x00\x04\xc7SC\x9e'

        assert format_response(self.zone, 55933, 'ant', 28, b'\x03ant\x05cs430\x06luther\x03edu\x00\x00\x1c\x00\x01') == \
                            b'\xda}\x81\x00\x00\x01\x00\x01\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x0e\x10\x00\x10J\x9ap\xec:\xc0\xc6\x845\x9e\x8d7\x94\x86YY'

    def test_parse_request(self):
        '''Parse the request'''
        assert parse_request('cs430.luther.edu', b'6\xc3\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x01\x00\x01') == \
                              (14019, 'ant', 1, b'\x03ant\x05cs430\x06luther\x03edu\x00\x00\x01\x00\x01')

        assert parse_request('cs430.luther.edu', b'i\xce\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x1c\x00\x01') == \
                              (27086, 'ant', 28, b'\x03ant\x05cs430\x06luther\x03edu\x00\x00\x1c\x00\x01')

    def test_parse_request_query_error(self):
        '''Query type is incorrect'''
        with pytest.raises(ValueError) as excinfo:
            parse_request('cs430.luther.edu', b'6\xc3\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x03\x00\x01')
        exception_msg = excinfo.value.args[0]
        assert exception_msg == 'Unknown query type'

    def test_parse_request_class_error(self):
        '''Query class is incorrect'''
        with pytest.raises(ValueError) as excinfo:
            parse_request('cs430.luther.edu', b'6\xc3\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x01\x00\x03')
        exception_msg = excinfo.value.args[0]
        assert exception_msg == 'Unknown class'

    def test_parse_request_query_zone(self):
        '''Query zone is incorrect'''
        with pytest.raises(ValueError) as excinfo:
            parse_request('luther.edu', b'6\xc3\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03ant\x05cs430\x06luther\x03edu\x00\x00\x01\x00\x01')
        exception_msg = excinfo.value.args[0]
        assert exception_msg == 'Unknown zone'

if __name__ == '__main__':
    pytest.main(['test_nameserver.py'])
