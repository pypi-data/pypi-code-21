from adys import *
f = bn2smv("reseau1.bn", "async")
append_line(f, "CTLSPEC EF x3;")
append_line(f, "CTLSPEC x1 & x2 & !x3 -> EF x3;")
append_line(f, "CTLSPEC AF ((!x1&!x2&!x3)| (x1&x2&x3))")
append_line(f, "LTLSPEC F G ((!x1&!x2&!x3)|F (x1&x2&x3))")
NuSMV("reseau1-async.smv")
