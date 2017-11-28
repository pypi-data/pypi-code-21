import writer as w
import sys

if(sys.argv[1] == "--translate-to"):
	w.setClarissaSettingWithPath("Settings/translate.setting", "to", sys.argv[2])