from ifhotf import hfunc

#functions, classes here

def run(ifunction):
	#read data from stdin
	#	add max_request_size if payload+header length is bigger than 512
	req_input=ifunction.read()

	if req_input is not None:
		state=req_input[0]
		data=req_input[1]

		#if data is valid json, then run business logic
		if state is True:
			b=1+1
			ifunction.out(200,{"data":data})
		#...and if data is NOT valid json, then do some fallback logic
		elif state is False:
			ifunction.out(500,{"data":data})

#main
ifunction=hfunc()
while True:
	run(ifunction)


"""payload example:


GET / HTTP/1.1
A: 1
B: 2
C: {"dict":"json"}
Content-Length: 21
Header_connection: close
Header_content_length: 21
Method: POST
Request_url: http//api:8080/r/test1/%2Fif
Route: /if
Task-Id: ecc40a4f-3ceb-5f3c-975c-8e817c589334

{"name":"EUGENETEST"}



"""
