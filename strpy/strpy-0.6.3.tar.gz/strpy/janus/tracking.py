import sys
import math

from bobo.video import VideoDetection

class SimpleTracker(object):
    """Takes an iterable container of object detections, where the elements
    represent one frame of time-ordered video and where each element is a tuple
    of an Image and a list of BoundingBox detections.  It generates
    VideoDetections using simple overlap and missed detection metrics to
    create single-subject videos when iterated over.
    """
    def __init__(self, image_detections=None, min_num_track_dets=4, max_num_track_dets=sys.maxint, max_num_track_missed_dets=5, min_dist=80, height_lower_bound=None, debug=False):
        self.min_num_track_dets = min_num_track_dets
        self.max_num_track_dets = max_num_track_dets
        self.max_num_track_missed_dets = max_num_track_missed_dets
        self.min_dist = min_dist
        self.height_lower_bound = height_lower_bound
        self.imagedetections = image_detections
        self.seen_objs = []
        self.drop_frames = []
        self.debug = debug
        self.indices_to_remove = []

    def activetrackcount(self):
        return len(self.seen_objs) - len(self.indices_to_remove)

    def __iter__(self):
        """Generates VideoDetection tracks from a generator that yields sets of ImageDetections for frames"""

        def _distance(box1, box2):
            """distance between two bounding box centroids"""
            x1, y1 = box1.centroid()
            x2, y2 = box2.centroid()
            dis = (math.sqrt((x1-x2)**2 + (y1-y2)**2))
            return dis

        def _overlap(box1, box2):
            """Area of intersection / area of union for two bounding boxes"""
            return 0 if (box1.area() < 1 or box2.area() < 1) else box1.overlap(box2)

        def _bestmatch(bbox, list_to_compare):
            ret = [(_overlap(bbox, x), x) for x in list_to_compare]
            return ret

        def _bestdis(bbox, list_to_compare):
            return [(_distance(bbox, x), x) for x in list_to_compare]

        for frame_dets in self.imagedetections():
            if len(frame_dets) == 0: continue
            im = frame_dets[0].clone()
            bboxes = [im.boundingbox() for im in frame_dets]

            # All BoundingBox detections are from a single image
            if self.height_lower_bound is not None:
                bboxes = filter(lambda box: box.height() >= self.height_lower_bound, bboxes)

            for print_index, printer in enumerate(self.seen_objs):
                if self.debug:
                    print "num of objs in list {0}: ".format(print_index), len(printer)

                if len(self.seen_objs) < 1:# or len(self.seen_objs) < len(bboxes):  #seed list of lists with objs
                        self.seen_objs = [im.clone().boundingbox(bbox=box) for box in bboxes]
                        for x in bboxes:
                            self.drop_frames.append(0)
                        if self.debug:
                            print "len(self.seen_objs): ",len(self.seen_objs)

            objs = []
            objs = [obj[-1].boundingbox() for obj in self.seen_objs] #grab last element of each obj list

            more_boxes = [x for x in bboxes]

            self.indices_to_remove = []
            for obj_idx, obj in enumerate(objs):
                if len(more_boxes) > 0:
                    same_obj = max(_bestmatch(obj, more_boxes)) #bestmatch returns a tuple of (overlap, boundingbox instance)
                    if same_obj[0] > 1: #match box with most overlap
                        idx = bboxes.index(same_obj[1])
                        other_idx = more_boxes.index(same_obj[1])
                        more_boxes.pop(other_idx)
                        self.seen_objs[obj_idx].append(im.clone().boundingbox(bbox=bboxes[idx]))
                        if len(self.seen_objs[obj_idx]) > self.max_num_track_dets:
                            yield VideoDetection(frames=self.seen_objs[obj_idx])
                            self.indices_to_remove.append(obj_idx)

                    elif min(_bestdis(obj, more_boxes))[0] < self.min_dist: # not box greater than 1 overlap so match closest
                        closest = min(_bestdis(obj, more_boxes))
                        idx = bboxes.index(closest[1])
                        other_idx = more_boxes.index(closest[1])
                        more_boxes.pop(other_idx)
                        self.seen_objs[obj_idx].append(im.clone().boundingbox(bbox=bboxes[idx]))

                        if len(self.seen_objs[obj_idx]) > self.max_num_track_dets:
                            yield VideoDetection(frames=self.seen_objs[obj_idx])
                            self.indices_to_remove.append(obj_idx)

                    else: #no good boxes to match
                        self.drop_frames[obj_idx] = self.drop_frames[obj_idx] + 1
                        if self.drop_frames[obj_idx] > self.max_num_track_missed_dets:
                            self.indices_to_remove.append(obj_idx)
                            if len(self.seen_objs[obj_idx]) > self.min_num_track_dets:
                                yield VideoDetection(frames=self.seen_objs[obj_idx])
                            if self.debug:
                                print '[janus.tracking.simpletracker]: Removed indx[%d] with length [%d] for missed detections [%d] case1' % (obj_idx, len(self.seen_objs[obj_idx]), self.drop_frames[obj_idx])

                else: #no good boxes to match
                    self.drop_frames[obj_idx] = self.drop_frames[obj_idx] + 1
                    if self.drop_frames[obj_idx] > self.max_num_track_missed_dets:
                        self.indices_to_remove.append(obj_idx)
                        if len(self.seen_objs[obj_idx]) > self.min_num_track_dets:
                            yield VideoDetection(frames=self.seen_objs[obj_idx])
                        if self.debug:
                            print '[janus.tracking.simpletracker]: Removed indx[%d] with length [%d] for missed detections [%d] case2' % (obj_idx, len(self.seen_objs[obj_idx]), self.drop_frames[obj_idx])

            for box in more_boxes:
                self.seen_objs.append([im.clone().boundingbox(bbox=box)])
                self.drop_frames.append(0)

            if len(self.indices_to_remove) > 0:
                # remove from back to keep indices stable while removing
                indices = sorted(self.indices_to_remove, reverse=True)
                for x in indices:
                    if self.debug:
                        print '[janus.tracking.simpletracker]: Removing idx[%d]' % x
                    del self.seen_objs[x]
                    del self.drop_frames[x]

        # Send final valid detections at end of video
        while len(self.seen_objs) > 0:
            if len(self.seen_objs[0]) > self.min_num_track_dets:
                yield VideoDetection(frames=self.seen_objs[0])
            del self.seen_objs[0]
        print '[janus.tracking.SimpleTracker] Done.'
