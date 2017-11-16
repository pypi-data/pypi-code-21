import pymatgen as pm
import pymatgen.core.surface as surface
import json
import sys
import Utils.SurfaceUtils as SUtils

s1 = pm.Structure.from_file(sys.argv[1], "w")
h = int(sys.argv[2])
k = int(sys.argv[3])
l = int(sys.argv[4])
thickness = float(sys.argv[5])
vacuum = float(sys.argv[6])
slabGenerator = surface.SlabGenerator(s1, [h,k,l], thickness, vacuum)

slab = slabGenerator.get_slab()

res = SUtils.toSurfaceDict(slab)
print(json.dumps(res))
