# Generated from grammar/SignalFlowV2Lexer.g4 by ANTLR 4.5.2
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO


import re
from SignalFlowV2Parser import SignalFlowV2Parser
from antlr4.Token import CommonToken


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2")
        buf.write(u"J\u020d\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4")
        buf.write(u"\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r")
        buf.write(u"\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22")
        buf.write(u"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4")
        buf.write(u"\30\t\30\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35")
        buf.write(u"\t\35\4\36\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4")
        buf.write(u"$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t")
        buf.write(u",\4-\t-\4.\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63")
        buf.write(u"\t\63\4\64\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\4")
        buf.write(u"9\t9\4:\t:\4;\t;\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@\4A\tA")
        buf.write(u"\4B\tB\4C\tC\4D\tD\4E\tE\4F\tF\4G\tG\4H\tH\4I\tI\4J\t")
        buf.write(u"J\4K\tK\4L\tL\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\3\3")
        buf.write(u"\3\3\3\4\3\4\3\4\3\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\6")
        buf.write(u"\3\6\3\6\3\6\3\6\3\6\3\6\3\7\3\7\3\7\3\b\3\b\3\b\3\b")
        buf.write(u"\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\t\3\n")
        buf.write(u"\3\n\3\n\3\n\3\n\3\n\3\n\3\13\3\13\3\13\3\f\3\f\3\f\3")
        buf.write(u"\f\3\f\3\r\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16\3\16\3")
        buf.write(u"\16\3\17\3\17\3\17\3\17\3\20\3\20\3\20\3\21\3\21\3\21")
        buf.write(u"\3\21\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\22\3\23\3")
        buf.write(u"\23\3\23\3\23\3\23\3\24\3\24\3\24\3\24\3\24\3\24\3\24")
        buf.write(u"\3\25\3\25\3\25\3\25\3\25\3\25\3\25\3\26\3\26\3\26\3")
        buf.write(u"\27\3\27\3\27\3\27\3\30\3\30\3\30\3\30\3\31\3\31\3\31")
        buf.write(u"\3\32\3\32\3\32\3\32\3\32\3\33\3\33\3\33\3\33\3\33\3")
        buf.write(u"\34\3\34\3\34\3\34\3\34\3\34\3\35\3\35\3\35\3\35\3\35")
        buf.write(u"\3\35\3\36\3\36\3\36\3\36\3\36\3\36\3\37\3\37\3\37\3")
        buf.write(u"\37\3 \3 \3 \3 \3 \3!\3!\3!\3!\3!\3!\3!\3!\3!\3\"\3\"")
        buf.write(u"\3\"\3\"\3\"\3\"\3#\3#\3#\5#\u014f\n#\3#\3#\5#\u0153")
        buf.write(u"\n#\3#\5#\u0156\n#\5#\u0158\n#\3#\3#\3$\3$\7$\u015e\n")
        buf.write(u"$\f$\16$\u0161\13$\3%\3%\3%\7%\u0166\n%\f%\16%\u0169")
        buf.write(u"\13%\3%\3%\3%\3%\7%\u016f\n%\f%\16%\u0172\13%\3%\5%\u0175")
        buf.write(u"\n%\3&\6&\u0178\n&\r&\16&\u0179\3\'\7\'\u017d\n\'\f\'")
        buf.write(u"\16\'\u0180\13\'\3\'\5\'\u0183\n\'\3\'\6\'\u0186\n\'")
        buf.write(u"\r\'\16\'\u0187\3\'\3\'\5\'\u018c\n\'\3\'\6\'\u018f\n")
        buf.write(u"\'\r\'\16\'\u0190\5\'\u0193\n\'\3(\3(\3(\3(\3(\3(\3(")
        buf.write(u"\3(\5(\u019d\n(\3)\3)\3*\3*\3*\3*\3+\3+\3,\3,\3,\3-\3")
        buf.write(u"-\3-\3.\3.\3/\3/\3\60\3\60\3\61\3\61\3\61\3\62\3\62\3")
        buf.write(u"\63\3\63\3\63\3\64\3\64\3\64\3\65\3\65\3\66\3\66\3\67")
        buf.write(u"\3\67\38\38\38\39\39\39\3:\3:\3;\3;\3<\3<\3=\3=\3>\3")
        buf.write(u">\3>\3?\3?\3?\3@\3@\3A\3A\3B\3B\3B\3C\3C\3C\3D\3D\3D")
        buf.write(u"\3E\3E\3E\3F\3F\3F\3G\3G\3H\3H\3H\3I\6I\u01f1\nI\rI\16")
        buf.write(u"I\u01f2\3J\3J\3J\5J\u01f8\nJ\3J\3J\3K\3K\7K\u01fe\nK")
        buf.write(u"\fK\16K\u0201\13K\3L\3L\5L\u0205\nL\3L\5L\u0208\nL\3")
        buf.write(u"L\3L\5L\u020c\nL\2\2M\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21")
        buf.write(u"\n\23\13\25\f\27\r\31\16\33\17\35\20\37\21!\22#\23%\24")
        buf.write(u"\'\25)\26+\27-\30/\31\61\32\63\33\65\34\67\359\36;\37")
        buf.write(u"= ?!A\"C#E$G%I&K\'M(O\2Q)S*U+W,Y-[.]/_\60a\61c\62e\63")
        buf.write(u"g\64i\65k\66m\67o8q9s:u;w<y={>}?\177@\u0081A\u0083B\u0085")
        buf.write(u"C\u0087D\u0089E\u008bF\u008dG\u008fH\u0091\2\u0093I\u0095")
        buf.write(u"J\u0097\2\3\2\16\5\2C\\aac|\6\2\62;C\\aac|\6\2\f\f\17")
        buf.write(u"\17))^^\6\2\f\f\17\17$$^^\3\2\62;\4\2GGgg\4\2--//\n\2")
        buf.write(u"$$))^^ddhhppttvv\3\2\62\65\3\2\629\4\2\13\13\"\"\4\2")
        buf.write(u"\f\f\17\17\u0224\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2")
        buf.write(u"\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2")
        buf.write(u"\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2")
        buf.write(u"\31\3\2\2\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2")
        buf.write(u"!\3\2\2\2\2#\3\2\2\2\2%\3\2\2\2\2\'\3\2\2\2\2)\3\2\2")
        buf.write(u"\2\2+\3\2\2\2\2-\3\2\2\2\2/\3\2\2\2\2\61\3\2\2\2\2\63")
        buf.write(u"\3\2\2\2\2\65\3\2\2\2\2\67\3\2\2\2\29\3\2\2\2\2;\3\2")
        buf.write(u"\2\2\2=\3\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2\2\2E\3")
        buf.write(u"\2\2\2\2G\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2")
        buf.write(u"Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2")
        buf.write(u"\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2\2")
        buf.write(u"\2\2e\3\2\2\2\2g\3\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3\2")
        buf.write(u"\2\2\2o\3\2\2\2\2q\3\2\2\2\2s\3\2\2\2\2u\3\2\2\2\2w\3")
        buf.write(u"\2\2\2\2y\3\2\2\2\2{\3\2\2\2\2}\3\2\2\2\2\177\3\2\2\2")
        buf.write(u"\2\u0081\3\2\2\2\2\u0083\3\2\2\2\2\u0085\3\2\2\2\2\u0087")
        buf.write(u"\3\2\2\2\2\u0089\3\2\2\2\2\u008b\3\2\2\2\2\u008d\3\2")
        buf.write(u"\2\2\2\u008f\3\2\2\2\2\u0093\3\2\2\2\2\u0095\3\2\2\2")
        buf.write(u"\3\u0099\3\2\2\2\5\u009d\3\2\2\2\7\u00a4\3\2\2\2\t\u00aa")
        buf.write(u"\3\2\2\2\13\u00af\3\2\2\2\r\u00b6\3\2\2\2\17\u00b9\3")
        buf.write(u"\2\2\2\21\u00c0\3\2\2\2\23\u00c9\3\2\2\2\25\u00d0\3\2")
        buf.write(u"\2\2\27\u00d3\3\2\2\2\31\u00d8\3\2\2\2\33\u00dd\3\2\2")
        buf.write(u"\2\35\u00e3\3\2\2\2\37\u00e7\3\2\2\2!\u00ea\3\2\2\2#")
        buf.write(u"\u00ee\3\2\2\2%\u00f6\3\2\2\2\'\u00fb\3\2\2\2)\u0102")
        buf.write(u"\3\2\2\2+\u0109\3\2\2\2-\u010c\3\2\2\2/\u0110\3\2\2\2")
        buf.write(u"\61\u0114\3\2\2\2\63\u0117\3\2\2\2\65\u011c\3\2\2\2\67")
        buf.write(u"\u0121\3\2\2\29\u0127\3\2\2\2;\u012d\3\2\2\2=\u0133\3")
        buf.write(u"\2\2\2?\u0137\3\2\2\2A\u013c\3\2\2\2C\u0145\3\2\2\2E")
        buf.write(u"\u0157\3\2\2\2G\u015b\3\2\2\2I\u0174\3\2\2\2K\u0177\3")
        buf.write(u"\2\2\2M\u017e\3\2\2\2O\u0194\3\2\2\2Q\u019e\3\2\2\2S")
        buf.write(u"\u01a0\3\2\2\2U\u01a4\3\2\2\2W\u01a6\3\2\2\2Y\u01a9\3")
        buf.write(u"\2\2\2[\u01ac\3\2\2\2]\u01ae\3\2\2\2_\u01b0\3\2\2\2a")
        buf.write(u"\u01b2\3\2\2\2c\u01b5\3\2\2\2e\u01b7\3\2\2\2g\u01ba\3")
        buf.write(u"\2\2\2i\u01bd\3\2\2\2k\u01bf\3\2\2\2m\u01c1\3\2\2\2o")
        buf.write(u"\u01c3\3\2\2\2q\u01c6\3\2\2\2s\u01c9\3\2\2\2u\u01cb\3")
        buf.write(u"\2\2\2w\u01cd\3\2\2\2y\u01cf\3\2\2\2{\u01d1\3\2\2\2}")
        buf.write(u"\u01d4\3\2\2\2\177\u01d7\3\2\2\2\u0081\u01d9\3\2\2\2")
        buf.write(u"\u0083\u01db\3\2\2\2\u0085\u01de\3\2\2\2\u0087\u01e1")
        buf.write(u"\3\2\2\2\u0089\u01e4\3\2\2\2\u008b\u01e7\3\2\2\2\u008d")
        buf.write(u"\u01ea\3\2\2\2\u008f\u01ec\3\2\2\2\u0091\u01f0\3\2\2")
        buf.write(u"\2\u0093\u01f7\3\2\2\2\u0095\u01fb\3\2\2\2\u0097\u0202")
        buf.write(u"\3\2\2\2\u0099\u009a\7f\2\2\u009a\u009b\7g\2\2\u009b")
        buf.write(u"\u009c\7h\2\2\u009c\4\3\2\2\2\u009d\u009e\7t\2\2\u009e")
        buf.write(u"\u009f\7g\2\2\u009f\u00a0\7v\2\2\u00a0\u00a1\7w\2\2\u00a1")
        buf.write(u"\u00a2\7t\2\2\u00a2\u00a3\7p\2\2\u00a3\6\3\2\2\2\u00a4")
        buf.write(u"\u00a5\7t\2\2\u00a5\u00a6\7c\2\2\u00a6\u00a7\7k\2\2\u00a7")
        buf.write(u"\u00a8\7u\2\2\u00a8\u00a9\7g\2\2\u00a9\b\3\2\2\2\u00aa")
        buf.write(u"\u00ab\7h\2\2\u00ab\u00ac\7t\2\2\u00ac\u00ad\7q\2\2\u00ad")
        buf.write(u"\u00ae\7o\2\2\u00ae\n\3\2\2\2\u00af\u00b0\7k\2\2\u00b0")
        buf.write(u"\u00b1\7o\2\2\u00b1\u00b2\7r\2\2\u00b2\u00b3\7q\2\2\u00b3")
        buf.write(u"\u00b4\7t\2\2\u00b4\u00b5\7v\2\2\u00b5\f\3\2\2\2\u00b6")
        buf.write(u"\u00b7\7c\2\2\u00b7\u00b8\7u\2\2\u00b8\16\3\2\2\2\u00b9")
        buf.write(u"\u00ba\7i\2\2\u00ba\u00bb\7n\2\2\u00bb\u00bc\7q\2\2\u00bc")
        buf.write(u"\u00bd\7d\2\2\u00bd\u00be\7c\2\2\u00be\u00bf\7n\2\2\u00bf")
        buf.write(u"\20\3\2\2\2\u00c0\u00c1\7p\2\2\u00c1\u00c2\7q\2\2\u00c2")
        buf.write(u"\u00c3\7p\2\2\u00c3\u00c4\7n\2\2\u00c4\u00c5\7q\2\2\u00c5")
        buf.write(u"\u00c6\7e\2\2\u00c6\u00c7\7c\2\2\u00c7\u00c8\7n\2\2\u00c8")
        buf.write(u"\22\3\2\2\2\u00c9\u00ca\7c\2\2\u00ca\u00cb\7u\2\2\u00cb")
        buf.write(u"\u00cc\7u\2\2\u00cc\u00cd\7g\2\2\u00cd\u00ce\7t\2\2\u00ce")
        buf.write(u"\u00cf\7v\2\2\u00cf\24\3\2\2\2\u00d0\u00d1\7k\2\2\u00d1")
        buf.write(u"\u00d2\7h\2\2\u00d2\26\3\2\2\2\u00d3\u00d4\7g\2\2\u00d4")
        buf.write(u"\u00d5\7n\2\2\u00d5\u00d6\7k\2\2\u00d6\u00d7\7h\2\2\u00d7")
        buf.write(u"\30\3\2\2\2\u00d8\u00d9\7g\2\2\u00d9\u00da\7n\2\2\u00da")
        buf.write(u"\u00db\7u\2\2\u00db\u00dc\7g\2\2\u00dc\32\3\2\2\2\u00dd")
        buf.write(u"\u00de\7y\2\2\u00de\u00df\7j\2\2\u00df\u00e0\7k\2\2\u00e0")
        buf.write(u"\u00e1\7n\2\2\u00e1\u00e2\7g\2\2\u00e2\34\3\2\2\2\u00e3")
        buf.write(u"\u00e4\7h\2\2\u00e4\u00e5\7q\2\2\u00e5\u00e6\7t\2\2\u00e6")
        buf.write(u"\36\3\2\2\2\u00e7\u00e8\7k\2\2\u00e8\u00e9\7p\2\2\u00e9")
        buf.write(u" \3\2\2\2\u00ea\u00eb\7v\2\2\u00eb\u00ec\7t\2\2\u00ec")
        buf.write(u"\u00ed\7{\2\2\u00ed\"\3\2\2\2\u00ee\u00ef\7h\2\2\u00ef")
        buf.write(u"\u00f0\7k\2\2\u00f0\u00f1\7p\2\2\u00f1\u00f2\7c\2\2\u00f2")
        buf.write(u"\u00f3\7n\2\2\u00f3\u00f4\7n\2\2\u00f4\u00f5\7{\2\2\u00f5")
        buf.write(u"$\3\2\2\2\u00f6\u00f7\7y\2\2\u00f7\u00f8\7k\2\2\u00f8")
        buf.write(u"\u00f9\7v\2\2\u00f9\u00fa\7j\2\2\u00fa&\3\2\2\2\u00fb")
        buf.write(u"\u00fc\7g\2\2\u00fc\u00fd\7z\2\2\u00fd\u00fe\7e\2\2\u00fe")
        buf.write(u"\u00ff\7g\2\2\u00ff\u0100\7r\2\2\u0100\u0101\7v\2\2\u0101")
        buf.write(u"(\3\2\2\2\u0102\u0103\7n\2\2\u0103\u0104\7c\2\2\u0104")
        buf.write(u"\u0105\7o\2\2\u0105\u0106\7d\2\2\u0106\u0107\7f\2\2\u0107")
        buf.write(u"\u0108\7c\2\2\u0108*\3\2\2\2\u0109\u010a\7q\2\2\u010a")
        buf.write(u"\u010b\7t\2\2\u010b,\3\2\2\2\u010c\u010d\7c\2\2\u010d")
        buf.write(u"\u010e\7p\2\2\u010e\u010f\7f\2\2\u010f.\3\2\2\2\u0110")
        buf.write(u"\u0111\7p\2\2\u0111\u0112\7q\2\2\u0112\u0113\7v\2\2\u0113")
        buf.write(u"\60\3\2\2\2\u0114\u0115\7k\2\2\u0115\u0116\7u\2\2\u0116")
        buf.write(u"\62\3\2\2\2\u0117\u0118\7P\2\2\u0118\u0119\7q\2\2\u0119")
        buf.write(u"\u011a\7p\2\2\u011a\u011b\7g\2\2\u011b\64\3\2\2\2\u011c")
        buf.write(u"\u011d\7V\2\2\u011d\u011e\7t\2\2\u011e\u011f\7w\2\2\u011f")
        buf.write(u"\u0120\7g\2\2\u0120\66\3\2\2\2\u0121\u0122\7H\2\2\u0122")
        buf.write(u"\u0123\7c\2\2\u0123\u0124\7n\2\2\u0124\u0125\7u\2\2\u0125")
        buf.write(u"\u0126\7g\2\2\u01268\3\2\2\2\u0127\u0128\7e\2\2\u0128")
        buf.write(u"\u0129\7n\2\2\u0129\u012a\7c\2\2\u012a\u012b\7u\2\2\u012b")
        buf.write(u"\u012c\7u\2\2\u012c:\3\2\2\2\u012d\u012e\7{\2\2\u012e")
        buf.write(u"\u012f\7k\2\2\u012f\u0130\7g\2\2\u0130\u0131\7n\2\2\u0131")
        buf.write(u"\u0132\7f\2\2\u0132<\3\2\2\2\u0133\u0134\7f\2\2\u0134")
        buf.write(u"\u0135\7g\2\2\u0135\u0136\7n\2\2\u0136>\3\2\2\2\u0137")
        buf.write(u"\u0138\7r\2\2\u0138\u0139\7c\2\2\u0139\u013a\7u\2\2\u013a")
        buf.write(u"\u013b\7u\2\2\u013b@\3\2\2\2\u013c\u013d\7e\2\2\u013d")
        buf.write(u"\u013e\7q\2\2\u013e\u013f\7p\2\2\u013f\u0140\7v\2\2\u0140")
        buf.write(u"\u0141\7k\2\2\u0141\u0142\7p\2\2\u0142\u0143\7w\2\2\u0143")
        buf.write(u"\u0144\7g\2\2\u0144B\3\2\2\2\u0145\u0146\7d\2\2\u0146")
        buf.write(u"\u0147\7t\2\2\u0147\u0148\7g\2\2\u0148\u0149\7c\2\2\u0149")
        buf.write(u"\u014a\7m\2\2\u014aD\3\2\2\2\u014b\u014c\6#\2\2\u014c")
        buf.write(u"\u0158\5\u0091I\2\u014d\u014f\7\17\2\2\u014e\u014d\3")
        buf.write(u"\2\2\2\u014e\u014f\3\2\2\2\u014f\u0150\3\2\2\2\u0150")
        buf.write(u"\u0153\7\f\2\2\u0151\u0153\7\17\2\2\u0152\u014e\3\2\2")
        buf.write(u"\2\u0152\u0151\3\2\2\2\u0153\u0155\3\2\2\2\u0154\u0156")
        buf.write(u"\5\u0091I\2\u0155\u0154\3\2\2\2\u0155\u0156\3\2\2\2\u0156")
        buf.write(u"\u0158\3\2\2\2\u0157\u014b\3\2\2\2\u0157\u0152\3\2\2")
        buf.write(u"\2\u0158\u0159\3\2\2\2\u0159\u015a\b#\2\2\u015aF\3\2")
        buf.write(u"\2\2\u015b\u015f\t\2\2\2\u015c\u015e\t\3\2\2\u015d\u015c")
        buf.write(u"\3\2\2\2\u015e\u0161\3\2\2\2\u015f\u015d\3\2\2\2\u015f")
        buf.write(u"\u0160\3\2\2\2\u0160H\3\2\2\2\u0161\u015f\3\2\2\2\u0162")
        buf.write(u"\u0167\7)\2\2\u0163\u0166\5O(\2\u0164\u0166\n\4\2\2\u0165")
        buf.write(u"\u0163\3\2\2\2\u0165\u0164\3\2\2\2\u0166\u0169\3\2\2")
        buf.write(u"\2\u0167\u0165\3\2\2\2\u0167\u0168\3\2\2\2\u0168\u016a")
        buf.write(u"\3\2\2\2\u0169\u0167\3\2\2\2\u016a\u0175\7)\2\2\u016b")
        buf.write(u"\u0170\7$\2\2\u016c\u016f\5O(\2\u016d\u016f\n\5\2\2\u016e")
        buf.write(u"\u016c\3\2\2\2\u016e\u016d\3\2\2\2\u016f\u0172\3\2\2")
        buf.write(u"\2\u0170\u016e\3\2\2\2\u0170\u0171\3\2\2\2\u0171\u0173")
        buf.write(u"\3\2\2\2\u0172\u0170\3\2\2\2\u0173\u0175\7$\2\2\u0174")
        buf.write(u"\u0162\3\2\2\2\u0174\u016b\3\2\2\2\u0175J\3\2\2\2\u0176")
        buf.write(u"\u0178\t\6\2\2\u0177\u0176\3\2\2\2\u0178\u0179\3\2\2")
        buf.write(u"\2\u0179\u0177\3\2\2\2\u0179\u017a\3\2\2\2\u017aL\3\2")
        buf.write(u"\2\2\u017b\u017d\t\6\2\2\u017c\u017b\3\2\2\2\u017d\u0180")
        buf.write(u"\3\2\2\2\u017e\u017c\3\2\2\2\u017e\u017f\3\2\2\2\u017f")
        buf.write(u"\u0182\3\2\2\2\u0180\u017e\3\2\2\2\u0181\u0183\7\60\2")
        buf.write(u"\2\u0182\u0181\3\2\2\2\u0182\u0183\3\2\2\2\u0183\u0185")
        buf.write(u"\3\2\2\2\u0184\u0186\t\6\2\2\u0185\u0184\3\2\2\2\u0186")
        buf.write(u"\u0187\3\2\2\2\u0187\u0185\3\2\2\2\u0187\u0188\3\2\2")
        buf.write(u"\2\u0188\u0192\3\2\2\2\u0189\u018b\t\7\2\2\u018a\u018c")
        buf.write(u"\t\b\2\2\u018b\u018a\3\2\2\2\u018b\u018c\3\2\2\2\u018c")
        buf.write(u"\u018e\3\2\2\2\u018d\u018f\t\6\2\2\u018e\u018d\3\2\2")
        buf.write(u"\2\u018f\u0190\3\2\2\2\u0190\u018e\3\2\2\2\u0190\u0191")
        buf.write(u"\3\2\2\2\u0191\u0193\3\2\2\2\u0192\u0189\3\2\2\2\u0192")
        buf.write(u"\u0193\3\2\2\2\u0193N\3\2\2\2\u0194\u019c\7^\2\2\u0195")
        buf.write(u"\u019d\t\t\2\2\u0196\u0197\t\n\2\2\u0197\u0198\t\13\2")
        buf.write(u"\2\u0198\u019d\t\13\2\2\u0199\u019a\t\13\2\2\u019a\u019d")
        buf.write(u"\t\13\2\2\u019b\u019d\t\13\2\2\u019c\u0195\3\2\2\2\u019c")
        buf.write(u"\u0196\3\2\2\2\u019c\u0199\3\2\2\2\u019c\u019b\3\2\2")
        buf.write(u"\2\u019dP\3\2\2\2\u019e\u019f\7\60\2\2\u019fR\3\2\2\2")
        buf.write(u"\u01a0\u01a1\7\60\2\2\u01a1\u01a2\7\60\2\2\u01a2\u01a3")
        buf.write(u"\7\60\2\2\u01a3T\3\2\2\2\u01a4\u01a5\7,\2\2\u01a5V\3")
        buf.write(u"\2\2\2\u01a6\u01a7\7*\2\2\u01a7\u01a8\b,\3\2\u01a8X\3")
        buf.write(u"\2\2\2\u01a9\u01aa\7+\2\2\u01aa\u01ab\b-\4\2\u01abZ\3")
        buf.write(u"\2\2\2\u01ac\u01ad\7.\2\2\u01ad\\\3\2\2\2\u01ae\u01af")
        buf.write(u"\7<\2\2\u01af^\3\2\2\2\u01b0\u01b1\7=\2\2\u01b1`\3\2")
        buf.write(u"\2\2\u01b2\u01b3\7,\2\2\u01b3\u01b4\7,\2\2\u01b4b\3\2")
        buf.write(u"\2\2\u01b5\u01b6\7?\2\2\u01b6d\3\2\2\2\u01b7\u01b8\7")
        buf.write(u"]\2\2\u01b8\u01b9\b\63\5\2\u01b9f\3\2\2\2\u01ba\u01bb")
        buf.write(u"\7_\2\2\u01bb\u01bc\b\64\6\2\u01bch\3\2\2\2\u01bd\u01be")
        buf.write(u"\7~\2\2\u01bej\3\2\2\2\u01bf\u01c0\7`\2\2\u01c0l\3\2")
        buf.write(u"\2\2\u01c1\u01c2\7(\2\2\u01c2n\3\2\2\2\u01c3\u01c4\7")
        buf.write(u">\2\2\u01c4\u01c5\7>\2\2\u01c5p\3\2\2\2\u01c6\u01c7\7")
        buf.write(u"@\2\2\u01c7\u01c8\7@\2\2\u01c8r\3\2\2\2\u01c9\u01ca\7")
        buf.write(u"-\2\2\u01cat\3\2\2\2\u01cb\u01cc\7/\2\2\u01ccv\3\2\2")
        buf.write(u"\2\u01cd\u01ce\7\61\2\2\u01cex\3\2\2\2\u01cf\u01d0\7")
        buf.write(u"\u0080\2\2\u01d0z\3\2\2\2\u01d1\u01d2\7}\2\2\u01d2\u01d3")
        buf.write(u"\b>\7\2\u01d3|\3\2\2\2\u01d4\u01d5\7\177\2\2\u01d5\u01d6")
        buf.write(u"\b?\b\2\u01d6~\3\2\2\2\u01d7\u01d8\7>\2\2\u01d8\u0080")
        buf.write(u"\3\2\2\2\u01d9\u01da\7@\2\2\u01da\u0082\3\2\2\2\u01db")
        buf.write(u"\u01dc\7?\2\2\u01dc\u01dd\7?\2\2\u01dd\u0084\3\2\2\2")
        buf.write(u"\u01de\u01df\7@\2\2\u01df\u01e0\7?\2\2\u01e0\u0086\3")
        buf.write(u"\2\2\2\u01e1\u01e2\7>\2\2\u01e2\u01e3\7?\2\2\u01e3\u0088")
        buf.write(u"\3\2\2\2\u01e4\u01e5\7>\2\2\u01e5\u01e6\7@\2\2\u01e6")
        buf.write(u"\u008a\3\2\2\2\u01e7\u01e8\7#\2\2\u01e8\u01e9\7?\2\2")
        buf.write(u"\u01e9\u008c\3\2\2\2\u01ea\u01eb\7B\2\2\u01eb\u008e\3")
        buf.write(u"\2\2\2\u01ec\u01ed\7/\2\2\u01ed\u01ee\7@\2\2\u01ee\u0090")
        buf.write(u"\3\2\2\2\u01ef\u01f1\t\f\2\2\u01f0\u01ef\3\2\2\2\u01f1")
        buf.write(u"\u01f2\3\2\2\2\u01f2\u01f0\3\2\2\2\u01f2\u01f3\3\2\2")
        buf.write(u"\2\u01f3\u0092\3\2\2\2\u01f4\u01f8\5\u0091I\2\u01f5\u01f8")
        buf.write(u"\5\u0095K\2\u01f6\u01f8\5\u0097L\2\u01f7\u01f4\3\2\2")
        buf.write(u"\2\u01f7\u01f5\3\2\2\2\u01f7\u01f6\3\2\2\2\u01f8\u01f9")
        buf.write(u"\3\2\2\2\u01f9\u01fa\bJ\t\2\u01fa\u0094\3\2\2\2\u01fb")
        buf.write(u"\u01ff\7%\2\2\u01fc\u01fe\n\r\2\2\u01fd\u01fc\3\2\2\2")
        buf.write(u"\u01fe\u0201\3\2\2\2\u01ff\u01fd\3\2\2\2\u01ff\u0200")
        buf.write(u"\3\2\2\2\u0200\u0096\3\2\2\2\u0201\u01ff\3\2\2\2\u0202")
        buf.write(u"\u0204\7^\2\2\u0203\u0205\5\u0091I\2\u0204\u0203\3\2")
        buf.write(u"\2\2\u0204\u0205\3\2\2\2\u0205\u020b\3\2\2\2\u0206\u0208")
        buf.write(u"\7\17\2\2\u0207\u0206\3\2\2\2\u0207\u0208\3\2\2\2\u0208")
        buf.write(u"\u0209\3\2\2\2\u0209\u020c\7\f\2\2\u020a\u020c\7\17\2")
        buf.write(u"\2\u020b\u0207\3\2\2\2\u020b\u020a\3\2\2\2\u020c\u0098")
        buf.write(u"\3\2\2\2\33\2\u014e\u0152\u0155\u0157\u015f\u0165\u0167")
        buf.write(u"\u016e\u0170\u0174\u0179\u017e\u0182\u0187\u018b\u0190")
        buf.write(u"\u0192\u019c\u01f2\u01f7\u01ff\u0204\u0207\u020b\n\3")
        buf.write(u"#\2\3,\3\3-\4\3\63\5\3\64\6\3>\7\3?\b\b\2\2")
        return buf.getvalue()


class SignalFlowV2Lexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    DEF = 1
    RETURN = 2
    RAISE = 3
    FROM = 4
    IMPORT = 5
    AS = 6
    GLOBAL = 7
    NONLOCAL = 8
    ASSERT = 9
    IF = 10
    ELIF = 11
    ELSE = 12
    WHILE = 13
    FOR = 14
    IN = 15
    TRY = 16
    FINALLY = 17
    WITH = 18
    EXCEPT = 19
    LAMBDA = 20
    OR = 21
    AND = 22
    NOT = 23
    IS = 24
    NONE = 25
    TRUE = 26
    FALSE = 27
    CLASS = 28
    YIELD = 29
    DEL = 30
    PASS = 31
    CONTINUE = 32
    BREAK = 33
    NEWLINE = 34
    ID = 35
    STRING = 36
    INT = 37
    FLOAT = 38
    DOT = 39
    ELLIPSE = 40
    STAR = 41
    OPEN_PAREN = 42
    CLOSE_PAREN = 43
    COMMA = 44
    COLON = 45
    SEMICOLON = 46
    POWER = 47
    ASSIGN = 48
    OPEN_BRACK = 49
    CLOSE_BRACK = 50
    OR_OP = 51
    XOR = 52
    AND_OP = 53
    LEFT_SHIFT = 54
    RIGHT_SHIFT = 55
    ADD = 56
    MINUS = 57
    DIV = 58
    NOT_OP = 59
    OPEN_BRACE = 60
    CLOSE_BRACE = 61
    LESS_THAN = 62
    GREATER_THAN = 63
    EQUALS = 64
    GT_EQ = 65
    LT_EQ = 66
    NOT_EQ_1 = 67
    NOT_EQ_2 = 68
    AT = 69
    ARROW = 70
    SKIP_ = 71
    COMMENT = 72

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'def'", u"'return'", u"'raise'", u"'from'", u"'import'", u"'as'", 
            u"'global'", u"'nonlocal'", u"'assert'", u"'if'", u"'elif'", 
            u"'else'", u"'while'", u"'for'", u"'in'", u"'try'", u"'finally'", 
            u"'with'", u"'except'", u"'lambda'", u"'or'", u"'and'", u"'not'", 
            u"'is'", u"'None'", u"'True'", u"'False'", u"'class'", u"'yield'", 
            u"'del'", u"'pass'", u"'continue'", u"'break'", u"'.'", u"'...'", 
            u"'*'", u"'('", u"')'", u"','", u"':'", u"';'", u"'**'", u"'='", 
            u"'['", u"']'", u"'|'", u"'^'", u"'&'", u"'<<'", u"'>>'", u"'+'", 
            u"'-'", u"'/'", u"'~'", u"'{'", u"'}'", u"'<'", u"'>'", u"'=='", 
            u"'>='", u"'<='", u"'<>'", u"'!='", u"'@'", u"'->'" ]

    symbolicNames = [ u"<INVALID>",
            u"DEF", u"RETURN", u"RAISE", u"FROM", u"IMPORT", u"AS", u"GLOBAL", 
            u"NONLOCAL", u"ASSERT", u"IF", u"ELIF", u"ELSE", u"WHILE", u"FOR", 
            u"IN", u"TRY", u"FINALLY", u"WITH", u"EXCEPT", u"LAMBDA", u"OR", 
            u"AND", u"NOT", u"IS", u"NONE", u"TRUE", u"FALSE", u"CLASS", 
            u"YIELD", u"DEL", u"PASS", u"CONTINUE", u"BREAK", u"NEWLINE", 
            u"ID", u"STRING", u"INT", u"FLOAT", u"DOT", u"ELLIPSE", u"STAR", 
            u"OPEN_PAREN", u"CLOSE_PAREN", u"COMMA", u"COLON", u"SEMICOLON", 
            u"POWER", u"ASSIGN", u"OPEN_BRACK", u"CLOSE_BRACK", u"OR_OP", 
            u"XOR", u"AND_OP", u"LEFT_SHIFT", u"RIGHT_SHIFT", u"ADD", u"MINUS", 
            u"DIV", u"NOT_OP", u"OPEN_BRACE", u"CLOSE_BRACE", u"LESS_THAN", 
            u"GREATER_THAN", u"EQUALS", u"GT_EQ", u"LT_EQ", u"NOT_EQ_1", 
            u"NOT_EQ_2", u"AT", u"ARROW", u"SKIP_", u"COMMENT" ]

    ruleNames = [ u"DEF", u"RETURN", u"RAISE", u"FROM", u"IMPORT", u"AS", 
                  u"GLOBAL", u"NONLOCAL", u"ASSERT", u"IF", u"ELIF", u"ELSE", 
                  u"WHILE", u"FOR", u"IN", u"TRY", u"FINALLY", u"WITH", 
                  u"EXCEPT", u"LAMBDA", u"OR", u"AND", u"NOT", u"IS", u"NONE", 
                  u"TRUE", u"FALSE", u"CLASS", u"YIELD", u"DEL", u"PASS", 
                  u"CONTINUE", u"BREAK", u"NEWLINE", u"ID", u"STRING", u"INT", 
                  u"FLOAT", u"ESCAPE_SEQ", u"DOT", u"ELLIPSE", u"STAR", 
                  u"OPEN_PAREN", u"CLOSE_PAREN", u"COMMA", u"COLON", u"SEMICOLON", 
                  u"POWER", u"ASSIGN", u"OPEN_BRACK", u"CLOSE_BRACK", u"OR_OP", 
                  u"XOR", u"AND_OP", u"LEFT_SHIFT", u"RIGHT_SHIFT", u"ADD", 
                  u"MINUS", u"DIV", u"NOT_OP", u"OPEN_BRACE", u"CLOSE_BRACE", 
                  u"LESS_THAN", u"GREATER_THAN", u"EQUALS", u"GT_EQ", u"LT_EQ", 
                  u"NOT_EQ_1", u"NOT_EQ_2", u"AT", u"ARROW", u"SPACES", 
                  u"SKIP_", u"COMMENT", u"LINE_JOINING" ]

    grammarFileName = u"SignalFlowV2Lexer.g4"

    def __init__(self, input=None):
        super(SignalFlowV2Lexer, self).__init__(input)
        self.checkVersion("4.5.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


        # A queue where extra tokens are pushed on (see the NEWLINE lexer rule).
        self.tokens = []

        # The stack that keeps track of the indentation level.
        self.indents = []

        # The amount of opened braces, brackets and parenthesis.
        self.opened = 0

        # The most recently produced token.
        self.lastToken = None

    def emitToken(self, t):
        self._token = t
        self.tokens.append(t)

    def nextToken(self):
        # Check if the end-of-file is ahead and there are still some DEDENTS expected.
        if self._input.LA(1) == SignalFlowV2Parser.EOF and self.indents:

            # Remove any trailing EOF tokens from our buffer.
            for i in range(len(self.tokens) -1, -1, -1):
                if (self.tokens[i].type == SignalFlowV2Parser.EOF):
                    del self.tokens[i]

            # First emit an extra line break that serves as the end of the statement.
            self.emitToken(self.commonToken(SignalFlowV2Parser.NEWLINE, "\n"))

            # Now emit as many DEDENT tokens as needed.
            while self.indents:
                self.emitToken(self.createDedent());
                self.indents.pop()

            # Put the EOF back on the token stream.
            self.emitToken(self.commonToken(SignalFlowV2Parser.EOF, "<EOF>"))

        next = Lexer.nextToken(self)

        if next.channel == Token.DEFAULT_CHANNEL:
            # Keep track of the last token on the default channel.
            self.lastToken = next

        return next if not self.tokens else self.tokens.pop(0)

    def createDedent(self):
        dedent = self.commonToken(SignalFlowV2Parser.DEDENT, "")
        dedent.line = self.lastToken.line
        return dedent

    def commonToken(self, type, text):
        stop = self.getCharIndex() - 1
        start = stop if not text else stop - len(text) + 1
        return CommonToken(self._tokenFactorySourcePair, type, self.DEFAULT_TOKEN_CHANNEL, start, stop)

    ## Calculates the indentation of the provided whiteSpace, taking the
    ## following rules into account:
    ##
    ## "Tabs are replaced (from left to right) by one to eight spaces
    ##  such that the total number of characters up to and including
    ##  the replacement is a multiple of eight [...]"
    ##
    ##  -- https://docs.python.org/3.1/reference/lexical_analysis.html#indentation
    @staticmethod
    def getIndentationCount(whiteSpace):
        count = 0;
        for ch in whiteSpace:
            if '\t' == ch:
                count += 8 - (count % 8)
            else:
                count += 1
        return count

    def atStartOfInput(self):
        return self.column == 0 and self.line == 1


    def action(self, localctx, ruleIndex, actionIndex):
    	if self._actions is None:
    		actions = dict()
    		actions[33] = self.NEWLINE_action 
    		actions[42] = self.OPEN_PAREN_action 
    		actions[43] = self.CLOSE_PAREN_action 
    		actions[49] = self.OPEN_BRACK_action 
    		actions[50] = self.CLOSE_BRACK_action 
    		actions[60] = self.OPEN_BRACE_action 
    		actions[61] = self.CLOSE_BRACE_action 
    		self._actions = actions
    	action = self._actions.get(ruleIndex, None)
    	if action is not None:
    		action(localctx, actionIndex)
    	else:
    		raise Exception("No registered action for:" + str(ruleIndex))

    def NEWLINE_action(self, localctx , actionIndex):
        if actionIndex == 0:

            newLine = re.sub("[^\r\n]+", "", self.text)
            whiteSpaces = re.sub("[\r\n]+", "", self.text)
            next = self._input.LA(1)
            if self.opened > 0 or next == '\r' or next == '\n' or next == '#':
                # If we are inside a list or on a blank line, ignore all indents,
                # dedents and line breaks.
                self.skip()
            else:
                self.emitToken(self.commonToken(SignalFlowV2Lexer.NEWLINE, newLine));
                indent = SignalFlowV2Lexer.getIndentationCount(whiteSpaces);
                previous = 0 if not self.indents else self.indents[-1]
                if indent == previous:
                    # skip indents of the same size as the present indent-size
                    self.skip()

                elif indent > previous:
                    self.indents.append(indent)
                    self.emitToken(self.commonToken(SignalFlowV2Parser.INDENT, whiteSpaces))
                else:
                    # Possibly emit more than 1 DEDENT token.
                    while self.indents and self.indents[-1] > indent:
                        self.emitToken(self.createDedent())
                        self.indents.pop()
                
     

    def OPEN_PAREN_action(self, localctx , actionIndex):
        if actionIndex == 1:
            self.opened += 1
     

    def CLOSE_PAREN_action(self, localctx , actionIndex):
        if actionIndex == 2:
            self.opened -= 1
     

    def OPEN_BRACK_action(self, localctx , actionIndex):
        if actionIndex == 3:
            self.opened += 1
     

    def CLOSE_BRACK_action(self, localctx , actionIndex):
        if actionIndex == 4:
            self.opened -= 1
     

    def OPEN_BRACE_action(self, localctx , actionIndex):
        if actionIndex == 5:
            self.opened += 1
     

    def CLOSE_BRACE_action(self, localctx , actionIndex):
        if actionIndex == 6:
            self.opened -= 1
     

    def sempred(self, localctx, ruleIndex, predIndex):
        if self._predicates is None:
            preds = dict()
            preds[33] = self.NEWLINE_sempred
            self._predicates = preds
        pred = self._predicates.get(ruleIndex, None)
        if pred is not None:
            return pred(localctx, predIndex)
        else:
            raise Exception("No registered predicate for:" + str(ruleIndex))

    def NEWLINE_sempred(self, localctx, predIndex):
            if predIndex == 0:
                return self.atStartOfInput()
         


