'''
Created on Jun 29, 2015

@author: aser
'''

from des_widgets import encrypter, decrypter

from nose.tools import assert_equal, assert_not_equal, assert_raises
class TestEncrypt():
    
    def test_encrypt(self):
        mykey = encrypter(astr = 'blahblahblah')
        assert_equal( mykey, '**DES**fc23c33f7ddf4413f7e2d888e9f63414')

    def test_encrypt_long(self):
        mykey = encrypter(astr = 'asdfssadfasdfasdfasdfasdfasdfasdfasdfasfasdfasdfasdfasdfasdfasdfasdfasdfasfd')
        
        assert_equal( mykey, '**DES**121be8d1c31fc731b67b7025dad22a59498819d6c65e308a61aa49732df3a5ddcdcab732c83463d77f4f75e8b18a6204a4c691bb1c648f6022a337da7e379825d37936e10093d492cce64df55f68931d')

    def test_encrypt_new_key(self):
        mykey = encrypter(astr = 'blahblahblah', des_key = 'test')
        assert_equal( mykey, '**DES**ca91db4c1688c413f17282ee17a0aac2')
        
        
        
    def test_decrypt(self):
        decrypted = decrypter(astr = '**DES**fc23c33f7ddf4413f7e2d888e9f63414')
        assert_equal( decrypted, 'blahblahblah')

    def test_decrypt_long(self):
        decrypted = decrypter(astr = '**DES**121be8d1c31fc731b67b7025dad22a59498819d6c65e308a61aa49732df3a5ddcdcab732c83463d77f4f75e8b18a6204a4c691bb1c648f6022a337da7e379825d37936e10093d492cce64df55f68931d')
        assert_equal( decrypted, 'asdfssadfasdfasdfasdfasdfasdfasdfasdfasfasdfasdfasdfasdfasdfasdfasdfasdfasfd')
        
    def test_decrypt_fail(self):
        decrypted = decrypter(astr = '**DES**fc23c33f7ddf4413f7e2d888e9f63414', des_key = 'test')
        assert_not_equal( decrypted, 'asdfssadfasdfasdfasdfasdfasdfasdfasdfasfasdfasdfasdfasdfasdfasdfasdfasdfasfd')
