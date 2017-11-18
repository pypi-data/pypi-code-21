from .terrain import Terrain, Airport, Runway, ParkingSlot, MapView, Graph
from .. import mapping
from typing import List
import os


class Anapa(Airport):
    id = 12
    name = "Anapa"
    position = mapping.Point(-5406.2803440839, 243127.2973737)
    tacan = None
    frequencies = [121000000, 38400000, 250000000, 3750000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Anapa, self).__init__()

        self.runways.append(Runway(40))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=1, position=mapping.Point(-5210.8227539063, 244593.3125), large=False, heli=False,
                airplanes=True, slot_name='91', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(-5132.0927734375, 244642.953125), large=False, heli=False,
                airplanes=True, slot_name='92', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=7, position=mapping.Point(-5041.333984375, 244797.3125), large=False, heli=False,
                airplanes=True, slot_name='82', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-5120.0620117188, 244747.6875), large=False, heli=False,
                airplanes=True, slot_name='83', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-4928.2514648438, 244830.65625), large=False, heli=False,
                airplanes=True, slot_name='80', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-4803.1616210938, 244945.359375), large=False, heli=False,
                airplanes=True, slot_name='77', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-4849.3823242188, 244864.5625), large=False, heli=False,
                airplanes=True, slot_name='78', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-4748.1674804688, 244814.921875), large=False, heli=False,
                airplanes=True, slot_name='75', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-4788.91796875, 244331.359375), large=False, heli=False,
                airplanes=True, slot_name='73', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-4934.5922851563, 244157.984375), large=False, heli=False,
                airplanes=True, slot_name='66', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-4970.013671875, 244304.828125), large=False, heli=False,
                airplanes=True, slot_name='70', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-4888.375, 244238.765625), large=False, heli=False,
                airplanes=True, slot_name='67', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-4835.1455078125, 244250.59375), large=False, heli=False,
                airplanes=True, slot_name='72', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=129, position=mapping.Point(-5913.833984375, 241692.09375), large=False, heli=False,
                airplanes=True, slot_name='56', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=132, position=mapping.Point(-5783.2290039063, 241654.5625), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=135, position=mapping.Point(-5750.9443359375, 241965.640625), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=138, position=mapping.Point(-5827.509765625, 242001.28125), large=False, heli=False,
                airplanes=True, slot_name='62', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=143, position=mapping.Point(-5450.2270507813, 241772.78125), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=146, position=mapping.Point(-5482.51953125, 241461.65625), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=149, position=mapping.Point(-5319.6337890625, 241735.21875), large=False, heli=False,
                airplanes=True, slot_name='41', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=150, position=mapping.Point(-5693.875, 242025.953125), large=False, heli=False,
                airplanes=True, slot_name='59', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=151, position=mapping.Point(-5431.3403320313, 241689.96875), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=152, position=mapping.Point(-5408.34765625, 241546.4375), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=153, position=mapping.Point(-5524.3833007813, 241687.984375), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=162, position=mapping.Point(-5709.0590820313, 241739.3125), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=164, position=mapping.Point(-4923.7856445313, 244385.59375), large=False, heli=False,
                airplanes=True, slot_name='69', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=167, position=mapping.Point(-5004.4897460938, 244412.03125), large=False, heli=False,
                airplanes=True, slot_name='68', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=168, position=mapping.Point(-4853.888671875, 244131.53125), large=False, heli=False,
                airplanes=True, slot_name='65', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=169, position=mapping.Point(-4754.4418945313, 244224.140625), large=False, heli=False,
                airplanes=True, slot_name='71', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=170, position=mapping.Point(-4713.6962890625, 244707.6875), large=False, heli=False,
                airplanes=True, slot_name='74', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=171, position=mapping.Point(-4883.8500976563, 244971.8125), large=False, heli=False,
                airplanes=True, slot_name='76', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=172, position=mapping.Point(-5008.9404296875, 244857.09375), large=False, heli=False,
                airplanes=True, slot_name='79', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=173, position=mapping.Point(-5151.9809570313, 244532.0625), large=False, heli=False,
                airplanes=True, slot_name='90', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=174, position=mapping.Point(-5326.1245117188, 244537.140625), large=False, heli=False,
                airplanes=True, slot_name='87', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=175, position=mapping.Point(-5100.162109375, 244858.546875), large=False, heli=False,
                airplanes=True, slot_name='81', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=176, position=mapping.Point(-5239.669921875, 244840.875), large=False, heli=False,
                airplanes=True, slot_name='84', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=183, position=mapping.Point(-5207.0048828125, 244762.484375), large=False, heli=False,
                airplanes=True, slot_name='85', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=184, position=mapping.Point(-5297.986328125, 244744.515625), large=False, heli=False,
                airplanes=True, slot_name='86', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=185, position=mapping.Point(-5297.392578125, 242734.078125), large=False, heli=True,
                airplanes=True, slot_name='20', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=186, position=mapping.Point(-5327.2578125, 242707.5), large=False, heli=True,
                airplanes=True, slot_name='18', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=187, position=mapping.Point(-5342.1748046875, 242694.171875), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=188, position=mapping.Point(-5252.5966796875, 242773.984375), large=False, heli=True,
                airplanes=True, slot_name='23', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=189, position=mapping.Point(-5267.5219726563, 242760.703125), large=False, heli=True,
                airplanes=True, slot_name='22', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=190, position=mapping.Point(-5282.4541015625, 242747.375), large=False, heli=True,
                airplanes=True, slot_name='21', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=191, position=mapping.Point(-5312.3198242188, 242720.765625), large=False, heli=True,
                airplanes=True, slot_name='19', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=192, position=mapping.Point(-5237.6557617188, 242787.296875), large=False, heli=True,
                airplanes=True, slot_name='24', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=193, position=mapping.Point(-5357.1171875, 242680.859375), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=194, position=mapping.Point(-5372.0551757813, 242667.578125), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=195, position=mapping.Point(-5386.9770507813, 242654.25), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=196, position=mapping.Point(-5401.9111328125, 242640.96875), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=197, position=mapping.Point(-5416.8559570313, 242627.65625), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=198, position=mapping.Point(-4894.9404296875, 243043), large=True, heli=True,
                airplanes=True, slot_name='27', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=199, position=mapping.Point(-4939.7358398438, 243003.09375), large=True, heli=True,
                airplanes=True, slot_name='26', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=200, position=mapping.Point(-4984.5400390625, 242963.1875), large=True, heli=True,
                airplanes=True, slot_name='25', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=201, position=mapping.Point(-5359.1123046875, 244615.390625), large=False, heli=False,
                airplanes=True, slot_name='88', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=202, position=mapping.Point(-5267.8071289063, 244633.515625), large=False, heli=False,
                airplanes=True, slot_name='89', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=203, position=mapping.Point(-4669.0244140625, 243243.609375), large=True, heli=True,
                airplanes=True, slot_name='32', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=204, position=mapping.Point(-4713.8266601563, 243203.6875), large=True, heli=True,
                airplanes=True, slot_name='31', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=205, position=mapping.Point(-4758.6293945313, 243163.75), large=True, heli=True,
                airplanes=True, slot_name='30', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=206, position=mapping.Point(-4803.4248046875, 243123.859375), large=True, heli=True,
                airplanes=True, slot_name='29', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=207, position=mapping.Point(-4848.224609375, 243083.953125), large=True, heli=True,
                airplanes=True, slot_name='28', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=208, position=mapping.Point(-4811.4125976563, 244637.4375), large=True, heli=True,
                airplanes=True, slot_name='40', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=209, position=mapping.Point(-4772.6127929688, 244591.703125), large=True, heli=True,
                airplanes=True, slot_name='39', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=210, position=mapping.Point(-4733.7978515625, 244545.921875), large=True, heli=True,
                airplanes=True, slot_name='38', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=211, position=mapping.Point(-4617.3813476563, 244408.671875), large=True, heli=True,
                airplanes=True, slot_name='35', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=212, position=mapping.Point(-4694.9990234375, 244500.171875), large=True, heli=True,
                airplanes=True, slot_name='37', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=213, position=mapping.Point(-4656.1831054688, 244454.40625), large=True, heli=True,
                airplanes=True, slot_name='36', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=214, position=mapping.Point(-4578.5727539063, 244362.890625), large=True, heli=True,
                airplanes=True, slot_name='34', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=215, position=mapping.Point(-4539.7690429688, 244317.125), large=True, heli=True,
                airplanes=True, slot_name='33', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=216, position=mapping.Point(-5798.951171875, 242110.25), large=False, heli=False,
                airplanes=True, slot_name='63', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=217, position=mapping.Point(-5732.0517578125, 241882.84375), large=False, heli=False,
                airplanes=True, slot_name='55', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=218, position=mapping.Point(-5839.6616210938, 241776.875), large=False, heli=False,
                airplanes=True, slot_name='58', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=219, position=mapping.Point(-5932.72265625, 241774.890625), large=False, heli=False,
                airplanes=True, slot_name='57', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=220, position=mapping.Point(-5825.1123046875, 241880.859375), large=False, heli=False,
                airplanes=True, slot_name='54', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=221, position=mapping.Point(-5881.3588867188, 242066.9375), large=False, heli=False,
                airplanes=True, slot_name='64', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=222, position=mapping.Point(-5802.1215820313, 241737.328125), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=223, position=mapping.Point(-5665.3227539063, 242134.90625), large=False, heli=False,
                airplanes=True, slot_name='60', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=224, position=mapping.Point(-5747.7255859375, 242091.609375), large=False, heli=False,
                airplanes=True, slot_name='61', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=225, position=mapping.Point(-5501.3950195313, 241544.453125), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=226, position=mapping.Point(-5393.787109375, 241650.421875), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=227, position=mapping.Point(-5300.724609375, 241652.40625), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=228, position=mapping.Point(-5431.810546875, 242614.359375), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=229, position=mapping.Point(-5446.7602539063, 242601.078125), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=230, position=mapping.Point(-5461.9755859375, 242587.5625), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=231, position=mapping.Point(-5476.9311523438, 242574.265625), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=232, position=mapping.Point(-5491.8818359375, 242560.984375), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=233, position=mapping.Point(-5506.8481445313, 242547.703125), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=234, position=mapping.Point(-5521.7978515625, 242534.421875), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=235, position=mapping.Point(-5536.7490234375, 242521.140625), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=236, position=mapping.Point(-5551.69921875, 242507.859375), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=237, position=mapping.Point(-5566.6494140625, 242494.578125), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=238, position=mapping.Point(-5581.6000976563, 242481.296875), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))


class KrasnodarCenter(Airport):
    id = 13
    name = "Krasnodar-Center"
    position = mapping.Point(11692.789495652, 367948.47230953)
    tacan = None
    frequencies = [122000000, 38600000, 251000000, 3800000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(KrasnodarCenter, self).__init__()

        self.runways.append(Runway(270))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(11250.362304688, 369029.71875), large=False, heli=False,
                airplanes=True, slot_name='33', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(11209.124023438, 369103.96875), large=False, heli=False,
                airplanes=True, slot_name='34', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(11297.9140625, 369131.84375), large=False, heli=False,
                airplanes=True, slot_name='35', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(11354.944335938, 369350.1875), large=False, heli=False,
                airplanes=True, slot_name='30', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(11279.916992188, 369310.375), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(11339.193359375, 369238.625), large=False, heli=False,
                airplanes=True, slot_name='32', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(11479.546875, 369366.09375), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(11430.643554688, 369296.625), large=False, heli=False,
                airplanes=True, slot_name='28', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(11515.967773438, 369259.5), large=False, heli=False,
                airplanes=True, slot_name='29', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(11554.1015625, 369290.15625), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(11603.004882813, 369359.625), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(11639.42578125, 369253.03125), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(11539.911132813, 369555.09375), large=False, heli=False,
                airplanes=True, slot_name='40', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(11644.665039063, 369477.75), large=False, heli=False,
                airplanes=True, slot_name='37', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(11693.568359375, 369547.21875), large=False, heli=False,
                airplanes=True, slot_name='36', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(11608.244140625, 369584.34375), large=False, heli=False,
                airplanes=True, slot_name='38', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(11454.586914063, 369592.21875), large=False, heli=False,
                airplanes=True, slot_name='41', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(11491.0078125, 369485.625), large=False, heli=False,
                airplanes=True, slot_name='39', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(11188.311523438, 368984.75), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(11103.43359375, 368981.5), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(11118.734375, 369073.375), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(11117.921875, 368861.4375), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(11033.043945313, 368858.1875), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(11048.344726563, 368950.0625), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(11046.443359375, 368735.875), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(10961.565429688, 368732.625), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(10976.866210938, 368824.5), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(10973.875, 368608.53125), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(10888.997070313, 368605.28125), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(10904.297851563, 368697.15625), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(10900.069335938, 368479), large=False, heli=False,
                airplanes=True, slot_name='54', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(10815.19140625, 368475.75), large=False, heli=False,
                airplanes=True, slot_name='55', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=64, position=mapping.Point(10830.4921875, 368567.625), large=False, heli=False,
                airplanes=True, slot_name='56', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=99, position=mapping.Point(11207.108398438, 367130.21875), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=100, position=mapping.Point(11208.15625, 367150.15625), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(11209.203125, 367170.15625), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=102, position=mapping.Point(11210.249023438, 367190.125), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=103, position=mapping.Point(11211.295898438, 367210.09375), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=104, position=mapping.Point(11212.342773438, 367230.0625), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=105, position=mapping.Point(11213.389648438, 367250.03125), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=106, position=mapping.Point(11214.436523438, 367270), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=107, position=mapping.Point(11215.483398438, 367289.96875), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(11216.529296875, 367309.9375), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=109, position=mapping.Point(11217.576171875, 367329.90625), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=110, position=mapping.Point(11218.623046875, 367349.90625), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=111, position=mapping.Point(11219.669921875, 367369.875), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=112, position=mapping.Point(11220.716796875, 367389.84375), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=113, position=mapping.Point(11221.763671875, 367409.8125), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=114, position=mapping.Point(11222.809570313, 367429.78125), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(11223.856445313, 367449.75), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=116, position=mapping.Point(11252.299804688, 368274.625), large=True, heli=True,
                airplanes=True, slot_name='18', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=117, position=mapping.Point(11255.440429688, 368334.53125), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=118, position=mapping.Point(11258.581054688, 368394.4375), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=119, position=mapping.Point(11261.720703125, 368454.34375), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=120, position=mapping.Point(11264.861328125, 368514.28125), large=True, heli=True,
                airplanes=True, slot_name='22', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=121, position=mapping.Point(11268.000976563, 368574.1875), large=True, heli=True,
                airplanes=True, slot_name='23', length=70, width=60, height=None, shelter=False))


class Novorossiysk(Airport):
    id = 14
    name = "Novorossiysk"
    position = mapping.Point(-40915.496728899, 279256.64920952)
    tacan = None
    frequencies = [123000000, 38800000, 252000000, 3850000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Novorossiysk, self).__init__()

        self.runways.append(Runway(220))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-41061.63671875, 278799.125), large=True, heli=True,
                airplanes=True, slot_name='08', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-41110.4453125, 278764.21875), large=True, heli=True,
                airplanes=True, slot_name='07', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-41159.2578125, 278729.28125), large=True, heli=True,
                airplanes=True, slot_name='06', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-41208.05859375, 278694.40625), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-41256.859375, 278659.53125), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-41307.6875, 278623.8125), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-41356.48828125, 278588.875), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-41405.296875, 278553.96875), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-40107.84765625, 279575.78125), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-40107.2109375, 279595.78125), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-40106.53515625, 279615.75), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-40105.86328125, 279635.71875), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-40105.21484375, 279655.71875), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-40104.5625, 279675.71875), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-40103.875, 279695.6875), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-40103.21875, 279715.6875), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-40484.4296875, 279207.28125), large=False, heli=False,
                airplanes=True, slot_name='33', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-40330.08984375, 279041.5625), large=False, heli=False,
                airplanes=True, slot_name='37', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-40480.1875, 279024.3125), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-40404.67578125, 279097.28125), large=False, heli=False,
                airplanes=True, slot_name='36', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-40409.90625, 279151.5625), large=False, heli=False,
                airplanes=True, slot_name='34', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-40294.01171875, 279118.4375), large=False, heli=False,
                airplanes=True, slot_name='38', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-40373.796875, 279228.4375), large=False, heli=False,
                airplanes=True, slot_name='35', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-40559.94140625, 279134.28125), large=False, heli=False,
                airplanes=True, slot_name='32', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-40670.59765625, 279113.15625), large=False, heli=False,
                airplanes=True, slot_name='28', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-40590.78515625, 279003.125), large=False, heli=False,
                airplanes=True, slot_name='29', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-40554.7109375, 279080.03125), large=False, heli=False,
                airplanes=True, slot_name='30', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-40769.64453125, 279003.03125), large=False, heli=False,
                airplanes=True, slot_name='22', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-40615.3046875, 278837.3125), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-40765.40234375, 278820.0625), large=False, heli=False,
                airplanes=True, slot_name='21', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=67, position=mapping.Point(-40689.890625, 278893.03125), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-40695.12109375, 278947.3125), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=70, position=mapping.Point(-40579.2265625, 278914.1875), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-40659.01171875, 279024.1875), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=75, position=mapping.Point(-40845.15625, 278930.03125), large=False, heli=False,
                airplanes=True, slot_name='18', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-40955.8125, 278908.90625), large=False, heli=False,
                airplanes=True, slot_name='17', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-40876, 278798.875), large=False, heli=False,
                airplanes=True, slot_name='20', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-40839.92578125, 278875.78125), large=False, heli=False,
                airplanes=True, slot_name='19', length=30, width=25, height=10, shelter=True))


class Krymsk(Airport):
    id = 15
    name = "Krymsk"
    position = mapping.Point(-6583.663574989, 294383.98405512)
    tacan = None
    frequencies = [124000000, 39000000, 253000000, 3900000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Krymsk, self).__init__()

        self.runways.append(Runway(220))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-7523.8505859375, 293785.125), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-7498.2939453125, 293754.34375), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-7511.0883789063, 293769.75), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-7536.615234375, 293800.5), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-7549.3779296875, 293815.90625), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-7562.1723632813, 293831.25), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-7574.9345703125, 293846.65625), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-5818.9565429688, 295246.28125), large=True, heli=True,
                airplanes=True, slot_name='55', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-5858.3950195313, 295291.5), large=True, heli=True,
                airplanes=True, slot_name='54', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-5779.55078125, 295201.0625), large=True, heli=True,
                airplanes=True, slot_name='56', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-5740.0849609375, 295155.875), large=True, heli=True,
                airplanes=True, slot_name='57', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-6101.1254882813, 295271.21875), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-6146.380859375, 295188.65625), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-6172.1333007813, 295287.09375), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-8104.83203125, 293981.75), large=False, heli=False,
                airplanes=True, slot_name='16', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=66, position=mapping.Point(-8057.6416015625, 294061.9375), large=False, heli=False,
                airplanes=True, slot_name='18', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=67, position=mapping.Point(-8138.1328125, 294089.4375), large=False, heli=False,
                airplanes=True, slot_name='17', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-6536.3872070313, 295044.9375), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-6462.9853515625, 295102.125), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=72, position=mapping.Point(-6527.7041015625, 295157.34375), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=75, position=mapping.Point(-6702.66796875, 294994.1875), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-6629.2661132813, 295051.375), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=77, position=mapping.Point(-6693.9848632813, 295106.59375), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-7038.6762695313, 294746.28125), large=False, heli=False,
                airplanes=True, slot_name='41', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=81, position=mapping.Point(-6973.716796875, 294812.90625), large=False, heli=False,
                airplanes=True, slot_name='40', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-7045.3271484375, 294858.84375), large=False, heli=False,
                airplanes=True, slot_name='39', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=84, position=mapping.Point(-7485.5297851563, 293738.9375), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-7187.0395507813, 294745.53125), large=True, heli=True,
                airplanes=True, slot_name='36', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-7270.5078125, 294703.71875), large=True, heli=True,
                airplanes=True, slot_name='35', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=87, position=mapping.Point(-7063.7890625, 294511.5625), large=True, heli=True,
                airplanes=True, slot_name='38', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-7171.9384765625, 294477.4375), large=True, heli=True,
                airplanes=True, slot_name='37', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=89, position=mapping.Point(-7322.7099609375, 294282.5625), large=True, heli=True,
                airplanes=True, slot_name='32', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-7402.568359375, 294233.5625), large=True, heli=True,
                airplanes=True, slot_name='30', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=91, position=mapping.Point(-7498.103515625, 294155.125), large=True, heli=True,
                airplanes=True, slot_name='29', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=92, position=mapping.Point(-7572.076171875, 294094.65625), large=True, heli=True,
                airplanes=True, slot_name='28', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=93, position=mapping.Point(-7627.1674804688, 294214.65625), large=True, heli=True,
                airplanes=True, slot_name='27', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=94, position=mapping.Point(-7601.8002929688, 294305.8125), large=True, heli=True,
                airplanes=True, slot_name='31', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=95, position=mapping.Point(-7511.4951171875, 294380.5625), large=True, heli=True,
                airplanes=True, slot_name='34', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=96, position=mapping.Point(-7420.8046875, 294397.375), large=True, heli=True,
                airplanes=True, slot_name='33', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=97, position=mapping.Point(-7744.3994140625, 293980.25), large=True, heli=True,
                airplanes=True, slot_name='12', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=98, position=mapping.Point(-7802.484375, 294050.40625), large=True, heli=True,
                airplanes=True, slot_name='13', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=99, position=mapping.Point(-7886.3530273438, 294252.53125), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=100, position=mapping.Point(-8007.9438476563, 294150.03125), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(-7876.7319335938, 293947.03125), large=True, heli=True,
                airplanes=True, slot_name='14', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=102, position=mapping.Point(-7948.3583984375, 293886.6875), large=True, heli=True,
                airplanes=True, slot_name='15', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=104, position=mapping.Point(-6325.6552734375, 295041.5), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=107, position=mapping.Point(-6351.4077148438, 295139.9375), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(-6280.3999023438, 295124.0625), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=110, position=mapping.Point(-7765.9921875, 294391.1875), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=112, position=mapping.Point(-7843.90234375, 294456.6875), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=113, position=mapping.Point(-7776.7807617188, 294484.75), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(-7801.1469726563, 294264.84375), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=118, position=mapping.Point(-7879.0571289063, 294330.34375), large=False, heli=False,
                airplanes=True, slot_name='21', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=119, position=mapping.Point(-7811.935546875, 294358.40625), large=False, heli=False,
                airplanes=True, slot_name='58', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=121, position=mapping.Point(-7615.4453125, 293915.96875), large=False, heli=False,
                airplanes=True, slot_name='11', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=124, position=mapping.Point(-7713.9541015625, 293890.4375), large=False, heli=False,
                airplanes=True, slot_name='09', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=125, position=mapping.Point(-7697.9487304688, 293961.34375), large=False, heli=False,
                airplanes=True, slot_name='10', length=30, width=25, height=10, shelter=True))


class Maykop(Airport):
    id = 16
    name = "Maykop"
    position = mapping.Point(-26441.347360305, 458040.61422532)
    tacan = None
    frequencies = [125000000, 39200000, 254000000, 3950000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Maykop, self).__init__()

        self.runways.append(Runway(220))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-27414.4921875, 457887.875), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-27425.181640625, 457871), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-27435.921875, 457854.09375), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-27446.619140625, 457837.25), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-27500.54296875, 457808.5), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-27579.2734375, 457794.34375), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-27480.849609375, 457812.0625), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-27946.376953125, 457556), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-27991.70703125, 457444.875), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=36, position=mapping.Point(-27520.232421875, 457804.96875), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-27969.04296875, 457500.4375), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-27923.71484375, 457611.53125), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-26534.21875, 458463.9375), large=False, heli=True,
                airplanes=True, slot_name='33', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-26425.2890625, 458514.25), large=False, heli=True,
                airplanes=True, slot_name='39', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-26443.4296875, 458505.875), large=False, heli=True,
                airplanes=True, slot_name='38', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-26461.591796875, 458497.46875), large=False, heli=True,
                airplanes=True, slot_name='37', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-26479.755859375, 458489.09375), large=False, heli=True,
                airplanes=True, slot_name='36', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-26497.89453125, 458480.71875), large=False, heli=True,
                airplanes=True, slot_name='35', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(-26516.0546875, 458472.3125), large=False, heli=True,
                airplanes=True, slot_name='34', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-26407.126953125, 458522.65625), large=False, heli=True,
                airplanes=True, slot_name='40', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-26552.357421875, 458455.5625), large=False, heli=True,
                airplanes=True, slot_name='32', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(-26570.521484375, 458447.15625), large=False, heli=True,
                airplanes=True, slot_name='31', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-26588.6875, 458438.75), large=False, heli=True,
                airplanes=True, slot_name='30', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-26606.8203125, 458430.375), large=False, heli=True,
                airplanes=True, slot_name='29', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=64, position=mapping.Point(-26624.990234375, 458421.96875), large=False, heli=True,
                airplanes=True, slot_name='28', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-26643.146484375, 458413.59375), large=False, heli=True,
                airplanes=True, slot_name='27', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=66, position=mapping.Point(-26661.28515625, 458405.21875), large=False, heli=True,
                airplanes=True, slot_name='26', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-26404.630859375, 458758.59375), large=False, heli=True,
                airplanes=True, slot_name='46', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-26361.634765625, 458870.625), large=False, heli=True,
                airplanes=True, slot_name='52', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-26368.80078125, 458851.9375), large=False, heli=True,
                airplanes=True, slot_name='51', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=81, position=mapping.Point(-26375.96875, 458833.25), large=False, heli=True,
                airplanes=True, slot_name='50', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-26383.13671875, 458814.625), large=False, heli=True,
                airplanes=True, slot_name='49', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-26390.3046875, 458795.9375), large=False, heli=True,
                airplanes=True, slot_name='48', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=84, position=mapping.Point(-26397.470703125, 458777.28125), large=False, heli=True,
                airplanes=True, slot_name='47', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-26433.294921875, 458683.90625), large=False, heli=True,
                airplanes=True, slot_name='42', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-26440.4609375, 458665.25), large=False, heli=True,
                airplanes=True, slot_name='41', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=87, position=mapping.Point(-27539.900390625, 457801.40625), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-27901.052734375, 457667.09375), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=89, position=mapping.Point(-27559.578125, 457797.90625), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-26426.15625, 458702.4375), large=False, heli=True,
                airplanes=True, slot_name='43', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=92, position=mapping.Point(-26418.98828125, 458721.125), large=False, heli=True,
                airplanes=True, slot_name='44', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=93, position=mapping.Point(-26411.8203125, 458739.75), large=False, heli=True,
                airplanes=True, slot_name='45', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=94, position=mapping.Point(-27549.08984375, 457621.1875), large=True, heli=True,
                airplanes=True, slot_name='06', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=96, position=mapping.Point(-27380.05078125, 458053.75), large=True, heli=True,
                airplanes=True, slot_name='17', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=97, position=mapping.Point(-27105.31640625, 458037.6875), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=98, position=mapping.Point(-27307.609375, 458166.40625), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=99, position=mapping.Point(-27192.81640625, 458303.0625), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=100, position=mapping.Point(-26940.52734375, 458193.53125), large=True, heli=True,
                airplanes=True, slot_name='22', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(-26974.025390625, 458469.5625), large=True, heli=True,
                airplanes=True, slot_name='23', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=102, position=mapping.Point(-26827.0078125, 458538.0625), large=True, heli=True,
                airplanes=True, slot_name='24', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=103, position=mapping.Point(-26726.876953125, 458320.21875), large=True, heli=True,
                airplanes=True, slot_name='25', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=105, position=mapping.Point(-26154.03125, 458811.5), large=True, heli=True,
                airplanes=True, slot_name='54', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=106, position=mapping.Point(-26267.814453125, 459022.59375), large=True, heli=True,
                airplanes=True, slot_name='53', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=107, position=mapping.Point(-26168.03125, 459077.71875), large=True, heli=True,
                airplanes=True, slot_name='55', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(-25954.34375, 458886.34375), large=True, heli=True,
                airplanes=True, slot_name='57', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=110, position=mapping.Point(-25984.953125, 459124.1875), large=True, heli=True,
                airplanes=True, slot_name='56', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=112, position=mapping.Point(-27178.244140625, 457924.375), large=True, heli=True,
                airplanes=True, slot_name='18', length=70, width=60, height=None, shelter=False))


class Gelendzhik(Airport):
    id = 17
    name = "Gelendzhik"
    position = mapping.Point(-50392.648146355, 298387.43849386)
    tacan = None
    frequencies = [126000000, 39400000, 255000000, 4000000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Gelendzhik, self).__init__()

        self.runways.append(Runway(220))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=0, position=mapping.Point(-50007.546875, 298460.71875), large=True, heli=True,
                airplanes=True, slot_name='13', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-50053.63671875, 298422.3125), large=True, heli=True,
                airplanes=True, slot_name='12', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-50099.7421875, 298383.875), large=True, heli=True,
                airplanes=True, slot_name='11', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-50435.8515625, 298121.28125), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-50451.4609375, 298108.21875), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-50466.8046875, 298095.375), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-50482.14453125, 298082.5625), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-50497.5, 298069.71875), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-50512.8359375, 298056.875), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-50528.171875, 298044.0625), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-50543.51171875, 298031.21875), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-50558.84765625, 298018.375), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-50574.1875, 298005.5625), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))


class Sochi(Airport):
    id = 18
    name = "Sochi"
    position = mapping.Point(-164474.73482633, 462236.21834688)
    tacan = None
    frequencies = [127000000, 39600000, 256000000, 4050000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Sochi, self).__init__()

        self.runways.append(Runway(240))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-164477.484375, 461754.53125), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-164505.65625, 461701.5), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-164970.5625, 460858.0625), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-164989.203125, 460822.71875), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-164979.890625, 460840.40625), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-164420.703125, 461860.6875), large=True, heli=True,
                airplanes=True, slot_name='22', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-164392.53125, 461913.59375), large=True, heli=True,
                airplanes=True, slot_name='23', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-164336.171875, 462019.59375), large=True, heli=True,
                airplanes=True, slot_name='25', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-164364.359375, 461966.59375), large=True, heli=True,
                airplanes=True, slot_name='24', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-164449.3125, 461807.4375), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-164931.828125, 460930.46875), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-164829.203125, 461125.09375), large=False, heli=True,
                airplanes=True, slot_name='18', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-164875.828125, 461036.65625), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-164959.78125, 460877.4375), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-164950.453125, 460895.15625), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-164941.125, 460912.75), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-164922.46875, 460948.15625), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-164913.171875, 460965.875), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-164903.828125, 460983.59375), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-164838.53125, 461107.40625), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-164866.515625, 461054.34375), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-164857.1875, 461072.03125), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-164847.84375, 461089.75), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-164885.171875, 461018.96875), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-164894.5, 461001.28125), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-164288.921875, 462107.65625), large=True, heli=True,
                airplanes=True, slot_name='26', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-164260.75, 462160.65625), large=True, heli=True,
                airplanes=True, slot_name='27', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(-164232.578125, 462213.59375), large=True, heli=True,
                airplanes=True, slot_name='28', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-164147.625, 462372.71875), large=True, heli=True,
                airplanes=True, slot_name='31', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-164119.4375, 462425.75), large=True, heli=True,
                airplanes=True, slot_name='32', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=64, position=mapping.Point(-164091.28125, 462478.6875), large=True, heli=True,
                airplanes=True, slot_name='33', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-164175.796875, 462319.75), large=True, heli=True,
                airplanes=True, slot_name='30', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=66, position=mapping.Point(-164203.96875, 462266.84375), large=True, heli=True,
                airplanes=True, slot_name='29', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-164775.546875, 463128.5625), large=False, heli=False,
                airplanes=True, slot_name='66', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-164838.75, 463060.25), large=False, heli=False,
                airplanes=True, slot_name='68', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=81, position=mapping.Point(-164766.0625, 463016.3125), large=False, heli=False,
                airplanes=True, slot_name='67', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-164674.28125, 463183.09375), large=False, heli=False,
                airplanes=True, slot_name='63', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-164737.484375, 463114.78125), large=False, heli=False,
                airplanes=True, slot_name='65', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-164664.796875, 463070.84375), large=False, heli=False,
                airplanes=True, slot_name='64', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-164573.921875, 463238), large=False, heli=False,
                airplanes=True, slot_name='60', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-164637.125, 463169.6875), large=False, heli=False,
                airplanes=True, slot_name='62', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=91, position=mapping.Point(-164564.4375, 463125.75), large=False, heli=False,
                airplanes=True, slot_name='61', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=93, position=mapping.Point(-164473.5625, 463292.375), large=False, heli=False,
                airplanes=True, slot_name='57', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=95, position=mapping.Point(-164536.765625, 463224.0625), large=False, heli=False,
                airplanes=True, slot_name='59', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=96, position=mapping.Point(-164464.078125, 463180.125), large=False, heli=False,
                airplanes=True, slot_name='58', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=98, position=mapping.Point(-164370.953125, 463346.75), large=False, heli=False,
                airplanes=True, slot_name='54', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=100, position=mapping.Point(-164434.15625, 463278.4375), large=False, heli=False,
                airplanes=True, slot_name='56', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(-164361.46875, 463234.5), large=False, heli=False,
                airplanes=True, slot_name='55', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=104, position=mapping.Point(-164333.625, 463333.6875), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=105, position=mapping.Point(-164260.9375, 463289.75), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=106, position=mapping.Point(-164270.421875, 463402), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=109, position=mapping.Point(-164233.5, 463387.84375), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=110, position=mapping.Point(-164160.8125, 463343.90625), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=111, position=mapping.Point(-164170.296875, 463456.15625), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=114, position=mapping.Point(-164132.734375, 463442.59375), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(-164060.046875, 463398.65625), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=116, position=mapping.Point(-164069.53125, 463510.90625), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=119, position=mapping.Point(-164032.046875, 463497.90625), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=120, position=mapping.Point(-163968.84375, 463566.21875), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=121, position=mapping.Point(-163959.359375, 463453.96875), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=128, position=mapping.Point(-164034.625, 462584.46875), large=True, heli=True,
                airplanes=True, slot_name='35', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=129, position=mapping.Point(-164006.4375, 462637.5), large=True, heli=True,
                airplanes=True, slot_name='36', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=130, position=mapping.Point(-164062.796875, 462531.5), large=True, heli=True,
                airplanes=True, slot_name='34', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=134, position=mapping.Point(-163949.84375, 462743.25), large=True, heli=True,
                airplanes=True, slot_name='38', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=135, position=mapping.Point(-163921.65625, 462796.28125), large=True, heli=True,
                airplanes=True, slot_name='39', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=136, position=mapping.Point(-163978.015625, 462690.28125), large=True, heli=True,
                airplanes=True, slot_name='37', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=137, position=mapping.Point(-163893.3125, 462849.15625), large=True, heli=True,
                airplanes=True, slot_name='40', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=138, position=mapping.Point(-163865.125, 462902.1875), large=True, heli=True,
                airplanes=True, slot_name='41', length=70, width=60, height=None, shelter=False))


class KrasnodarPashkovsky(Airport):
    id = 19
    name = "Krasnodar-Pashkovsky"
    position = mapping.Point(7674.038444859, 385029.5736699)
    tacan = None
    frequencies = [128000000, 39800000, 257000000, 4100000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(KrasnodarPashkovsky, self).__init__()

        self.runways.append(Runway(40))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=0, position=mapping.Point(7964.482421875, 387801.03125), large=True, heli=True,
                airplanes=True, slot_name='08', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(8005.3208007813, 387845.03125), large=True, heli=True,
                airplanes=True, slot_name='09', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(8127.8627929688, 387976.8125), large=True, heli=True,
                airplanes=True, slot_name='12', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(8087.0170898438, 387932.84375), large=True, heli=True,
                airplanes=True, slot_name='11', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(8046.1616210938, 387888.8125), large=True, heli=True,
                airplanes=True, slot_name='10', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(7923.1420898438, 387756.90625), large=True, heli=True,
                airplanes=True, slot_name='07', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(8168.7744140625, 388020.78125), large=True, heli=True,
                airplanes=True, slot_name='13', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(6926.1547851563, 386704.40625), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(6966.53125, 386748.78125), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(7047.3159179688, 386837.5625), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(7006.9116210938, 386793.125), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(6885.4204101563, 386660.3125), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(7087.6899414063, 386881.90625), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(8734.8017578125, 388642.53125), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(8775.5771484375, 388686.59375), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(8816.3603515625, 388730.59375), large=False, heli=True,
                airplanes=True, slot_name='18', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(8857.1376953125, 388774.625), large=False, heli=True,
                airplanes=True, slot_name='19', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(8694.072265625, 388598.53125), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(8652.9404296875, 388554.84375), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))


class Sukhumi(Airport):
    id = 20
    name = "Sukhumi"
    position = mapping.Point(-220531.73642658, 564387.05872916)
    tacan = None
    frequencies = [129000000, 40000000, 258000000, 4150000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Sukhumi, self).__init__()

        self.runways.append(Runway(300))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-219863.984375, 563508.6875), large=True, heli=True,
                airplanes=True, slot_name='23', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-219887.796875, 563586.0625), large=True, heli=True,
                airplanes=True, slot_name='22', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-219911.09375, 563654.5625), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-219760.4375, 563975.125), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-219710.328125, 564235), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-219830.765625, 564130.75), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-219791.421875, 563737), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-219773.0625, 563880.4375), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-219733.421875, 563743.375), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-219714.203125, 564198), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-219701.984375, 564314.5625), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-219706.140625, 564274.8125), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-219809.890625, 564329.5), large=False, heli=True,
                airplanes=True, slot_name='20', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-219814.046875, 564289.875), large=False, heli=True,
                airplanes=True, slot_name='19', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-219818.21875, 564250.0625), large=False, heli=True,
                airplanes=True, slot_name='18', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-219822.40625, 564210.3125), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-219826.59375, 564170.5), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-219740.046875, 564173.4375), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-219743.703125, 564134.25), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-219747.890625, 564094.5), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-219752.0625, 564054.6875), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-219756.25, 564014.9375), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-219760.46875, 563934.625), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))


class Gudauta(Airport):
    id = 21
    name = "Gudauta"
    position = mapping.Point(-196974.19851241, 516290.23098695)
    tacan = None
    frequencies = [130000000, 40200000, 259000000, 4200000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Gudauta, self).__init__()

        self.runways.append(Runway(330))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-197846.828125, 516550.125), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-197795.75, 516441.59375), large=True, heli=True,
                airplanes=True, slot_name='06', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-197821.296875, 516495.8125), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-197872.375, 516604.375), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-197897.9375, 516658.6875), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-197923.484375, 516713.03125), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-197744.65625, 516333), large=True, heli=True,
                airplanes=True, slot_name='08', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-197770.203125, 516387.21875), large=True, heli=True,
                airplanes=True, slot_name='07', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-197693.5625, 516224.4375), large=True, heli=True,
                airplanes=True, slot_name='10', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-197719.109375, 516278.65625), large=True, heli=True,
                airplanes=True, slot_name='09', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-196349.828125, 515792), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-196434.640625, 515787.34375), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-196420.78125, 515879.4375), large=False, heli=False,
                airplanes=True, slot_name='28', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-196404.984375, 515691.71875), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-196489.78125, 515687.09375), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-196475.921875, 515779.21875), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-196704.65625, 515788.1875), large=False, heli=False,
                airplanes=True, slot_name='17', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-196619.84375, 515792.84375), large=False, heli=False,
                airplanes=True, slot_name='18', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-196633.703125, 515700.75), large=False, heli=False,
                airplanes=True, slot_name='19', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-196649.5, 515888.46875), large=False, heli=False,
                airplanes=True, slot_name='29', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-196564.703125, 515893.09375), large=False, heli=False,
                airplanes=True, slot_name='30', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-196578.5625, 515800.96875), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-196460.125, 515591.1875), large=False, heli=False,
                airplanes=True, slot_name='20', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-196544.9375, 515586.53125), large=False, heli=False,
                airplanes=True, slot_name='21', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-196531.078125, 515678.625), large=False, heli=False,
                airplanes=True, slot_name='22', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-196515.28125, 515490.90625), large=False, heli=False,
                airplanes=True, slot_name='11', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-196600.078125, 515486.28125), large=False, heli=False,
                airplanes=True, slot_name='12', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-196586.21875, 515578.40625), large=False, heli=False,
                airplanes=True, slot_name='13', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-196759.609375, 515688.28125), large=False, heli=False,
                airplanes=True, slot_name='14', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-196674.796875, 515692.9375), large=False, heli=False,
                airplanes=True, slot_name='15', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-196688.65625, 515600.84375), large=False, heli=False,
                airplanes=True, slot_name='16', length=30, width=25, height=10, shelter=True))


class Batumi(Airport):
    id = 22
    name = "Batumi"
    position = mapping.Point(-355692.3067714, 617269.96285781)
    tacan = "16X"
    frequencies = [131000000, 40400000, 260000000, 4250000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Batumi, self).__init__()

        self.runways.append(Runway(300))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(-355972.03125, 618122.6875), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(-355984.8125, 618141.25), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=7, position=mapping.Point(-356010.375, 618177.5625), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-355997.40625, 618159.25), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-356091.65625, 618219.125), large=True, heli=True,
                airplanes=True, slot_name='06', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-356059.21875, 618240.25), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-356100.46875, 618303.125), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-356140.09375, 618271.0625), large=True, heli=True,
                airplanes=True, slot_name='08', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-356180.90625, 618327), large=True, heli=True,
                airplanes=True, slot_name='10', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-356151.25, 618352.625), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))


class Senaki(Airport):
    id = 23
    name = "Senaki"
    position = mapping.Point(-281713.83114196, 647369.87369832)
    tacan = "31X"
    frequencies = [132000000, 40600000, 261000000, 4300000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Senaki, self).__init__()

        self.runways.append(Runway(90))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-281508.78125, 648224.25), large=False, heli=False,
                airplanes=True, slot_name='60', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-281620.4375, 648117.6875), large=False, heli=False,
                airplanes=True, slot_name='59', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-281484.71875, 648004.4375), large=False, heli=True,
                airplanes=True, slot_name='57', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-281610.125, 647992.125), large=False, heli=False,
                airplanes=True, slot_name='58', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-281626.65625, 647900.5), large=False, heli=False,
                airplanes=True, slot_name='56', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-281480.34375, 647871.5625), large=False, heli=False,
                airplanes=True, slot_name='55', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-281606.84375, 647805.8125), large=False, heli=False,
                airplanes=True, slot_name='54', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-281585.71875, 647848.4375), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-281451.375, 647818.5625), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-281605.375, 647714.625), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-281463.09375, 647680.5625), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-281436.125, 647633.1875), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-281570.65625, 647665.0625), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-281395.0625, 646840.875), large=False, heli=False,
                airplanes=True, slot_name='30', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-281506.53125, 646732.3125), large=False, heli=False,
                airplanes=True, slot_name='29', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-281392.3125, 647552.6875), large=False, heli=False,
                airplanes=True, slot_name='32', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-281437.1875, 647462.5625), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-281390.15625, 647409.6875), large=False, heli=False,
                airplanes=True, slot_name='33', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-281298.46875, 647460.1875), large=False, heli=False,
                airplanes=True, slot_name='34', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-281251.0625, 647428.625), large=False, heli=False,
                airplanes=True, slot_name='39', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-281331.65625, 647260.125), large=False, heli=False,
                airplanes=True, slot_name='38', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-281372.1875, 647351.3125), large=False, heli=False,
                airplanes=True, slot_name='36', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-281340.5, 647387.375), large=False, heli=False,
                airplanes=True, slot_name='35', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-281248.90625, 647285.625), large=False, heli=False,
                airplanes=True, slot_name='41', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-281156.90625, 647346.1875), large=False, heli=False,
                airplanes=True, slot_name='40', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=50, position=mapping.Point(-281135.03125, 647212.1875), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-281160.34375, 647165.25), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-281201.84375, 647127.125), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-281255.09375, 647204), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-281104.375, 647307.75), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-281379.375, 646756.6875), large=False, heli=False,
                airplanes=True, slot_name='16', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=70, position=mapping.Point(-281391.34375, 646184), large=False, heli=False,
                airplanes=True, slot_name='07', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-281296.34375, 646191), large=False, heli=False,
                airplanes=True, slot_name='09', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=72, position=mapping.Point(-281350.96875, 646101.125), large=False, heli=False,
                airplanes=True, slot_name='08', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=74, position=mapping.Point(-281231.53125, 646209.375), large=False, heli=False,
                airplanes=True, slot_name='10', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-281212.25, 646248.875), large=False, heli=False,
                airplanes=True, slot_name='11', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-281277.25, 646359.8125), large=False, heli=False,
                airplanes=True, slot_name='13', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-281466.90625, 646396.5), large=False, heli=False,
                airplanes=True, slot_name='06', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-281365.1875, 646605.875), large=False, heli=False,
                airplanes=True, slot_name='14', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-281198.4375, 646762.4375), large=False, heli=False,
                airplanes=True, slot_name='18', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-281114.4375, 646872.5625), large=False, heli=False,
                airplanes=True, slot_name='20', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-281208.46875, 646989.125), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-281172.21875, 647061.625), large=False, heli=False,
                airplanes=True, slot_name='22', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-281012.65625, 646951.75), large=False, heli=False,
                airplanes=True, slot_name='21', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-281239.40625, 646910.5625), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=94, position=mapping.Point(-281352.09375, 646879.875), large=False, heli=False,
                airplanes=True, slot_name='28', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=95, position=mapping.Point(-281290.125, 646987.4375), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=97, position=mapping.Point(-281335.625, 646976.3125), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=98, position=mapping.Point(-281385.78125, 646924.1875), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(-281213.65625, 646332.625), large=False, heli=False,
                airplanes=True, slot_name='12', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=105, position=mapping.Point(-281265.40625, 647124.4375), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=107, position=mapping.Point(-281388.34375, 647272.375), large=False, heli=False,
                airplanes=True, slot_name='69', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(-281613.75, 648362.125), large=False, heli=False,
                airplanes=True, slot_name='61', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=109, position=mapping.Point(-281619.03125, 646385.625), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=111, position=mapping.Point(-281577.53125, 646430.8125), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=113, position=mapping.Point(-281538.28125, 646474.4375), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(-281495.90625, 646520.5625), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=117, position=mapping.Point(-281457.5, 646563.1875), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=119, position=mapping.Point(-281337.96875, 646694.25), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=120, position=mapping.Point(-281279.15625, 646758.9375), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=121, position=mapping.Point(-281191.5625, 646855.125), large=False, heli=True,
                airplanes=True, slot_name='19', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=123, position=mapping.Point(-281415.78125, 648105.9375), large=False, heli=True,
                airplanes=True, slot_name='63', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=124, position=mapping.Point(-281521.46875, 648100.875), large=False, heli=True,
                airplanes=True, slot_name='62', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=129, position=mapping.Point(-281636.28125, 648069.5), large=False, heli=True,
                airplanes=True, slot_name='64', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=130, position=mapping.Point(-281665, 648066.25), large=False, heli=True,
                airplanes=True, slot_name='65', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=131, position=mapping.Point(-281693.0625, 648063.3125), large=False, heli=True,
                airplanes=True, slot_name='66', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=132, position=mapping.Point(-281724.6875, 648060.75), large=False, heli=True,
                airplanes=True, slot_name='67', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=133, position=mapping.Point(-281336.53125, 647506.5), large=False, heli=True,
                airplanes=True, slot_name='68', length=30, width=25, height=None, shelter=False))


class Kobuleti(Airport):
    id = 24
    name = "Kobuleti"
    position = mapping.Point(-317948.32727306, 635639.37385346)
    tacan = "67X"
    frequencies = [133000000, 40800000, 262000000, 4350000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Kobuleti, self).__init__()

        self.runways.append(Runway(70))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-317899.40625, 636670.4375), large=True, heli=True,
                airplanes=True, slot_name='28', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-317680.78125, 636917.5625), large=True, heli=True,
                airplanes=True, slot_name='30', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-317870.0625, 636859.8125), large=True, heli=True,
                airplanes=True, slot_name='29', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-317874.9375, 635000.375), large=True, heli=True,
                airplanes=True, slot_name='42', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-317740.6875, 635084.25), large=True, heli=True,
                airplanes=True, slot_name='41', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-318024.84375, 636164.5625), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-318097.4375, 636237.875), large=False, heli=False,
                airplanes=True, slot_name='22', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-318026.75, 636258.8125), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-317938.25, 636402.5), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-318010.84375, 636475.875), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=36, position=mapping.Point(-317940.15625, 636496.8125), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-317787.46875, 635295.8125), large=False, heli=False,
                airplanes=True, slot_name='40', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-317697.21875, 635543.6875), large=False, heli=False,
                airplanes=True, slot_name='37', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-317584.375, 635853.8125), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-317621.96875, 635750.4375), large=False, heli=False,
                airplanes=True, slot_name='33', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-317471.53125, 635753.3125), large=False, heli=False,
                airplanes=True, slot_name='32', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-317509.15625, 635649.9375), large=False, heli=False,
                airplanes=True, slot_name='34', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-317546.78125, 635546.5625), large=False, heli=False,
                airplanes=True, slot_name='36', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-317641.71875, 635285.6875), large=False, heli=False,
                airplanes=True, slot_name='39', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-317584.40625, 635443.1875), large=False, heli=False,
                airplanes=True, slot_name='38', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-318319.71875, 635219.75), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-318326.46875, 635190.4375), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-318272.5, 635424.3125), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-318279.21875, 635395.0625), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-318286, 635365.8125), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(-318312.96875, 635248.9375), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-318292.71875, 635336.625), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-318299.46875, 635307.4375), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-318306.21875, 635278.125), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=66, position=mapping.Point(-318189.96875, 635662.6875), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=68, position=mapping.Point(-318200.21875, 635634.5), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=70, position=mapping.Point(-318210.5, 635606.3125), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=72, position=mapping.Point(-318220.75, 635578.125), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=74, position=mapping.Point(-318231, 635549.9375), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=75, position=mapping.Point(-318241.28125, 635521.75), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-318251.53125, 635493.5625), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-318102, 635959.75), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-318122.53125, 635903.375), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-318143.03125, 635847), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=84, position=mapping.Point(-318163.5625, 635790.625), large=True, heli=True,
                airplanes=True, slot_name='18', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-317659.59375, 635647.0625), large=False, heli=False,
                airplanes=True, slot_name='35', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-318184.09375, 635734.25), large=True, heli=True,
                airplanes=True, slot_name='17', length=70, width=60, height=None, shelter=False))


class Kutaisi(Airport):
    id = 25
    name = "Kutaisi"
    position = mapping.Point(-284889.06283057, 683853.75717885)
    tacan = None
    frequencies = [134000000, 41000000, 263000000, 4400000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Kutaisi, self).__init__()

        self.runways.append(Runway(70))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=1, position=mapping.Point(-284388.03125, 683374.5), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=4, position=mapping.Point(-284599, 682349.875), large=True, heli=True,
                airplanes=True, slot_name='16', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-286161.75, 683077.3125), large=True, heli=True,
                airplanes=True, slot_name='17', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-285940.21875, 683041), large=True, heli=True,
                airplanes=True, slot_name='18', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-286057.875, 682825.1875), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-285906.40625, 682736.6875), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-285759.90625, 682944.1875), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-284219.84375, 685068.0625), large=True, heli=True,
                airplanes=True, slot_name='55', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-283953.65625, 685187.75), large=True, heli=True,
                airplanes=True, slot_name='58', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-283989.9375, 684966.1875), large=True, heli=True,
                airplanes=True, slot_name='56', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-284123.03125, 685177.5625), large=True, heli=True,
                airplanes=True, slot_name='57', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-284379.75, 683403.3125), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-284371.5, 683432.1875), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-284363.21875, 683461), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-284354.96875, 683489.875), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-284346.6875, 683518.6875), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-284338.4375, 683547.5), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-284330.15625, 683576.375), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-284321.875, 683605.1875), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-284313.59375, 683634.0625), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-284305.34375, 683662.875), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-284297.0625, 683691.6875), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-284473.4375, 683648.5625), large=False, heli=False,
                airplanes=True, slot_name='36', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-284506.53125, 683533.25), large=False, heli=False,
                airplanes=True, slot_name='35', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-284539.59375, 683417.875), large=False, heli=False,
                airplanes=True, slot_name='34', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-284559.3125, 682395), large=True, heli=True,
                airplanes=True, slot_name='15', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-284519.65625, 682440), large=True, heli=True,
                airplanes=True, slot_name='14', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-284480, 682485), large=True, heli=True,
                airplanes=True, slot_name='13', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=52, position=mapping.Point(-284703.15625, 682692.6875), large=False, heli=False,
                airplanes=True, slot_name='22', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=54, position=mapping.Point(-284670.0625, 682808), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-284637, 682923.375), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(-284838.28125, 682980.8125), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-284871.375, 682865.5), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-284904.4375, 682750.125), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(-284435.9375, 683201.3125), large=False, heli=False,
                airplanes=True, slot_name='32', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-284594.96875, 683021.5625), large=False, heli=False,
                airplanes=True, slot_name='28', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-284515.4375, 683111.4375), large=False, heli=False,
                airplanes=True, slot_name='30', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=67, position=mapping.Point(-284672.34375, 683250), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=68, position=mapping.Point(-284592.84375, 683339.875), large=False, heli=False,
                airplanes=True, slot_name='33', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-284751.875, 683160.125), large=False, heli=False,
                airplanes=True, slot_name='29', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=70, position=mapping.Point(-284164.1875, 683969), large=False, heli=False,
                airplanes=True, slot_name='41', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=72, position=mapping.Point(-284230.34375, 683738.3125), large=False, heli=False,
                airplanes=True, slot_name='37', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=74, position=mapping.Point(-284197.25, 683853.625), large=False, heli=False,
                airplanes=True, slot_name='39', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-284398.5625, 683911.125), large=False, heli=False,
                airplanes=True, slot_name='40', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=77, position=mapping.Point(-284365.46875, 684026.4375), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-284431.625, 683795.75), large=False, heli=False,
                airplanes=True, slot_name='38', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-284120.59375, 684724.3125), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=81, position=mapping.Point(-284186.75, 684493.625), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-284153.65625, 684608.9375), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-284354.96875, 684666.4375), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-284321.875, 684781.75), large=False, heli=False,
                airplanes=True, slot_name='54', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=87, position=mapping.Point(-284388.03125, 684551.0625), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-284196.4375, 684391), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-284156.8125, 684154.3125), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=92, position=mapping.Point(-284176.625, 684272.6875), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=94, position=mapping.Point(-284383.0625, 684237.875), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=95, position=mapping.Point(-284402.90625, 684356.25), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=96, position=mapping.Point(-284363.28125, 684119.5625), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))


class Mineralnye(Airport):
    id = 26
    name = "Mineralnye"
    position = mapping.Point(-51251.551717591, 705718.47981263)
    tacan = None
    frequencies = [135000000, 41200000, 264000000, 4450000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Mineralnye, self).__init__()

        self.runways.append(Runway(290))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(-51745.29296875, 705864.25), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-51900.9296875, 706188.875), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-51875.19921875, 706134.625), large=True, heli=True,
                airplanes=True, slot_name='18', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-51849.44921875, 706080.4375), large=True, heli=True,
                airplanes=True, slot_name='17', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-51823.73828125, 706026.25), large=True, heli=True,
                airplanes=True, slot_name='16', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-51797.9921875, 705972), large=True, heli=True,
                airplanes=True, slot_name='15', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-51772.23828125, 705917.875), large=True, heli=True,
                airplanes=True, slot_name='14', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-51732.44921875, 705837.1875), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-51719.55078125, 705810.0625), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-51706.6640625, 705783), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-51693.83203125, 705755.875), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-51680.92578125, 705728.75), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-51668.078125, 705701.6875), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-51655.234375, 705674.625), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-51642.3515625, 705647.4375), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-51629.46484375, 705620.375), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=36, position=mapping.Point(-51616.6328125, 705593.3125), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-51603.75, 705566.1875), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-51590.890625, 705539.125), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-52055.375, 706514.0625), large=True, heli=True,
                airplanes=True, slot_name='25', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-52029.640625, 706459.8125), large=True, heli=True,
                airplanes=True, slot_name='24', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-52003.89453125, 706405.6875), large=True, heli=True,
                airplanes=True, slot_name='23', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-51978.17578125, 706351.4375), large=True, heli=True,
                airplanes=True, slot_name='22', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-51952.421875, 706297.1875), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-51926.6796875, 706243), large=True, heli=True,
                airplanes=True, slot_name='20', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-52132.625, 706676.75), large=True, heli=True,
                airplanes=True, slot_name='28', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-52106.890625, 706622.4375), large=True, heli=True,
                airplanes=True, slot_name='27', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-52081.140625, 706568.375), large=True, heli=True,
                airplanes=True, slot_name='26', length=70, width=60, height=None, shelter=False))


class Nalchik(Airport):
    id = 27
    name = "Nalchik"
    position = mapping.Point(-124921.90954665, 760428.0733062)
    tacan = None
    frequencies = [136000000, 41400000, 265000000, 4500000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Nalchik, self).__init__()

        self.runways.append(Runway(60))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-125277.8359375, 760545.625), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-125119.265625, 760800.75), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-125153.2734375, 760751.3125), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=24, position=mapping.Point(-125187.2265625, 760701.875), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-125221.234375, 760652.375), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-125294.8359375, 760520.875), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-125311.7890625, 760496.1875), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-125328.7890625, 760471.4375), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-125345.796875, 760446.75), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-125362.796875, 760422), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-125379.75, 760397.3125), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-125396.75, 760372.5625), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-125413.7578125, 760347.8125), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-125430.7578125, 760323.125), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-125255.1875, 760602.9375), large=True, heli=True,
                airplanes=True, slot_name='15', length=70, width=60, height=None, shelter=False))


class Mozdok(Airport):
    id = 28
    name = "Mozdok"
    position = mapping.Point(-83454.571428571, 834453.14285714)
    tacan = None
    frequencies = [137000000, 41600000, 266000000, 4550000]
    unit_zones = []
    civilian = False

    def __init__(self):
        super(Mozdok, self).__init__()

        self.runways.append(Runway(80))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=6, position=mapping.Point(-83756.9765625, 835044.375), large=False, heli=True,
                airplanes=True, slot_name='23', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-83709.4765625, 835329.4375), large=False, heli=True,
                airplanes=True, slot_name='24', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-85089.6484375, 831900.625), large=False, heli=True,
                airplanes=True, slot_name='37', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-85244.9765625, 831859.3125), large=False, heli=True,
                airplanes=True, slot_name='38', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-85211.515625, 831977.5), large=False, heli=True,
                airplanes=True, slot_name='36', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=18, position=mapping.Point(-85076.625, 832018.875), large=False, heli=True,
                airplanes=True, slot_name='35', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-85228.046875, 832295.875), large=False, heli=True,
                airplanes=True, slot_name='33', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-85267.84375, 832172.375), large=False, heli=True,
                airplanes=True, slot_name='34', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-85130.890625, 832222.5), large=False, heli=True,
                airplanes=True, slot_name='32', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-83971.671875, 832792.3125), large=False, heli=True,
                airplanes=True, slot_name='31', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-83950.7578125, 833011.4375), large=False, heli=True,
                airplanes=True, slot_name='30', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-83939.3828125, 833133.4375), large=False, heli=True,
                airplanes=True, slot_name='29', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=30, position=mapping.Point(-83928.53125, 833278.125), large=False, heli=True,
                airplanes=True, slot_name='28', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=32, position=mapping.Point(-83958.5078125, 833466.25), large=False, heli=True,
                airplanes=True, slot_name='27', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-84066, 833605.25), large=False, heli=True,
                airplanes=True, slot_name='26', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-83759.5078125, 835548.25), large=False, heli=True,
                airplanes=True, slot_name='25', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=68, position=mapping.Point(-84032.2421875, 834076.9375), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-84018.8125, 834181.0625), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=70, position=mapping.Point(-83991.9609375, 834389.3125), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-83985.4296875, 834443.375), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=72, position=mapping.Point(-83978.53125, 834493.5), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=73, position=mapping.Point(-83972.1171875, 834548.625), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=74, position=mapping.Point(-83965.109375, 834597.625), large=False, heli=True,
                airplanes=True, slot_name='09', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=75, position=mapping.Point(-83958.8046875, 834653.875), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-83951.6796875, 834701.75), large=False, heli=True,
                airplanes=True, slot_name='11', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=77, position=mapping.Point(-83945.4921875, 834754.125), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-83938.25, 834805.875), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-83933.109375, 834858.5), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-83924.8203125, 834910), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=81, position=mapping.Point(-83918.8671875, 834961.875), large=False, heli=True,
                airplanes=True, slot_name='16', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-83911.390625, 835014.1875), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-83897.96875, 835118.3125), large=False, heli=True,
                airplanes=True, slot_name='18', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=84, position=mapping.Point(-83891.9375, 835169), large=False, heli=True,
                airplanes=True, slot_name='19', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-83884.5390625, 835222.4375), large=False, heli=True,
                airplanes=True, slot_name='20', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-83878.3125, 835277), large=False, heli=True,
                airplanes=True, slot_name='21', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=87, position=mapping.Point(-85118.03125, 831784.9375), large=False, heli=True,
                airplanes=True, slot_name='39', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-83872.03125, 835325.9375), large=False, heli=True,
                airplanes=True, slot_name='22', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-84058.984375, 833868.6875), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=91, position=mapping.Point(-84045.5546875, 833972.875), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))


class Lochini(Airport):
    id = 29
    name = "Lochini"
    position = mapping.Point(-315478.57142857, 896538.85714286)
    tacan = None
    frequencies = [138000000, 41800000, 267000000, 4600000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Lochini, self).__init__()

        self.runways.append(Runway(300))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=1, position=mapping.Point(-315166.40625, 897212.5), large=False, heli=True,
                airplanes=True, slot_name='36', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(-315195.96875, 897192.25), large=False, heli=True,
                airplanes=True, slot_name='37', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=5, position=mapping.Point(-315225.53125, 897172), large=False, heli=True,
                airplanes=True, slot_name='39', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=7, position=mapping.Point(-315255.09375, 897151.75), large=False, heli=True,
                airplanes=True, slot_name='38', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-315109.90625, 897130), large=True, heli=True,
                airplanes=True, slot_name='31', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-315139.46875, 897109.75), large=False, heli=True,
                airplanes=True, slot_name='32', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-315169.03125, 897089.5), large=True, heli=True,
                airplanes=True, slot_name='34', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-315198.59375, 897069.25), large=False, heli=True,
                airplanes=True, slot_name='33', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-315228.15625, 897049), large=False, heli=True,
                airplanes=True, slot_name='35', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=19, position=mapping.Point(-315053.375, 897047.5), large=True, heli=True,
                airplanes=True, slot_name='26', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=21, position=mapping.Point(-315082.9375, 897027.25), large=False, heli=True,
                airplanes=True, slot_name='27', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=23, position=mapping.Point(-315112.5, 897007), large=True, heli=True,
                airplanes=True, slot_name='29', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=25, position=mapping.Point(-315142.0625, 896986.75), large=False, heli=True,
                airplanes=True, slot_name='28', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=27, position=mapping.Point(-315171.625, 896966.5), large=False, heli=True,
                airplanes=True, slot_name='30', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-314996.875, 896964.9375), large=True, heli=True,
                airplanes=True, slot_name='21', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=31, position=mapping.Point(-315026.4375, 896944.6875), large=False, heli=True,
                airplanes=True, slot_name='22', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=33, position=mapping.Point(-315056, 896924.4375), large=True, heli=True,
                airplanes=True, slot_name='24', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-315085.5625, 896904.1875), large=False, heli=True,
                airplanes=True, slot_name='23', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-315115.125, 896883.9375), large=False, heli=True,
                airplanes=True, slot_name='25', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=39, position=mapping.Point(-314940.375, 896882.4375), large=True, heli=True,
                airplanes=True, slot_name='16', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=41, position=mapping.Point(-314969.9375, 896862.1875), large=False, heli=True,
                airplanes=True, slot_name='17', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=43, position=mapping.Point(-314999.5, 896841.9375), large=True, heli=True,
                airplanes=True, slot_name='19', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=45, position=mapping.Point(-315029.0625, 896821.6875), large=False, heli=True,
                airplanes=True, slot_name='18', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=47, position=mapping.Point(-315058.625, 896801.4375), large=False, heli=True,
                airplanes=True, slot_name='20', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-314883.84375, 896799.9375), large=True, heli=True,
                airplanes=True, slot_name='11', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-314913.40625, 896779.6875), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-314942.96875, 896759.4375), large=True, heli=True,
                airplanes=True, slot_name='14', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-314972.53125, 896739.1875), large=False, heli=True,
                airplanes=True, slot_name='13', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-315002.09375, 896718.9375), large=False, heli=True,
                airplanes=True, slot_name='15', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-314827.34375, 896717.4375), large=True, heli=True,
                airplanes=True, slot_name='06', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(-314856.90625, 896697.1875), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-314886.46875, 896676.9375), large=True, heli=True,
                airplanes=True, slot_name='09', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-314916.03125, 896656.6875), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=67, position=mapping.Point(-314945.59375, 896636.4375), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-314770.84375, 896635), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-314800.40625, 896614.75), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=73, position=mapping.Point(-314829.96875, 896594.5), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=75, position=mapping.Point(-314859.53125, 896574.25), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=78, position=mapping.Point(-314983.3125, 896467.0625), large=False, heli=True,
                airplanes=True, slot_name='44', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-314990.90625, 896555), large=False, heli=True,
                airplanes=True, slot_name='42', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-315016.125, 896539.75), large=False, heli=True,
                airplanes=True, slot_name='43', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-314889.09375, 896554), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(-314940.34375, 896389.9375), large=True, heli=True,
                airplanes=True, slot_name='46', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=109, position=mapping.Point(-314901.03125, 896415.6875), large=False, heli=True,
                airplanes=True, slot_name='47', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=112, position=mapping.Point(-315042, 896525.5), large=False, heli=True,
                airplanes=True, slot_name='48', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=113, position=mapping.Point(-314713.125, 896543.9375), large=True, heli=True,
                airplanes=True, slot_name='51', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=114, position=mapping.Point(-314742.71875, 896523.75), large=False, heli=True,
                airplanes=True, slot_name='50', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(-314772.28125, 896503.5), large=True, heli=True,
                airplanes=True, slot_name='49', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=120, position=mapping.Point(-314420.96875, 895574.75), large=False, heli=True,
                airplanes=False, slot_name='66', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=122, position=mapping.Point(-314394.9375, 895595.125), large=False, heli=True,
                airplanes=False, slot_name='65', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=124, position=mapping.Point(-314371.6875, 895613.8125), large=False, heli=True,
                airplanes=False, slot_name='64', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=126, position=mapping.Point(-314345.0625, 895634.5), large=False, heli=True,
                airplanes=False, slot_name='63', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=128, position=mapping.Point(-314249.375, 895478.125), large=False, heli=True,
                airplanes=False, slot_name='69', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=130, position=mapping.Point(-314326.15625, 895514.375), large=False, heli=True,
                airplanes=False, slot_name='68', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=131, position=mapping.Point(-314370.125, 895537.3125), large=False, heli=True,
                airplanes=False, slot_name='67', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=133, position=mapping.Point(-314324.09375, 895745.875), large=False, heli=True,
                airplanes=False, slot_name='70', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=135, position=mapping.Point(-314385.09375, 895827.25), large=False, heli=True,
                airplanes=False, slot_name='56', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=136, position=mapping.Point(-314301.25, 895767.9375), large=False, heli=True,
                airplanes=False, slot_name='71', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=138, position=mapping.Point(-314266.40625, 895797.8125), large=False, heli=True,
                airplanes=False, slot_name='72', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=140, position=mapping.Point(-314342.28125, 895862.125), large=False, heli=True,
                airplanes=False, slot_name='55', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=142, position=mapping.Point(-314310.25, 895892.6875), large=False, heli=True,
                airplanes=False, slot_name='54', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=144, position=mapping.Point(-314273.65625, 895919.9375), large=False, heli=True,
                airplanes=False, slot_name='53', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=146, position=mapping.Point(-314242.53125, 895946.5), large=False, heli=True,
                airplanes=False, slot_name='73', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=147, position=mapping.Point(-314256.84375, 896017.9375), large=False, heli=True,
                airplanes=False, slot_name='52', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=149, position=mapping.Point(-314336.625, 895987.625), large=False, heli=True,
                airplanes=False, slot_name='74', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=150, position=mapping.Point(-314373.125, 895962.5625), large=False, heli=True,
                airplanes=False, slot_name='78', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=152, position=mapping.Point(-314404.75, 895930.1875), large=False, heli=True,
                airplanes=False, slot_name='77', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=154, position=mapping.Point(-314422.5, 895756.75), large=False, heli=True,
                airplanes=False, slot_name='57', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=156, position=mapping.Point(-314482.53125, 895824.4375), large=False, heli=True,
                airplanes=False, slot_name='58', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=159, position=mapping.Point(-314958.96875, 896482.875), large=True, heli=True,
                airplanes=True, slot_name='45', length=70, width=60, height=None, shelter=False))


class Soganlug(Airport):
    id = 30
    name = "Soganlug"
    position = mapping.Point(-317838.57142857, 895424.57142858)
    tacan = None
    frequencies = [139000000, 42000000, 268000000, 4650000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Soganlug, self).__init__()

        self.runways.append(Runway(130))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-317118.53125, 894178.25), large=True, heli=True,
                airplanes=True, slot_name='05', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-317991.84375, 895367.25), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=10, position=mapping.Point(-318016.28125, 895389.9375), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=12, position=mapping.Point(-318051.78125, 895428.6875), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=14, position=mapping.Point(-318528.5625, 895798.75), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))


class Vaziani(Airport):
    id = 31
    name = "Vaziani"
    position = mapping.Point(-319069.063, 903150.625)
    tacan = None
    frequencies = [140000000, 42200000, 269000000, 4700000]
    unit_zones = []
    civilian = False

    def __init__(self):
        super(Vaziani, self).__init__()

        self.runways.append(Runway(140))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=3, position=mapping.Point(-317519.15625, 903209.375), large=False, heli=False,
                airplanes=True, slot_name='25', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=11, position=mapping.Point(-318048.375, 902475.5625), large=True, heli=True,
                airplanes=True, slot_name='01', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=13, position=mapping.Point(-318088.9375, 902514.4375), large=True, heli=True,
                airplanes=True, slot_name='02', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=15, position=mapping.Point(-318124.75, 902549.1875), large=True, heli=True,
                airplanes=True, slot_name='03', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=17, position=mapping.Point(-318167.3125, 902591.9375), large=True, heli=True,
                airplanes=True, slot_name='04', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=22, position=mapping.Point(-319623.0625, 904241.25), large=True, heli=True,
                airplanes=True, slot_name='79', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=26, position=mapping.Point(-319753.25, 904275.1875), large=True, heli=True,
                airplanes=True, slot_name='09', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=28, position=mapping.Point(-319783.5625, 904239.5625), large=True, heli=True,
                airplanes=True, slot_name='08', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=29, position=mapping.Point(-319858.53125, 904159), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=34, position=mapping.Point(-317993.84375, 902709.875), large=False, heli=False,
                airplanes=True, slot_name='11', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=35, position=mapping.Point(-318059.53125, 902639.6875), large=False, heli=False,
                airplanes=True, slot_name='10', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=37, position=mapping.Point(-317935.90625, 902714.9375), large=False, heli=False,
                airplanes=True, slot_name='13', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=38, position=mapping.Point(-317923.0625, 902609.3125), large=False, heli=False,
                airplanes=True, slot_name='12', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=40, position=mapping.Point(-317868.28125, 902587.625), large=False, heli=False,
                airplanes=True, slot_name='14', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-317947.8125, 902877.1875), large=False, heli=False,
                airplanes=True, slot_name='16', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=44, position=mapping.Point(-317837.84375, 902896.4375), large=False, heli=False,
                airplanes=True, slot_name='18', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=46, position=mapping.Point(-317881.65625, 902816.6875), large=False, heli=False,
                airplanes=True, slot_name='15', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=48, position=mapping.Point(-317629.125, 902843.1875), large=False, heli=False,
                airplanes=True, slot_name='21', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=49, position=mapping.Point(-317699.46875, 902898.5625), large=False, heli=False,
                airplanes=True, slot_name='22', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=51, position=mapping.Point(-317737.40625, 902815.9375), large=False, heli=False,
                airplanes=True, slot_name='19', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=53, position=mapping.Point(-317696, 902803.75), large=False, heli=False,
                airplanes=True, slot_name='20', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-317855.1875, 903263.9375), large=False, heli=False,
                airplanes=True, slot_name='28', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-317766.96875, 903280.1875), large=False, heli=False,
                airplanes=True, slot_name='27', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-317772.09375, 903189.3125), large=False, heli=False,
                airplanes=True, slot_name='30', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-317814.5625, 903198), large=False, heli=False,
                airplanes=True, slot_name='29', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-317589.46875, 903264.75), large=False, heli=False,
                airplanes=True, slot_name='26', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=64, position=mapping.Point(-317627.4375, 903182.125), large=False, heli=False,
                airplanes=True, slot_name='23', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=65, position=mapping.Point(-317586, 903169.9375), large=False, heli=False,
                airplanes=True, slot_name='24', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=69, position=mapping.Point(-318171.875, 902714.8125), large=False, heli=False,
                airplanes=True, slot_name='31', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=71, position=mapping.Point(-318161.53125, 902842.25), large=False, heli=False,
                airplanes=True, slot_name='33', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=73, position=mapping.Point(-318249.21875, 902737.3125), large=False, heli=False,
                airplanes=True, slot_name='32', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=74, position=mapping.Point(-318238.625, 902904.0625), large=False, heli=True,
                airplanes=True, slot_name='35', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=76, position=mapping.Point(-318317.5, 902845.1875), large=False, heli=False,
                airplanes=True, slot_name='34', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=77, position=mapping.Point(-318372.3125, 902884.625), large=False, heli=False,
                airplanes=True, slot_name='36', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=79, position=mapping.Point(-318307.71875, 902972.125), large=False, heli=True,
                airplanes=True, slot_name='37', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=80, position=mapping.Point(-318388.15625, 903087.9375), large=False, heli=False,
                airplanes=True, slot_name='39', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=82, position=mapping.Point(-318466.4375, 902994.5625), large=False, heli=False,
                airplanes=True, slot_name='38', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=83, position=mapping.Point(-318379.34375, 903159.625), large=False, heli=False,
                airplanes=True, slot_name='41', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=85, position=mapping.Point(-318515.96875, 903105.5), large=False, heli=False,
                airplanes=True, slot_name='40', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=86, position=mapping.Point(-318462.9375, 903208.625), large=False, heli=False,
                airplanes=True, slot_name='42', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=88, position=mapping.Point(-318596.71875, 903207.6875), large=False, heli=False,
                airplanes=True, slot_name='45', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=90, position=mapping.Point(-318627.6875, 903244.375), large=False, heli=False,
                airplanes=True, slot_name='44', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=92, position=mapping.Point(-318695.125, 903247.875), large=False, heli=False,
                airplanes=True, slot_name='43', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=93, position=mapping.Point(-318479.28125, 903285.4375), large=False, heli=False,
                airplanes=True, slot_name='47', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=95, position=mapping.Point(-318593.1875, 903320.8125), large=False, heli=False,
                airplanes=True, slot_name='46', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=96, position=mapping.Point(-318486.875, 903378.3125), large=False, heli=False,
                airplanes=True, slot_name='49', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=98, position=mapping.Point(-318603.75, 903414), large=False, heli=False,
                airplanes=True, slot_name='48', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=99, position=mapping.Point(-318489.59375, 903508.8125), large=False, heli=False,
                airplanes=True, slot_name='50', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=101, position=mapping.Point(-318570.65625, 903564.5), large=False, heli=False,
                airplanes=True, slot_name='51', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=103, position=mapping.Point(-318832.78125, 903551.25), large=False, heli=False,
                airplanes=True, slot_name='55', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=105, position=mapping.Point(-318752.9375, 903513.3125), large=False, heli=False,
                airplanes=True, slot_name='54', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=106, position=mapping.Point(-318711.90625, 903552.375), large=False, heli=False,
                airplanes=True, slot_name='53', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=108, position=mapping.Point(-318798.75, 903597.3125), large=False, heli=False,
                airplanes=True, slot_name='56', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=110, position=mapping.Point(-318649.9375, 903679.0625), large=False, heli=False,
                airplanes=True, slot_name='52', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=112, position=mapping.Point(-318776.75, 903750), large=False, heli=False,
                airplanes=True, slot_name='58', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=114, position=mapping.Point(-318822.15625, 903644.1875), large=False, heli=False,
                airplanes=True, slot_name='57', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=115, position=mapping.Point(-318845.28125, 903815.0625), large=False, heli=False,
                airplanes=True, slot_name='60', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=117, position=mapping.Point(-318910.84375, 903690.9375), large=False, heli=False,
                airplanes=True, slot_name='59', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=118, position=mapping.Point(-318952.9375, 903772.75), large=False, heli=False,
                airplanes=True, slot_name='62', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=120, position=mapping.Point(-318913.0625, 903854.6875), large=False, heli=True,
                airplanes=True, slot_name='61', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=123, position=mapping.Point(-319072.78125, 903773.5), large=False, heli=False,
                airplanes=True, slot_name='64', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=124, position=mapping.Point(-319027.25, 903910.625), large=False, heli=False,
                airplanes=True, slot_name='65', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=125, position=mapping.Point(-319135.25, 903789.3125), large=False, heli=False,
                airplanes=True, slot_name='67', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=127, position=mapping.Point(-319125.21875, 903881), large=False, heli=True,
                airplanes=True, slot_name='66', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=128, position=mapping.Point(-319026.84375, 903982.875), large=False, heli=False,
                airplanes=True, slot_name='80', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=130, position=mapping.Point(-319044.28125, 904303.4375), large=False, heli=False,
                airplanes=True, slot_name='90', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=132, position=mapping.Point(-318994.40625, 904258.875), large=False, heli=False,
                airplanes=True, slot_name='91', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=133, position=mapping.Point(-319096.25, 904228), large=False, heli=False,
                airplanes=True, slot_name='89', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=135, position=mapping.Point(-319119, 904181.25), large=False, heli=False,
                airplanes=True, slot_name='88', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=137, position=mapping.Point(-319132.8125, 904128.5625), large=False, heli=False,
                airplanes=True, slot_name='87', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=139, position=mapping.Point(-319120.15625, 904039.125), large=False, heli=False,
                airplanes=True, slot_name='81', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=141, position=mapping.Point(-319164.25, 904038.8125), large=False, heli=False,
                airplanes=True, slot_name='82', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=143, position=mapping.Point(-319290.78125, 904101.4375), large=False, heli=False,
                airplanes=True, slot_name='84', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=145, position=mapping.Point(-319184.1875, 904158), large=False, heli=False,
                airplanes=True, slot_name='86', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=147, position=mapping.Point(-319214.75, 904053.8125), large=False, heli=False,
                airplanes=True, slot_name='83', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=149, position=mapping.Point(-319249.71875, 904140.375), large=False, heli=False,
                airplanes=True, slot_name='85', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=151, position=mapping.Point(-319192.28125, 903808.125), large=False, heli=False,
                airplanes=True, slot_name='68', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=154, position=mapping.Point(-319223.6875, 903906.0625), large=False, heli=True,
                airplanes=True, slot_name='69', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=156, position=mapping.Point(-319284.46875, 903838.875), large=False, heli=False,
                airplanes=True, slot_name='70', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=157, position=mapping.Point(-319296.59375, 903964.3125), large=False, heli=True,
                airplanes=True, slot_name='92', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=160, position=mapping.Point(-319387.59375, 903909.8125), large=False, heli=False,
                airplanes=True, slot_name='72', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=161, position=mapping.Point(-319428.09375, 903958.5625), large=False, heli=False,
                airplanes=True, slot_name='73', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=163, position=mapping.Point(-319487.03125, 904033.625), large=False, heli=False,
                airplanes=True, slot_name='75', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=165, position=mapping.Point(-319444.21875, 904085.0625), large=False, heli=True,
                airplanes=True, slot_name='76', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=166, position=mapping.Point(-319513.25, 904150.1875), large=False, heli=True,
                airplanes=True, slot_name='77', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=167, position=mapping.Point(-319559.8125, 904095.375), large=False, heli=False,
                airplanes=True, slot_name='74', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=168, position=mapping.Point(-317878.21875, 902911.625), large=False, heli=False,
                airplanes=True, slot_name='17', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=172, position=mapping.Point(-319010.875, 903766.25), large=False, heli=False,
                airplanes=True, slot_name='63', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=173, position=mapping.Point(-319340.96875, 903867.75), large=False, heli=False,
                airplanes=True, slot_name='71', length=30, width=25, height=10, shelter=True))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=175, position=mapping.Point(-319840.125, 904183.375), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=176, position=mapping.Point(-319821.0625, 904207.125), large=False, heli=True,
                airplanes=True, slot_name='07', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=177, position=mapping.Point(-319599.15625, 904222.375), large=False, heli=True,
                airplanes=True, slot_name='78', length=30, width=25, height=None, shelter=False))


class Beslan(Airport):
    id = 32
    name = "Beslan"
    position = mapping.Point(-148810.84954665, 843756.7533062)
    tacan = None
    frequencies = [141000000, 42400000, 270000000, 4750000]
    unit_zones = []
    civilian = True

    def __init__(self):
        super(Beslan, self).__init__()

        self.runways.append(Runway(90))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=2, position=mapping.Point(-148868.4375, 843496.4375), large=False, heli=True,
                airplanes=True, slot_name='02', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=8, position=mapping.Point(-148838.5, 843498.3125), large=False, heli=True,
                airplanes=True, slot_name='01', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=9, position=mapping.Point(-148845.28125, 843609.375), large=False, heli=True,
                airplanes=True, slot_name='04', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=16, position=mapping.Point(-148815.34375, 843611.1875), large=False, heli=True,
                airplanes=True, slot_name='03', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=20, position=mapping.Point(-148875.234375, 843607.5), large=False, heli=True,
                airplanes=True, slot_name='05', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=42, position=mapping.Point(-148853.515625, 843744), large=False, heli=True,
                airplanes=True, slot_name='06', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=55, position=mapping.Point(-148875.8125, 844108.375), large=True, heli=True,
                airplanes=True, slot_name='15', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=56, position=mapping.Point(-148873.375, 844068.5), large=False, heli=True,
                airplanes=True, slot_name='14', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=57, position=mapping.Point(-148870.921875, 844028.5625), large=True, heli=True,
                airplanes=True, slot_name='13', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=58, position=mapping.Point(-148868.484375, 843988.625), large=False, heli=True,
                airplanes=True, slot_name='12', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=59, position=mapping.Point(-148866.046875, 843948.6875), large=True, heli=True,
                airplanes=True, slot_name='11', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=60, position=mapping.Point(-148863.59375, 843908.75), large=False, heli=True,
                airplanes=True, slot_name='10', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=61, position=mapping.Point(-148860.84375, 843863.75), large=True, heli=True,
                airplanes=True, slot_name='09', length=70, width=60, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=62, position=mapping.Point(-148858.421875, 843824.125), large=False, heli=True,
                airplanes=True, slot_name='08', length=30, width=25, height=None, shelter=False))
        self.parking_slots.append(ParkingSlot(
                crossroad_idx=63, position=mapping.Point(-148856.03125, 843784.9375), large=True, heli=True,
                airplanes=True, slot_name='07', length=70, width=60, height=None, shelter=False))


class Caucasus(Terrain):
    center = {"lat": 45.12945, "long": 34.26527}
    bounds = mapping.Rectangle(380*1000, -560*1000, -600*1000, 1130*1000)
    map_view_default = MapView(mapping.Point(-255714.28571428, 680571.42857143), 1000000)
    city_graph = Graph.from_pickle(os.path.join(os.path.dirname(__file__), 'caucasus.p'))  # type: Graph

    def __init__(self):
        super(Caucasus, self).__init__("Caucasus")
        # caucasus center MGRS
        # 36TWQ9949898109
        self.bullseye_blue = {"x": -291014, "y": 617414}
        self.bullseye_red = {"x": 11557, "y": 371700}

        self.airports['Anapa'] = Anapa()
        self.airports['Krasnodar-Center'] = KrasnodarCenter()
        self.airports['Novorossiysk'] = Novorossiysk()
        self.airports['Krymsk'] = Krymsk()
        self.airports['Maykop'] = Maykop()
        self.airports['Gelendzhik'] = Gelendzhik()
        self.airports['Sochi'] = Sochi()
        self.airports['Krasnodar-Pashkovsky'] = KrasnodarPashkovsky()
        self.airports['Sukhumi'] = Sukhumi()
        self.airports['Gudauta'] = Gudauta()
        self.airports['Batumi'] = Batumi()
        self.airports['Senaki'] = Senaki()
        self.airports['Kobuleti'] = Kobuleti()
        self.airports['Kutaisi'] = Kutaisi()
        self.airports['Mineralnye'] = Mineralnye()
        self.airports['Nalchik'] = Nalchik()
        self.airports['Mozdok'] = Mozdok()
        self.airports['Lochini'] = Lochini()
        self.airports['Soganlug'] = Soganlug()
        self.airports['Vaziani'] = Vaziani()
        self.airports['Beslan'] = Beslan()

        self.anapa().unit_zones.append(mapping.Rectangle(-5802.857142854, 242768.57142857, -7402.857142854, 244368.57142857))
        self.anapa().unit_zones.append(mapping.Rectangle(-4217.1428571397, 239325.71428572, -5417.1428571397, 240525.71428572))
        self.anapa().unit_zones.append(mapping.Rectangle(-5759.9999999969, 239132.85714286, -7159.9999999969, 240532.85714286))
        self.anapa().unit_zones.append(mapping.Rectangle(-3967.1428571397, 245318.57142857, -6767.1428571397, 248118.57142857))

        self.krasnodar_center().unit_zones.append(mapping.Rectangle(13360.857142856, 366714.28571429, 12360.857142856, 367714.28571429))
        self.krasnodar_center().unit_zones.append(mapping.Rectangle(13375.142857142, 367717.14285714, 12375.142857142, 368717.14285714))
        self.krasnodar_center().unit_zones.append(mapping.Rectangle(11072.285714285, 366687.14285714, 10372.285714285, 367387.14285714))
        self.krasnodar_center().unit_zones.append(mapping.Rectangle(15490.857142856, 361865.71428571, 12490.857142856, 364865.71428571))

        self.novorossiysk().unit_zones.append(mapping.Rectangle(-39022.285714285, 277836.85714285, -40122.285714285, 278936.85714285))
        self.novorossiysk().unit_zones.append(mapping.Rectangle(-40290.857142857, 279953.99999999, -40790.857142857, 280453.99999999))
        self.novorossiysk().unit_zones.append(mapping.Rectangle(-40255.142857142, 276589.71428571, -41155.142857142, 277489.71428571))

        self.krymsk().unit_zones.append(mapping.Rectangle(-6292.8571428566, 295422.85714286, -7292.8571428566, 296422.85714286))
        self.krymsk().unit_zones.append(mapping.Rectangle(-5878.5714285709, 292315.71428571, -6878.5714285709, 293315.71428571))
        self.krymsk().unit_zones.append(mapping.Rectangle(-4885.7142857137, 293180, -5885.7142857137, 294180))
        self.krymsk().unit_zones.append(mapping.Rectangle(-5414.2857142852, 295651.42857143, -6214.2857142852, 296451.42857143))

        self.maykop().unit_zones.append(mapping.Rectangle(-24574.285714285, 455938.57142857, -26574.285714285, 457938.57142857))
        self.maykop().unit_zones.append(mapping.Rectangle(-26888.571428571, 459010, -29088.571428571, 461210))
        self.maykop().unit_zones.append(mapping.Rectangle(-24917.142857142, 459945.71428572, -26717.142857142, 461745.71428572))
        self.maykop().unit_zones.append(mapping.Rectangle(-29138.57142857, 457451.42857144, -30738.57142857, 459051.42857144))

        self.gelendzhik().unit_zones.append(mapping.Rectangle(-50072.857142857, 296894.28571429, -50972.857142857, 297794.28571429))
        self.gelendzhik().unit_zones.append(mapping.Rectangle(-49435.714285714, 296528.57142857, -50135.714285714, 297228.57142857))
        self.gelendzhik().unit_zones.append(mapping.Rectangle(-50470, 298271.42857143, -51170, 298971.42857143))
        self.gelendzhik().unit_zones.append(mapping.Rectangle(-48665.714285714, 297704.28571428, -49265.714285714, 298304.28571428))

        self.krasnodar_pashkovsky().unit_zones.append(mapping.Rectangle(8105.7142857243, 388292.85714286, 6705.7142857243, 389692.85714286))
        self.krasnodar_pashkovsky().unit_zones.append(mapping.Rectangle(7184.2857142957, 384857.14285715, 6184.2857142957, 385857.14285715))
        self.krasnodar_pashkovsky().unit_zones.append(mapping.Rectangle(8848.5714285814, 386628.57142858, 7948.571428581399, 387528.57142858))
        self.krasnodar_pashkovsky().unit_zones.append(mapping.Rectangle(9570.0000000098, 383164.28571429, 8570.0000000098, 384164.28571429))

        self.sukhumi().unit_zones.append(mapping.Rectangle(-220484.28571428, 563282.85714286, -221084.28571428, 563882.85714286))
        self.sukhumi().unit_zones.append(mapping.Rectangle(-220081.42857143, 562380.00000001, -220681.42857143, 562980.00000001))
        self.sukhumi().unit_zones.append(mapping.Rectangle(-218804.28571429, 564057.14285715, -219404.28571429, 564657.14285715))
        self.sukhumi().unit_zones.append(mapping.Rectangle(-218895.71428571, 563268.57142858, -219495.71428571, 563868.57142858))
        self.sukhumi().unit_zones.append(mapping.Rectangle(-221415.71428571, 565074.28571429, -222015.71428571, 565674.28571429))

        self.gudauta().unit_zones.append(mapping.Rectangle(-196705.71428572, 516900, -197405.71428572, 517600))
        self.gudauta().unit_zones.append(mapping.Rectangle(-195732.85714286, 514945.71428571, -196332.85714286, 515545.71428571))
        self.gudauta().unit_zones.append(mapping.Rectangle(-195075.71428572, 516880, -195875.71428572, 517680))

        self.batumi().unit_zones.append(mapping.Rectangle(-356160, 616688.00000003, -356960, 617488.00000003))
        self.batumi().unit_zones.append(mapping.Rectangle(-357551.42857143, 614990.85714289, -358551.42857143, 615990.85714289))
        self.batumi().unit_zones.append(mapping.Rectangle(-355574.28571429, 615740.85714289, -356474.28571429, 616640.85714289))

        self.senaki().unit_zones.append(mapping.Rectangle(-281829.99999999, 646374.2857143, -282629.99999999, 647174.2857143))
        self.senaki().unit_zones.append(mapping.Rectangle(-280231.42857142, 645832.85714287, -280931.42857142, 646532.85714287))
        self.senaki().unit_zones.append(mapping.Rectangle(-282110, 645288.57142859, -282910, 646088.57142859))
        self.senaki().unit_zones.append(mapping.Rectangle(-281052.85714285, 648450.00000002, -281452.85714285, 648850.00000002))

        self.kobuleti().unit_zones.append(mapping.Rectangle(-319184.85714285, 636121.14285715, -320584.85714285, 637521.14285715))
        self.kobuleti().unit_zones.append(mapping.Rectangle(-317053.42857142, 634509.71428572, -317553.42857142, 635009.71428572))
        self.kobuleti().unit_zones.append(mapping.Rectangle(-317776.28571428, 634158.28571429, -318276.28571428, 634658.28571429))

        self.kutaisi().unit_zones.append(mapping.Rectangle(-285691.42857142, 683870.00000001, -286691.42857142, 684870.00000001))
        self.kutaisi().unit_zones.append(mapping.Rectangle(-285131.42857142, 685257.14285716, -286131.42857142, 686257.14285716))
        self.kutaisi().unit_zones.append(mapping.Rectangle(-283062.85714285, 682065.71428573, -283762.85714285, 682765.71428573))
        self.kutaisi().unit_zones.append(mapping.Rectangle(-283252.85714285, 685130.00000001, -283752.85714285, 685630.00000001))

        self.mineralnye().unit_zones.append(mapping.Rectangle(-50675.714285712, 706205.71428572, -51275.714285712, 706805.71428572))
        self.mineralnye().unit_zones.append(mapping.Rectangle(-52302.857142855, 704720, -53002.857142855, 705420))
        self.mineralnye().unit_zones.append(mapping.Rectangle(-51194.285714284, 701500, -52594.285714284, 702900))
        self.mineralnye().unit_zones.append(mapping.Rectangle(-48049.999999998, 706642.85714286, -48849.999999998, 707442.85714286))

        self.lochini().unit_zones.append(mapping.Rectangle(-315025.71428571, 894574.28571429, -316225.71428571, 895774.28571429))
        self.lochini().unit_zones.append(mapping.Rectangle(-316225.71428571, 896138.57142857, -317425.71428571, 897338.57142857))
        self.lochini().unit_zones.append(mapping.Rectangle(-314582.85714286, 897795.71428571, -315982.85714286, 899195.71428571))

        self.soganlug().unit_zones.append(mapping.Rectangle(-318431.42857142, 894650.00000001, -318931.42857142, 895150.00000001))
        self.soganlug().unit_zones.append(mapping.Rectangle(-318949.99999999, 894894.28571429, -319549.99999999, 895494.28571429))
        self.soganlug().unit_zones.append(mapping.Rectangle(-318215.7142857, 897200.00000001, -319215.7142857, 898200.00000001))

        self.vaziani().unit_zones.append(mapping.Rectangle(-318605.71428571, 901664.28571429, -319605.71428571, 902664.28571429))
        self.vaziani().unit_zones.append(mapping.Rectangle(-319434.28571428, 902484.28571429, -320434.28571428, 903484.28571429))
        self.vaziani().unit_zones.append(mapping.Rectangle(-318435.71428571, 904565.71428572, -319435.71428571, 905565.71428572))
        self.vaziani().unit_zones.append(mapping.Rectangle(-316582.85714285, 903304.28571429, -317582.85714285, 904304.28571429))

        self.sochi().unit_zones.append(mapping.Rectangle(-164637.14285714, 461964.28571428, -165237.14285714, 462564.28571428))
        self.sochi().unit_zones.append(mapping.Rectangle(-162801.42857142, 460978.57142857, -163601.42857142, 461778.57142857))
        self.sochi().unit_zones.append(mapping.Rectangle(-165514.28571428, 461815.71428571, -165914.28571428, 462215.71428571))

        # for x in sorted(self.airports, key=lambda x: self.airports[x].id):
        #     airport = self.airports[x]
        #     print("airports[{id}] = {{'id': {id}, 'name': '{name}', 'tacan':{tacan}, 'runways': []}}".format(
        #         id=airport.id, name=x, tacan=airport.tacan if airport.tacan else None
        #     ))
        #     for r in self.airports[x].runways:
        #         print("airports[{id}]['runways'].append({hdg})".format(id=airport.id, hdg=r.heading))

    def soganlug(self) -> Airport:
        return self.airports["Soganlug"]

    def senaki(self) -> Airport:
        return self.airports["Senaki"]

    def sochi(self) -> Airport:
        return self.airports["Sochi"]

    def batumi(self) -> Airport:
        return self.airports["Batumi"]

    def nalchik(self) -> Airport:
        return self.airports["Nalchik"]

    def beslan(self) -> Airport:
        return self.airports["Beslan"]

    def mozdok(self) -> Airport:
        return self.airports["Mozdok"]

    def anapa(self) -> Airport:
        return self.airports["Anapa"]

    def krasnodar_center(self) -> Airport:
        return self.airports["Krasnodar-Center"]

    def krasnodar_pashkovsky(self) -> Airport:
        return self.airports["Krasnodar-Pashkovsky"]

    def novorossiysk(self) -> Airport:
        return self.airports["Novorossiysk"]

    def krymsk(self) -> Airport:
        return self.airports["Krymsk"]

    def maykop(self) -> Airport:
        return self.airports["Maykop"]

    def gelendzhik(self) -> Airport:
        return self.airports["Gelendzhik"]

    def mineralnye(self) -> Airport:
        return self.airports["Mineralnye"]

    def gudauta(self) -> Airport:
        return self.airports["Gudauta"]

    def vaziani(self) -> Airport:
        return self.airports["Vaziani"]

    def lochini(self) -> Airport:
        return self.airports["Lochini"]

    def kobuleti(self) -> Airport:
        return self.airports["Kobuleti"]

    def kutaisi(self) -> Airport:
        return self.airports["Kutaisi"]

    def sukhumi(self) -> Airport:
        return self.airports["Sukhumi"]

    def default_red_airports(self) -> List[Airport]:
        return [
            self.anapa(),
            self.krymsk(),
            self.novorossiysk(),
            self.krasnodar_center(),
            self.krasnodar_pashkovsky(),
            self.maykop(),
            self.gelendzhik(),
            self.mineralnye(),
            self.mozdok(),
            self.beslan(),
            self.nalchik(),
            self.sochi()
        ]

    def default_blue_airports(self) -> List[Airport]:
        return [
            self.batumi(),
            self.vaziani(),
            self.soganlug(),
            self.kobuleti(),
            self.senaki(),
            self.lochini(),
            self.kutaisi()
        ]