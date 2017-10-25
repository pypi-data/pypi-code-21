#imports
import requests,lxml
from lxml import html
#end imports

#globals
global trm
#end globals

def supported():
	return ["btc", "eth", "ltc", "bch", "xmr","neo","sc","xrp","dash","xem","bcc","miota","doge"]
def btcX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/bitcoin/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')

	finstr = ''.join(final)
	#print (finstr)
	return finstr

def ethX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/ethereum/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr

def ltcX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/litecoin/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr

def bchX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/bitcoin-cash/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr

def xmrX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/monero/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def neoX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/neo/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def scX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/siacoin/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def xrpX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/ripple/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def dashX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/dash/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def xemX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/nem/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def bccX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/bitconnect/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def miotaX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/iota/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def dogeX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/dogecoin/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
def cannX():
	pageContent=requests.get("https://coinmarketcap.com/currencies/cannabiscoin/")
	tree = html.fromstring(pageContent.content)
	final = tree.xpath('//*[@id="quote_price"]//text()')
	
	finstr = ''.join(final)
	#print (finstr)
	return finstr
#if __name__ == "__main__": #moreeee debug testing
	#define("cow")
	#example("anime")