'''
Testing the DNS resolver
'''
#!/usr/bin/python3


from random import seed
import pytest
from resolver import val_to_2_bytes
from resolver import val_to_n_bytes
from resolver import bytes_to_val
from resolver import get_2_bits
from resolver import get_offset
from resolver import parse_cli_query
from resolver import format_query
from resolver import parse_response
from resolver import parse_answers
from resolver import parse_address_a
from resolver import parse_address_aaaa

seed(430)


class TestResolver:
    '''Testing DNS resolver'''

    @pytest.fixture(scope='function', autouse=True)
    def setup_class(self):
        '''Setting up'''
        pass

    def test_val_to_bytes(self):
        '''Convert a value to 2 bytes'''
        assert val_to_2_bytes(43043) == [168, 35]
        assert val_to_n_bytes(430430, 3) == [6, 145, 94]

    def test_bytes_to_val(self):
        '''Convert a value to n bytes'''
        assert bytes_to_val([6, 145, 94]) == 430430

    def test_get_2_bits(self):
        '''Get 2 bits'''
        assert get_2_bits([200, 100]) == 3

    def test_get_offset(self):
        '''Get offset'''
        assert get_offset([200, 100]) == 2148

    def test_parse_cli_query(self):
        '''Parse command-line arguments'''
        assert parse_cli_query('resolver.py', 'A', 'luther.edu') == (1, ['luther', 'edu'], '8.26.56.26')
        assert parse_cli_query('resolver.py', 'A', 'luther.edu', '1.0.0.1') == (1, ['luther', 'edu'], '1.0.0.1')
        assert parse_cli_query('resolver.py', 'AAAA', 'luther.edu') == (28, ['luther', 'edu'], '8.8.4.4')
        with pytest.raises(ValueError) as excinfo:
            parse_cli_query('resolver.py', 'MX', 'luther.edu')
        exception_msg = excinfo.value.args[0]
        assert exception_msg == 'Unknown query type'

    def test_format_query(self):
        '''Format a query'''
        assert format_query(1, ['luther', 'edu']) == b'OB\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06luther\x03edu\x00\x00\x01\x00\x01'

    def test_parse_response(self):
        '''Parse the response'''
        assert parse_response(b'\xc7D\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x06luther\x03edu\x00\x00\x01' +
                              b'\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01,\x00\x04\xae\x81\x19\xaa') == \
                              [('luther.edu', 300, '174.129.25.170')]

        assert parse_response(b'k\xfb\x81\x80\x00\x01\x00\x06\x00\x00\x00\x00\x05yahoo\x03com' +
                              b'\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x04T\x00\x10 ' +
                              b'\x01I\x98\x00X\x186\x00\x00\x00\x00\x00\x00\x00\x11\xc0\x0c\x00\x1c' +
                              b'\x00\x01\x00\x00\x04T\x00\x10 \x01I\x98\x00X\x186\x00\x00\x00\x00\x00' +
                              b'\x00\x00\x10\xc0\x0c\x00\x1c\x00\x01\x00\x00\x04T\x00\x10 \x01I\x98' +
                              b'\x00D\x04\x1d\x00\x00\x00\x00\x00\x00\x00\x04\xc0\x0c\x00\x1c\x00' +
                              b'\x01\x00\x00\x04T\x00\x10 \x01I\x98\x00D\x04\x1d\x00\x00\x00\x00' +
                              b'\x00\x00\x00\x03\xc0\x0c\x00\x1c\x00\x01\x00\x00\x04T\x00\x10 \x01I' +
                              b'\x98\x00\x0c\x10#\x00\x00\x00\x00\x00\x00\x00\x05\xc0\x0c\x00\x1c' +
                              b'\x00\x01\x00\x00\x04T\x00\x10 \x01I\x98\x00\x0c\x10#\x00\x00\x00\x00\x00\x00\x00\x04') == \
                              [
                                  ('yahoo.com', 1108, '2001:4998:58:1836:0:0:0:11'),
                                  ('yahoo.com', 1108, '2001:4998:58:1836:0:0:0:10'),
                                  ('yahoo.com', 1108, '2001:4998:44:41d:0:0:0:4'),
                                  ('yahoo.com', 1108, '2001:4998:44:41d:0:0:0:3'),
                                  ('yahoo.com', 1108, '2001:4998:c:1023:0:0:0:5'),
                                  ('yahoo.com', 1108, '2001:4998:c:1023:0:0:0:4')
                              ]

    def test_parse_answers(self):
        '''Parse answers'''
        assert parse_answers(b'tH\x81\x80\x00\x01\x00\x01\x00\x03\x00\x01\x06luther\x03edu\x00\x00\x01\x00\x01' +
                             b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x01,\x00\x04\xae\x81\x19\xaa\xc0\x0c\x00\x02\x00' +
                             b'\x01\x00\x01Q\x80\x00\x10\x05dns-2\x07iastate\xc0\x13\xc0\x0c\x00\x02\x00\x01\x00' +
                             b'\x01Q\x80\x00\n\x03dns\x03uni\xc0\x13\xc0\x0c\x00\x02\x00\x01\x00\x01Q\x80\x00\t' +
                             b'\x06martin\xc0\x0c\xc0j\x00\x01\x00\x01\x00\x01Q\x80\x00\x04\xc0\xcb\xc4\x14', 28, 1) == \
                             [('luther.edu', 300, '174.129.25.170')]

        assert parse_answers(b'{\xae\x81\x80\x00\x01\x00\x06\x00\x05\x00\x08\x05yahoo\x03com' +
                             b'\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x04\xe9\x00' +
                             b'\x10 \x01I\x98\x00D\x04\x1d\x00\x00\x00\x00\x00\x00\x00\x04\xc0\x0c' +
                             b'\x00\x1c\x00\x01\x00\x00\x04\xe9\x00\x10 \x01I\x98\x00D\x04\x1d\x00' +
                             b'\x00\x00\x00\x00\x00\x00\x03\xc0\x0c\x00\x1c\x00\x01\x00\x00\x04\xe9' +
                             b'\x00\x10 \x01I\x98\x00X\x186\x00\x00\x00\x00\x00\x00\x00\x11\xc0\x0c' +
                             b'\x00\x1c\x00\x01\x00\x00\x04\xe9\x00\x10 \x01I\x98\x00\x0c\x10#\x00' +
                             b'\x00\x00\x00\x00\x00\x00\x04\xc0\x0c\x00\x1c\x00\x01\x00\x00\x04\xe9' +
                             b'\x00\x10 \x01I\x98\x00\x0c\x10#\x00\x00\x00\x00\x00\x00\x00\x05\xc0' +
                             b'\x0c\x00\x1c\x00\x01\x00\x00\x04\xe9\x00\x10 \x01I\x98\x00X\x186\x00' +
                             b'\x00\x00\x00\x00\x00\x00\x10\xc0\x0c\x00\x02\x00\x01\x00\x00s0\x00' +
                             b'\x06\x03ns1\xc0\x0c\xc0\x0c\x00\x02\x00\x01\x00\x00s0\x00\x06\x03ns3' +
                             b'\xc0\x0c\xc0\x0c\x00\x02\x00\x01\x00\x00s0\x00\x06\x03ns5\xc0\x0c\xc0' +
                             b'\x0c\x00\x02\x00\x01\x00\x00s0\x00\x06\x03ns2\xc0\x0c\xc0\x0c\x00\x02' +
                             b'\x00\x01\x00\x00s0\x00\x06\x03ns4\xc0\x0c\xc0\xcf\x00\x1c\x00\x01\x00' +
                             b'\x00CX\x00\x10 \x01I\x98\x010\x00\x00\x00\x00\x00\x00\x00\x00\x10\x01' +
                             b'\xc1\x05\x00\x1c\x00\x01\x00\x00\xda\xdb\x00\x10 \x01I\x98\x01@\x00' +
                             b'\x00\x00\x00\x00\x00\x00\x00\x10\x02\xc0\xe1\x00\x1c\x00\x01\x00\x00' +
                             b'\xd9\xb0\x00\x10$\x06\x86\x00\x00\xb8\xfe\x03\x00\x00\x00\x00\x00\x00' +
                             b'\x10\x03\xc0\xcf\x00\x01\x00\x01\x00\x11f\xdc\x00\x04D\xb4\x83\x10\xc1' +
                             b'\x05\x00\x01\x00\x01\x00\x11f\xde\x00\x04D\x8e\xff\x10\xc0\xe1\x00\x01' +
                             b'\x00\x01\x00\x0f\xfe\xc3\x00\x04\xcbT\xdd5\xc1\x17\x00\x01\x00\x01\x00' +
                             b'\x11\x8ah\x00\x04b\x8a\x0b\x9d\xc0\xf3\x00\x01\x00\x01\x00\x11PF\x00\x04w\xa0\xfdS', 27, 6) == \
                             [
                                 ('yahoo.com', 1257, '2001:4998:44:41d:0:0:0:4'),
                                 ('yahoo.com', 1257, '2001:4998:44:41d:0:0:0:3'),
                                 ('yahoo.com', 1257, '2001:4998:58:1836:0:0:0:11'),
                                 ('yahoo.com', 1257, '2001:4998:c:1023:0:0:0:4'),
                                 ('yahoo.com', 1257, '2001:4998:c:1023:0:0:0:5'),
                                 ('yahoo.com', 1257, '2001:4998:58:1836:0:0:0:10')
                             ]

    def test_parse_address_a(self):
        '''Parse IPv4 address'''
        assert parse_address_a(4, b'\xae\x81\x19\xaa') == '174.129.25.170'

    def test_parse_address_aaaa(self):
        '''Parse IPv6 address'''
        assert parse_address_aaaa(16, b' \x01I\x98\x00\x0c\x10#\x00\x00\x00\x00\x00\x00\x00\x04\xc0') == '2001:4998:c:1023:0:0:0:4'


if __name__ == '__main__':
    pytest.main(['test_resolver.py'])
