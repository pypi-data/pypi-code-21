import pymatgen as pm
import Utils.SurfaceUtils as SUtils
import json
import pymatgen.core.surface as surface
import pymatgen.analysis.adsorption as paa
import sys

s1 = pm.Structure.from_file(sys.argv[1], "w")

# print(s1)

h = int(sys.argv[2])
k = int(sys.argv[3])
l = int(sys.argv[4])
thickness = float(sys.argv[5])
vacuum = float(sys.argv[6])
slabGenerator = surface.SlabGenerator(s1, [h,k,l], thickness, vacuum)
slab = slabGenerator.get_slab()

res = {}
Slabs = SUtils.toSurfaceDict(slab)
res["Slab"] = Slabs


ASF = paa.AdsorbateSiteFinder(slab, sys.argv[7], sys.argv[8], None, sys.argv[9])
poditions = ASF.find_adsorption_sites()
pos = SUtils.toAbsorbSitesDict(poditions)
res["Positions"] = pos

print(json.dumps(res))