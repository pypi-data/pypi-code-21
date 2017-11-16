
def toSurfaceDict(slab):
    res = {}
    res["Type"] = "Surface"

    # 基本参数
    Name = slab.formula.upper().replace(" ", "")
    res["Name"] = Name
    res["Formula"] = Name
    res["NumberOfSites"] = len(slab.sites)
    # 写晶格常数
    LatticeParameters = []
    LatticeParameters.append(slab.lattice.a)
    LatticeParameters.append(slab.lattice.b)
    LatticeParameters.append(slab.lattice.c)
    LatticeParameters.append(slab.lattice.alpha)
    LatticeParameters.append(slab.lattice.beta)
    LatticeParameters.append(slab.lattice.gamma)
    res["LatticeParameters"] = LatticeParameters

    res["Lattice"] = slab.lattice.matrix.tolist()

    sites = []

    for i in slab.sites:
        dict = i.as_dict()
        sites.append({'element': dict['species'][0]['element'],
                      'x': dict['abc'][0],
                      'y': dict['abc'][1],
                      'z': dict['abc'][2]})
    res['sites'] = sites
    return res

def toAbsorbSitesDict(originalDict):
    res = {}
    name = ["all", "bridge", "ontop", "hollow"]
    for key in name:
        temp = []
        for position in originalDict[key]:
            temp.append(position.tolist())
        res[key] = temp
    return res