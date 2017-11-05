from ifhotf import hfunc

#functions, classes here

def run(ifunction):
	#read data from stdin
	#	add max_request_size if payload+header length is bigger than 512
	req_input=ifunction.read()

	if req_input is not None:
		state=req_input[0]
		method=req_input[1]
		data=req_input[2]

		#if data is valid json, then run business logic
		if state is True:
			ifunction.out(200,{"data":data})
		#...and if data is NOT valid json, then do some fallback logic
		elif state is False:
			ifunction.out(500,{"data":data})

#main
ifunction=hfunc()
while True:
	run(ifunction)
