from clickpoints.launch import main

import sys

#sys.argv.append(r"D:\Repositories\ClickPointsExamples\TweezerVideos\001\track.cdb")
#sys.argv.append(r"D:\Repositories\ClickPoints\clickpoints\addons\Westernblot\western.cdb")
#sys.argv.append(r"D:\Repositories\ClickPoints\clickpoints\addons\Kymograph\20140601-20140701.cdb")
#sys.argv.append(r"D:\Repositories\ClickPointsExamples\PlantRoot\dronpa.cdb")
sys.argv.append(r"D:\Repositories\ClickPointsExamples\TweezerVideos\001\track.cdb")
#sys.argv.append(r"D:\TestData\MEF_Test_20000_3\20160415-173301_Mic4_rep4_pos0_x3_y0_modeFluo6_zMinProj.tif")
main()


def getCurrentVersion():
    import json
    import os
    import natsort
    result = os.popen("conda search -crgerum -f clickpoints --json").read()
    result = json.loads(result)
    version = natsort.natsorted([f["version"] for f in result["clickpoints"]])[-1]
    return version

#print(getCurrentVersion())
#import clickpoints
#print(clickpoints.__version__)