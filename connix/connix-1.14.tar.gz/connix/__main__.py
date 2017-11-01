from . import connix
import time

if __name__ == '__main__':
	""" If called directly, run through a number of sanity tests.
	"""
	print("Python3 util module v" + connix.__VERSION__ + " by Patrick Lambert")
	print("Testing functions...")
	print()
	connix._test("guid", [])
	connix._test("guid", [32])
	connix._test("in_tag", ["this random string is something, right?", "random", ","])
	connix._test("in_tag", ["<p>This is a link to <a href='http://google.com'>Google</a>.</p>", "a"])
	jsonfile = "/tmp/" + connix.guid() + ".json"
	data = {'name': "Hello world", 'results': ["test 1", "test 2", "test 3"]}
	connix._test("save", [jsonfile, data])
	connix._test("load", [jsonfile])
	connix._test("unixtime", [])
	connix._test("now", [])
	connix._test("hashfile", [jsonfile])
	connix._test("hashfile", ["/doesnotexist"])
	connix._test("error", [])
	connix._test("hash", ["Hello world"])
	connix._test("remote_ip", [])
	connix._test("form", [])
	connix._test("email", ["root@localhost", "root@localhost", "Test 1 2 3", "This is\na\ntest!"])
	connix._test("curl", ["http://google.com/does.not.exist"])
	connix._test("in_list", [[{'id': "1", 'text': "Hello world"}, {'id': "2", 'text': "World hello"}, {'id': "3", 'text': "!"}], "id", "4"])
	connix._test("remove_spaces", ["  This is  a test of   the \"emergency  broadcast system\". "])
	connix._test("cmd", ["ps aux | wc -l"])
	saveto = "/tmp/" + connix.guid() + ".html"
	connix._test("download", ["http://www.cnn.com", saveto])
	connix._test("alphanum", ["Some escape attempt\"); cat /etc/passwd", True, True])
	connix._test("list_files", ["/etc/httpd", "*.conf"])
	connix._test("ask", ["Type something", "nothing"])
	connix._test("args", [])
	connix._test("base36", [time.time()])
	connix._test("is_int", ["23523"])
	connix._test("is_float", ["364.234"])
	connix._test("bold", ["This is a bold statement"])
	connix._test("underline", ["A line underneath"])
	connix._test("remove_tags", ["The prices is <span style=\"color: #888888;\"><strike>$14.99</strike></span><br>"])
	connix._test("unixtime2datetime", [connix.unixtime()])
	connix._test("encrypt", ["MySecretKey", "This is a very secret phrase!"])
	data = connix.encrypt("MySecretKey", "This is a very secret phrase!")
	connix._test("decrypt", ["MySecretKey", data])
	connix._test("max_len", ["This text is too long to fit in the max len.", 25])
	connix._test("urlencode", ["Some AD&D, + some quotes?"])
