"""
	이 파일은 연습 파일입니다
"""
'''
	요 것 도 주석
'''
# 요것도 주석
def print_lol(the_list):
	for item in the_list:
		if isinstance(item , list):
			print_lol(item)
		else:
			print(item)