#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CellDetector.py

# Copyright (c) 2015-2016, Richard Gerum, Sebastian Richter
#
# This file is part of ClickPoints.
#
# ClickPoints is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ClickPoints is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClickPoints. If not, see <http://www.gnu.org/licenses/>

import sys
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import eig, inv
from skimage.measure import regionprops, label
import clickpoints


def moveInDirection(startx, starty, dir, im, factor, maximum):
    cut = np.zeros(maximum)
    for i in range(maximum):
        y, x = int(starty + i * dir[1]), int(startx + i * dir[0])
        if 0 < y < im.shape[0] and 0 < x < im.shape[1] and im[y, x] != 0:
            cut[i] = im[y, x]
        else:
            i -= 1
            break
            #        if(A(uint16(starty+i*delta(2)),uint16(startx+i*delta(1))) < lightness)
            #            break;
            #        end

    line = cut[:i]
    smooth = 5
    if len(line) > smooth + 1:
        smoothline = np.zeros(len(line) - smooth)
        for i in range(len(line) - smooth):
            smoothline[i] = np.mean(line[i:i + smooth])
        # difference = diff(smoothline)
        maxdiff = -np.min(np.diff(smoothline))  # /(max(line)-min(line))
    else:
        maxdiff = 0

    for i in range(len(line)):
        if line[i] <= np.max(line) * factor + np.min(line) * (1 - factor):
            break
    else:
        i = 0

    # i = i(1);
    #     if i ~= 1 && line(1) == min(line)
    #         'ERRRRRRRORRRR'
    #         'bla'
    #     end
    x = startx + i * dir[0]
    y = starty + i * dir[1]
    l = np.sqrt((i * dir[0]) ** 2 + (i * dir[1]) ** 2)

    return x, y, l, maxdiff


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / N


def moveInDirection(startx, starty, dir, im, factor, maximum):
    pos = np.array([startx, starty])
    cut = np.zeros(maximum)
    for i in range(maximum):
        x, y = (pos + i * dir).astype(int)
        if 0 < y < im.shape[0] and 0 < x < im.shape[1] and im[y, x] != 0:
            cut[i] = im[y, x]
        else:
            i -= 1
            break

    line = cut[:i]
    smooth = 5
    if len(line) > smooth + 1:
        smoothline = running_mean(line, smooth)
        maxdiff = -np.min(np.diff(smoothline))
    else:
        maxdiff = 0

    for i in range(len(line)):
        if line[i] <= np.max(line) * factor + np.min(line) * (1 - factor):
            break
    else:
        i = 0

    x, y = pos + i * dir
    l = np.linalg.norm(i * dir)

    return x, y, l, maxdiff


def fitEllipse(x, y):
    x = x[:, np.newaxis]
    y = y[:, np.newaxis]
    D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
    S = np.dot(D.T, D)
    C = np.zeros([6, 6])
    C[0, 2] = C[2, 0] = 2
    C[1, 1] = -1
    E, V = eig(np.dot(inv(S), C))
    n = np.argmax(np.abs(E))
    a = V[:, n]
    return a


def ellipse_center(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    num = b * b - a * c
    x0 = (c * d - b * f) / num
    y0 = (a * f - b * d) / num
    return np.array([x0, y0])


def ellipse_angle_of_rotation(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    return 0.5 * np.arctan(2 * b / (a - c))


def ellipse_axis_length(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    up = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
    down1 = (b * b - a * c) * ((c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    down2 = (b * b - a * c) * ((a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    #if up < 0 or down1 < 0 or down2 < 0:
    #    return np.array([0, 0])
    res1 = np.sqrt(up / down1)
    res2 = np.sqrt(up / down2)
    return np.array([res1, res2])


def ellipse_angle_of_rotation2(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    if b == 0:
        if a > c:
            return 0
        else:
            return np.pi / 2
    else:
        if a > c:
            return np.arctan(2 * b / (a - c)) / 2
        else:
            return np.pi / 2 + np.arctan(2 * b / (a - c)) / 2


def mask_polygon(poly_verts, shape):
    from matplotlib.nxutils import points_inside_poly

    nx, ny = shape

    # Create vertex coordinates for each grid cell...
    # (<0,0> is at the top left of the grid in this system)
    x, y = np.meshgrid(np.arange(nx), np.arange(ny))
    x, y = x.flatten(), y.flatten()

    points = np.vstack((x, y)).T

    grid = points_inside_poly(points, poly_verts)
    grid = grid.reshape((ny, nx))

    return grid


def mask_polygon(polygon, width, height):
    from PIL import Image, ImageDraw

    # polygon = [(x1,y1),(x2,y2),...] or [x1,y1,x2,y2,...]
    # width = ?
    # height = ?

    img = Image.new('L', (width, height), 0)
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    mask = np.array(img)
    return mask


def count_old(im, progressbar, progress_offset):
    # im = plt.imread(bild)

    im = im.astype("float") / im.max()

    # declare variables
    steps = 16
    points = np.zeros([steps, 2])
    rot = np.array([[np.cos(np.pi * 2 / steps), np.sin(np.pi * 2 / steps)],
                    [-np.sin(np.pi * 2 / steps), np.cos(np.pi * 2 / steps)]])  # rotation matrix

    points_found = []

    sizes = []

    thresholds = np.arange(0.9, 0.1, -0.05)

    for index, i in enumerate(thresholds):
        progressbar.emit(index*100/thresholds.shape[0]+progress_offset)
        print(i)

        labels = label(im > i)
        props = regionprops(labels)
        for prop in props:
            # reject small areas
            if not (10 * 10 < prop.area < 10000):
                continue

            # get coordinates of the object
            y, x = prop.centroid

            # test if the center is inside the object
            if labels[int(y), int(x)] == 0:
                continue

            # get main axis
            a = prop.orientation

            # starting direction
            dir = np.array([np.cos(a), -np.sin(a)])

            # Test 20 pixels in every direction and find the point where the
            # relative intensity reaches 30% of the maximum
            for k in range(steps):
                dir = np.dot(rot, dir)
                x1, x2, l, maxdiff = moveInDirection(x, y, dir, im, 0.3, 30)
                points[k, :] = [x1, x2]

            # Fit an ellipse and plot it
            try:
                ellipse = fitEllipse(points[:, 0], points[:, 1])
            except np.linalg.linalg.LinAlgError:
                continue

            # get the parameter of the ellipse
            center = ellipse_center(ellipse)
            x0, y0 = center
            phi = ellipse_angle_of_rotation(ellipse)
            a, b = ellipse_axis_length(ellipse)

            # if it is not valid continue
            if np.isnan(a) or np.isnan(b):
                continue

            # calculate points of the ellipse
            R = np.linspace(0, 2 * np.pi, steps)
            X = center[0] + a * np.cos(R) * np.cos(phi) - b * np.sin(R) * np.sin(phi)
            Y = center[1] + a * np.cos(R) * np.sin(phi) + b * np.sin(R) * np.cos(phi)

            # Test 20 pixels in every direction and find the point where the
            # relative intensity reaches 30% of the maximum
            dist = 0
            maxdiffsum = np.zeros(steps)
            for k in range(steps):
                len = np.sqrt((X[k] - x0) ** 2 + (Y[k] - y0) ** 2)
                x1, x2, l, maxdiff = moveInDirection(x0, y0, np.array([(X[k] - x0), (Y[k] - y0)]) / len, im, 0.3, 30)
                points[k, :] = [x1, x2]
                dist = dist + np.sqrt((X[k] - x1) ** 2 + (Y[k] - x2) ** 2)
                maxdiffsum[k] = maxdiff

            EllipseSize = a * b * np.pi
            if min(maxdiffsum) * steps < 0.3:
                pass
                # plt.plot(x0, y0, '*r')
                # continue

            if EllipseSize < 10:
                plt.plot(x0, y0, '*b')
                continue

            if dist > 30:
                plt.plot(x0, y0, '*y')
                continue

            sizes.append(EllipseSize)

            # mask the found ellipse area
            x1 = int(np.min(X))
            y1 = int(np.min(Y))
            w = int(np.max(X)) - x1
            h = int(np.max(Y)) - y1
            polygon = [(x - x1, y - y1) for x, y in zip(X[:-1], Y[:-1])]
            mask = 1 - mask_polygon(polygon, int(w), int(h))
            im[y1:y1 + h, x1:x1 + w] *= mask

            # add the point to the found points
            points_found.append((float(x0), float(y0)))

    #plt.imshow(im)
    #plt.show()
    print(max(sizes))

    # return the result
    return np.array(points_found)


def count(im):
    import cv2
    from scipy.signal import wiener
    print(cv2.__version__)
    # im = plt.imread(bild)

    # Take the mean over all colors
    # a = np.mean(A, 3)
    # normalize the image to 1
    im = im - im.min()
    im = im.astype("float") / im.max()
    im = wiener(im, 5)
    im = (im * 255).astype("uint8")
    print(im, im.dtype, im.max(), im.min())
    # plt.imshow(im)
    # plt.show()

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()
    # Change thresholds
    params.minThreshold = 10;
    params.maxThreshold = 200;

    # Filter by Area.
    params.filterByArea = False
    params.minArea = 1500

    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0.01

    params.filterByColor = 1
    params.blobColor = 255

    for name in dir(params):
        print(name)

    # params.minDistBetweenBlobs = 10
    print(
    params.minThreshold, params.maxThreshold, params.filterByArea, params.thresholdStep, params.minDistBetweenBlobs)

    # Set up the detector with default parameters.
    ver = (cv2.__version__).split('.')
    if int(ver[0]) < 3:
        detector = cv2.SimpleBlobDetector(params)
    else:
        detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(im)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Show keypoints
    # cv2.imshow("Keypoints", im_with_keypoints)
    # cv2.waitKey(0)

    print(keypoints)
    for key in keypoints:
        print(key.octave)
        # plt.plot(key.pt[0], key.pt[1], 'ro')
        # plt.text(key.pt[0], key.pt[1], key.size)
    print(np.array([key.pt for key in keypoints]))
    return np.array([key.pt for key in keypoints])
    # plt.imshow(im, cmap="gray")
    # plt.show()


from qtpy import QtCore, QtGui, QtWidgets
from clickpoints.includes.QtShortCuts import AddQComboBox, AddQSaveFileChoose, AddQSpinBox, AddQLineEdit
from clickpoints.includes.matplotlibwidget import MatplotlibWidget, NavigationToolbar
import peewee


class Addon(clickpoints.Addon):
    signal_detection_finished = QtCore.Signal()
    signal_update_progress = QtCore.Signal(float)

    def __init__(self, *args, **kwargs):
        clickpoints.Addon.__init__(self, *args, **kwargs)
        self.setWindowTitle("CellCompare - ClickPoints")

        self.layout = QtWidgets.QVBoxLayout(self)

        # add a mode selector, which formatting should be used for the output
        self.addOption(key="celltype", display_name="Cell Type", value_type="string",
                       tooltip="How many images to use for the kymograph.")
        self.input_celltype = AddQLineEdit(self.layout, "Cell Type:", value=self.getOption("celltype"))
        self.linkOption("celltype", self.input_celltype)

        # add a mode selector, which formatting should be used for the output
        self.addOption(key="condition1", display_name="Condition 1", value_type="string",
                       tooltip="How many images to use for the kymograph.")
        self.input_condition1 = AddQLineEdit(self.layout, "Condition 1:", value=self.getOption("condition1"))
        self.linkOption("condition1", self.input_condition1)

        # add a mode selector, which formatting should be used for the output
        self.addOption(key="condition2", display_name="Condition 2", value_type="string",
                       tooltip="How many images to use for the kymograph.")
        self.input_condition2 = AddQLineEdit(self.layout, "Condition 2:", value=self.getOption("condition2"))
        self.linkOption("condition2", self.input_condition2)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(line)

        try:
            if self.db.getMarkers(type="marker").count() == 0:
                self.db.deleteMarkerTypes(name="marker")
        except peewee.DoesNotExist:
            pass

        # Check if the marker type is present
        self.marker_type1 = self.db.setMarkerType("cell_found", [0, 0, 255], self.db.TYPE_Normal)
        self.marker_type2 = self.db.setMarkerType("cell_missing", [255, 0, 0], self.db.TYPE_Normal, style='{"shape":"circle-o", "scale": 3}')
        self.marker_type3 = self.db.setMarkerType("cell_addition", [0, 255, 0], self.db.TYPE_Normal)
        self.marker_type4 = self.db.setMarkerType("cell_outside", "#cacaca", self.db.TYPE_Normal)
        self.marker_type = self.db.setMarkerType("offset", [255, 255, 0], self.db.TYPE_Track)
        self.cp.reloadTypes()

        self.button_detect = QtWidgets.QPushButton("Detect Cells")
        self.button_detect.clicked.connect(self.detectCells)
        self.layout.addWidget(self.button_detect)

        self.progressbar = QtWidgets.QProgressBar()
        self.layout.addWidget(self.progressbar)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(line)

        self.button_offset = QtWidgets.QPushButton("Apply Offset")
        self.button_offset.clicked.connect(self.applyOffset)
        self.layout.addWidget(self.button_offset)

        self.button_pairs = QtWidgets.QPushButton("Find Pairs")
        self.button_pairs.clicked.connect(self.findPairs)
        self.layout.addWidget(self.button_pairs)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(line)

        self.button_plot = QtWidgets.QPushButton("Update Plot")
        self.button_plot.clicked.connect(self.doPlot)
        self.layout.addWidget(self.button_plot)

        self.plot = MatplotlibWidget(self)
        self.layout.addWidget(self.plot)
        #self.layout.addWidget(NavigationToolbar(self.plot, self))

        self.signal_detection_finished.connect(self.detectionFinishedEvent)
        self.signal_update_progress.connect(lambda x: self.progressbar.setValue(x))

    def applyOffset(self):
        tracks = self.db.getTracks(type="offset")
        for track in tracks:
            print(track)
            f = track.image_ids
            points = track.points
            points = points - points[0, :]
            for id, p in zip(f, points):
                print(p)
                self.db.setOffset(image=id, x=-p[0], y=-p[1])

    def findPairs(self):
        markers = self.db.getMarkers(type=self.marker_type3)
        for marker in markers:
            marker.changeType(self.marker_type1)
        markers = self.db.getMarkers(type=self.marker_type4)
        for marker in markers:
            marker.changeType(self.marker_type1)

        self.db.deleteMarkers(type=self.marker_type2)

        im1 = self.db.getImage(0)
        im2 = self.db.getImage(1)
        im2_shape = im2.data.shape
        if im2.offset:
            offx, offy = im2.offset.x, im2.offset.y
        markers1 = self.db.getMarkers(image=im1, type=self.marker_type1)
        markers2 = self.db.getMarkers(image=im2, type=self.marker_type1)
        markers2 = [m for m in markers2]
        markers1 = [m for m in markers1]
        print("marker1", len(markers1))
        print("marker2", len(markers2))
        not_used = np.ones(len(markers2), dtype="bool")
        markers2_pos = np.array([m.correctedXY() for m in markers2])
        for marker in markers1:
            print(markers2_pos.shape)
            distances = np.linalg.norm(markers2_pos-marker.correctedXY(), axis=1)
            distances[not_used == False] = 9999
            if np.min(distances) < 30:
                print("Found", np.min(distances))
                not_used[np.argmin(distances)] = False
            else:
                print("Found", np.min(distances), marker.x, offx)
                if marker.x > offx and marker.y > offy:
                    self.db.setMarker(image=im2, type=self.marker_type2, x=marker.x-offx, y=marker.y-offy)
                else:
                    marker.type = self.marker_type4
                    marker.save()
        for index in np.arange(len(markers2))[not_used]:
            marker = markers2[index]
            if marker.x < im2_shape[1]-offx and marker.y < im2_shape[0]-offy:
                marker.type = self.marker_type3
            else:
                marker.type = self.marker_type4
            marker.save()
        self.cp.jumpToFrame(1)
        self.cp.reloadMarker()
        self.doPlot()

    def doPlot(self):
        #self.plot.axes.set_xlabel(u"distance (µm)")
        im2 = self.db.getImage(1)
        count1 = self.db.getMarkers(image=im2, type=self.marker_type1).count()
        count2 = self.db.getMarkers(image=im2, type=self.marker_type2).count()
        count3 = self.db.getMarkers(image=im2, type=self.marker_type3).count()
        count_total = count1 + count2
        self.plot.axes.clear()
        self.plot.axes.set_ylabel("cells (%)")
        self.plot.axes.set_ylim(0, 100)
        self.plot.axes.bar(0, count1/count_total*100, color="C0")
        self.plot.axes.text(0, count1 / count_total * 100 + 5, "# %d" % count1, ha="center")
        self.plot.axes.bar(1, count2/count_total*100, color="C3")
        self.plot.axes.text(1, count2 / count_total * 100 + 5, "# %d" % count2, ha="center")
        self.plot.axes.bar(2, count3/count_total*100, color="C2")
        self.plot.axes.text(2, count3 / count_total * 100 + 5, "# %d" % count3, ha="center")
        self.plot.axes.set_xticks([0, 1, 2])
        self.plot.axes.set_xticklabels(["adherent", "vanished", "added"])
        self.plot.axes.spines['right'].set_visible(False)
        self.plot.axes.spines['top'].set_visible(False)
        self.plot.axes.yaxis.set_ticks_position('left')
        self.plot.axes.xaxis.set_ticks_position('bottom')
        self.plot.figure.tight_layout()
        self.plot.draw()

    def detectCells(self):
        if self.is_running():
            self.terminate()
        else:
            self.db.deleteMarkers(type=self.marker_type1)
            self.db.deleteMarkers(type=self.marker_type2)
            self.db.deleteMarkers(type=self.marker_type3)
            self.db.deleteMarkers(type=self.marker_type4)
            self.button_detect.setText("Stop Detection")
            self.run_threaded(0)

    def detectionFinishedEvent(self):
        self.button_detect.setText("Detect Cells")

    def run(self, start_frame=0):
        # get images and mask_types
        images = self.db.getImages()

        self.progressbar.setMaximum(images.count()*100)

        # iterate over all images
        for index, image in enumerate(images):
            print(image.filename)
            data = image.data
            if len(data.shape) == 3:
                data = np.mean(image.data, axis=2)
            p1 = count_old(data, self.signal_update_progress, 100*index)

            self.db.deleteMarkers(image=image.id, type=self.marker_type1)
            self.db.setMarkers(image=image.id, x=p1[:, 0], y=p1[:, 1], type=self.marker_type1)
            self.cp.reloadMarker(image.sort_index)

            # check if we should terminate
            if self.cp.hasTerminateSignal():
                print("Cancelled cell detection")
                self.signal_detection_finished.emit()
                return

        self.signal_update_progress.emit(images.count() * 100)
        self.signal_detection_finished.emit()
        print("done")

    def buttonPressedEvent(self):
        self.show()
