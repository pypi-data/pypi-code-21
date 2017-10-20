import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.dlib
import pkg_resources
import os
from matplotlib import pyplot
import bob.ip.draw
import bob.ip.facedetect

#print "###################################"
#print os.path.join(pkg_resources.resource_filename(__name__, 'data'), 'multiple-faces.jpg')

# detect multiple bob
bob_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bob_bounding_box, _ = bob.ip.facedetect.detect_single_face(bob_color_image)

# detect multiple dlib
dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
dlib_bounding_box, _ = bob.ip.dlib.FaceDetector().detect_single_face(dlib_color_image)

# landmarks
detector = bob.ip.dlib.DlibLandmarkExtraction()
points_dlib = detector(dlib_color_image)
points_bob = detector(bob_color_image, bb=bob_bounding_box)
for p in points_bob:
    bob.ip.draw.plus(bob_color_image, p, radius=10, color=(255, 0, 0))

for p in points_dlib:
    bob.ip.draw.plus(dlib_color_image, p, radius=10, color=(255, 0, 0))


# face detections
bob.ip.draw.box(bob_color_image, bob_bounding_box.topleft, bob_bounding_box.size, color=(255, 0, 0))
bob.ip.draw.box(dlib_color_image, dlib_bounding_box.topleft, dlib_bounding_box.size, color=(255, 0, 0))


ax = pyplot.subplot(1, 2, 1)
ax.set_title("Dlib")
pyplot.imshow(bob.ip.dlib.utils.bob_to_dlib_image_convertion(dlib_color_image, change_color=False))
pyplot.axis('off')

ax = pyplot.subplot(1, 2, 2)
ax.set_title("Bob")
pyplot.imshow(bob.ip.dlib.utils.bob_to_dlib_image_convertion(bob_color_image, change_color=False))
pyplot.axis('off')

