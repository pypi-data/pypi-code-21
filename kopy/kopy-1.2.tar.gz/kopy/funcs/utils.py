# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

jamo_start = 44032
jamo_end = 55203
cho_start = 4352
jung_start = 4449
jong_start = 4520
cho_list = [u"ㄱ",u"ㄲ",u"ㄴ",u"ㄷ",u"ㄸ",u"ㄹ",u"ㅁ",u"ㅂ",u"ㅃ",u"ㅅ",u"ㅆ",u"ㅇ",u"ㅈ",u"ㅉ",u"ㅊ",u"ㅋ",u"ㅌ",u"ㅍ",u"ㅎ"]
jung_list = [u"ㅏ",u"ㅐ",u"ㅑ",u"ㅒ",u"ㅓ",u"ㅔ",u"ㅕ",u"ㅖ",u"ㅗ",u"ㅘ",u"ㅙ",u"ㅚ",u"ㅛ",u"ㅜ",u"ㅝ",u"ㅞ",u"ㅟ",u"ㅠ",u"ㅡ",u"ㅢ",u"ㅣ"]
jong_list = [u"",u"ㄱ",u"ㄲ",u"ㄳ",u"ㄴ",u"ㄵ",u"ㄶ",u"ㄷ",u"ㄹ",u"ㄺ",u"ㄻ",u"ㄼ",u"ㄽ",u"ㄾ",u"ㄿ",u"ㅀ",u"ㅁ",u"ㅂ",u"ㅄ",u"ㅅ",u"ㅆ",u"ㅇ",u"ㅈ",u"ㅊ",u"ㅋ",u"ㅌ",u"ㅍ",u"ㅎ"]
jaum_list = list(set(cho_list+jong_list))
try:
	jong_before = [chr(i) for i in range(4520,4547)] # 분리된 종성 리스트
except:
	jong_before = [unichr(i) for i in range(4520, 4547)]

def getfilePath(*name):
	if name:
		return str(os.path.realpath(__file__).rsplit('/',1)[0]) + "/" + name[0]
	else:
		return str(os.path.realpath(__file__).rsplit('/',1)[0])

def isHangul(ch):
	return ord(ch) >= jamo_start and ord(ch) <= jamo_end

def isHangul2(ch):
	return ch in set(cho_list+jung_list+jong_list)

def splitK(words):
	result = ""
	for word in words:
		if isHangul(word):
			word = ord(word) - jamo_start
			cho = int(word / 21 /28)
			jung = int((word / 28) % 21)
			if word % 28 :
				jong =int(word % 28)
				result+=(cho_list[cho]+jung_list[jung]+jong_list[jong])
			else:
				result+=(cho_list[cho]+jung_list[jung])
		else :
			result+=word
	return result

def joinK(words):
	result = ""
	container = 0
	for i, word in enumerate(words):
		if len(words) == 1:
			return replace(words)
		if word in jaum_list:
			if (len(words)-1 == i) or (words[i+1] in cho_list) or (isHangul2(words[i+1]) == False) :
				if (i == 0) or (container == 0 and words[i-1] != u'ㅏ'):
					result += replace(word)
				else:
					num = [i for i, x in enumerate(jong_list) if x == word]
					num = num[0]
					try:
						result += chr(container+num+jamo_start)
					except:
						result += unichr(container + num + jamo_start)
					container = 0
			elif words[i+1] in jung_list:
				if i != 0:
					if container == 0:
						if words[i - 1] == u'ㅏ':
							try:
								result += chr(container + jamo_start)
							except:
								result += unichr(container + jamo_start)
							container = 0
					else:
						try:
							result += chr(container+jamo_start)
						except:
							result += unichr(container + jamo_start)
						container = 0
				num = [i for i, x in enumerate(cho_list) if x == word]
				num = (num[0]*588)
				container += num
		elif word in jung_list:
			num = [y for y, x in enumerate(jung_list) if x == word]
			num = num[0]*28
			container += num
			if (i+1 == len(words)) or (words[i+1] == " "):
				try:
					result += chr(container+jamo_start)
				except:
					result += unichr(container + jamo_start)
				container = 0
		else:
			if container != 0 or words[i - 1] == u'ㅏ':
				try:
					result += chr(container+jamo_start)
				except:
					result += unichr(container + jamo_start)
				container = 0
			result += word
	else:
		if container != 0:
			try:
				result += chr(container+jamo_start)
			except:
				result += unichr(container + jamo_start)
	return result

# 음소분된 종성 복구
def replace(line):
	for c,i in enumerate(jong_before):
		line = line.replace(i,jong_list[c+1])
	return line



if __name__ == "__main__":
	pass