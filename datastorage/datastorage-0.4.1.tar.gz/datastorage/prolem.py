from datastorage import DataStorage as ds

someotherdata = ds(a=1,b=2,c="dsadasa")

data = ds(ciao=10)
data.added = ds(field=10)
print("are the same ?",data.added is data["added"])
data.addinganotherone="dsdadsa"
data.added.inside = 4
print("are the same ?",data.added is data["added"])
data["added"]["inside2"] = someotherdata
print("are the same ?",data.added is data["added"])
print(data)
print(dict(data))
