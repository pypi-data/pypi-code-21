import os
from csv import DictWriter
from glob import glob
from math import floor, ceil
from shutil import rmtree

import numpy as np
from scipy.spatial.distance import mahalanobis

from bobo.util import remkdir, filebase, Stopwatch, tolist, filepath, fileext, quietprint
from bobo.image import Image, ImageDetection
from bobo.video import VideoCapture
from bobo.videosearch import youtube, isactiveyoutuber, download as videosearch_download

from janus.frontalize import Frontalizer
from janus.detection import DlibObjectDetector, DlibShapePredictor
from janus.tracking import SimpleTracker
from janus.visualize import montage
from viset.dlib import DlibDetections, BASE_SCHEMA, TRACK_SCHEMA, POSE_SCHEMA, landmarks


def relimfile(im):
    fn = os.path.join(filebase(filepath(im.filename())), filebase(im.filename())+fileext(im.filename()))
    return fn


class VideoPipeline(object):
    def __init__(self, outdir, videofile, ext='.jpg', target_framerate=5, max_video_seconds=300, duration_threshold=15, write_images=True, write_montage=False, subsampler=None):
        self.videofile = videofile
        self.basename = filebase(videofile)
        self.outdir = outdir
        self.trackscsvfile = os.path.join(outdir, '%s.csv' % self.basename)
        self.metricsfile = os.path.join(outdir, '%s_metrics.txt' % self.basename)
        self.videodetections = []
        self.num_frames = 0
        self.ext = ext
        self.target_framerate = target_framerate
        self.max_video_seconds = max_video_seconds
        self.write_images = write_images
        self.write_montage = write_montage
        self.subsampler = subsampler

        self.capture = None
        self.tracker = None
        self.video_seconds = 0.0
        self.track_metrics = {}
        self.video_metrics = {}

        # Metrics
        self.start_threshold = 20 # Number of seconds by which a track has to start
        self.xdist_threshold = 0.2
        self.wr_threshold = 0.95
        self.duration_threshold = duration_threshold # Number of seconds long
        self.fps = 0.0

    def process(self):
        if os.path.isfile(self.trackscsvfile):
            print '[janus.video.pipeline]: Skipping processed video [%s]' % self.basename
            return self

        try:
            [_ for _ in self.calcmetrics()]
            self.dometrics()
            if self.subsampler:
                self.writesubsample()
            else:
                self.writetrackdetections()
                self.writemontage()
        except:
            print '[janus.video.pipeline]: Error processing [%s]' % self.basename
            raise
        finally:
            self.clear() # Reduce memory usage
            self.capture = None # Prevent Spark from trying to pickle cv2.VideoCapture
            self.tracker = None # Spark doesn't like to pickle generators either
        return self

    def clear(self):
        [im.flush() for vid in self.videodetections for im in vid]

    def remove(self, do_video=True, do_detections=True, do_metrics=False):
        """Removes downloaded videos"""
        imgoutdir = os.path.join(self.outdir, self.basename)
        if do_video and os.path.isfile(self.videofile):
            quietprint('[janus.video.videopipeline.remove]: removing video file: [%s]' % self.videofile, 2)
            os.remove(self.videofile)
        if do_detections and os.path.isfile(self.trackscsvfile):
            quietprint('[janus.video.videopipeline.remove]: removing detections file: [%s]' % self.trackscsvfile, 2)
            os.remove(self.trackscsvfile)
        if do_detections and os.path.isdir(imgoutdir):
            quietprint('[janus.video.videopipeline.remove]: removing images: [%s]' % imgoutdir, 2)
            rmtree(imgoutdir)
        if do_metrics and os.path.isfile(self.metricsfile):
            quietprint('[janus.video.videopipeline.remove]: removing metrics: [%s]' % self.metricsfile, 2)
            os.remove(self.metricsfile)

    def filter_no_first_good(self, do_video=True, do_detections=True, do_metrics=False):
        first_good = [t for t in self.videodetections if self._passes_metrics(self.track_metrics[t.attributes['TRACK_ID']])]
        if  len(first_good) == 0:
            self.remove(do_video=do_video, do_detections=do_detections, do_metrics=do_metrics)
            return False
        else:
            return True


    def _passes_metrics(self, m, first_good_only=True):
        return ((not first_good_only or float(m['track_start']) <= self.start_threshold) and # near beginning?
                float(m['xdist']) <= self.xdist_threshold and # near center?
                float(m['wr'] >= self.wr_threshold) and # mostly alone on camera?
                float(m['track_duration']) >= self.duration_threshold # we are long enough
                )

    def detectvideo(self):
        """Processes a videofile into frames and detections."""
        if not os.path.isfile(self.videofile):
            print '[janus.video.detectvideo]: Video file not found: %s' % self.videofile
            raise StopIteration

        detector = DlibObjectDetector()
        predictor = DlibShapePredictor()

        SCHEMA = BASE_SCHEMA
        print '[video.pipeline.detect] Processing [%s]' % (self.videofile)

        self.capture = VideoCapture(self.videofile, do_msec=True)
        fps = self.capture.fps

        self.num_frames = self.capture.num_frames
        self.fps = self.capture.fps
        self.fps = max(1, self.fps)  # avoid div-by-zero
        self.video_seconds = self.num_frames / float(self.fps)

        # 5.997 = 29.97 / 5 => 5.997
        # ceil(5.997) -> 6
        downsample_rate = max(1, int(ceil(float(fps) / self.target_framerate)))

        print '[janus.video.detectvideo]: [%s] num_frames [%d], fps [%.2f], seconds [%.1f], downsample_rate [%d]' % (self.basename, self.num_frames, float(self.fps), self.video_seconds, downsample_rate)

        kf = 0
        with Stopwatch() as sw:
            for kf, (msec, frame) in enumerate(self.capture):
                if (downsample_rate > 1) and (kf % downsample_rate != 0):
                    continue

                # Stop pipeline if we have no active tracks past the start threshold
                if msec / 1.e3 > self.start_threshold:
                    if self.tracker is None or self.tracker.activetrackcount() < 1:
                        print '[janus.video.detectvideo]: Ending detection on %s with no active tracks after %.1fs' % (self.basename, msec / 1.e3)
                        raise StopIteration

                if (self.max_video_seconds > 0) and (msec / 1.e3 > self.max_video_seconds):
                    print '[janus.video.detectvideo]: Ending detection on %s at max length %.1fs' % (self.basename, msec / 1.e3)
                    raise StopIteration

                framefn = '%s/%08d%s' % (self.basename, int(floor(msec)), self.ext)
                impath = os.path.join(self.outdir, framefn)
                im = ImageDetection(impath)
                im.data = frame

                if kf% (downsample_rate * 100) == 0:
                   print 'Processing %s' % impath

                bboxes = detector(im)
                landmarks = predictor(im, bboxes, aflw_order=True)

                if len(bboxes) == 0:
                   continue # missed detection

                imset = []
                for bb, lm in zip(bboxes, landmarks):
                   im = im.clone().boundingbox(bbox=bb)
                   rowdet = {'FILENAME': framefn, 'MEDIA_ID': self.basename,
                             'FACE_X': bb.xmin, 'FACE_Y': bb.ymin,
                             'FACE_WIDTH': bb.width(), 'FACE_HEIGHT': bb.height()}
                   lmidx = SCHEMA.index('LeftBrowLeftCorner_X')
                   rowlm = {k:v for k, v in zip(SCHEMA[lmidx:], [v for l in lm for v in l])}
                   im.attributes = dict(rowlm.items() + rowdet.items())
                imset.append(im)
                # Generate a value
                yield imset


    def trackdetections(self):
        self.tracker = SimpleTracker(self.detectvideo)
        for tid, vid in enumerate(self.tracker):
            vid.attributes = {'TRACK_ID': str(tid), 'MEDIA_ID': self.basename}
            for im in vid:
                im.attributes['TRACK_ID'] = str(tid)
            yield vid


    def calcmetrics(self):
        # Assumes re-calcing all video metrics from start is cheap
        for vid in self.trackdetections():
            self.videodetections.append(vid)

            frameset = {}
            for vid in self.videodetections:
                for im in vid:
                    fn = im.filename()
                    if fn not in frameset: frameset[fn] = []
                    frameset[fn].append(im)

            # Hold track level metrics
            self.track_metrics = {}
            track_visets = {vid[0].attributes['TRACK_ID']: vid for vid in self.videodetections}
            xweight = 1.0
            yweight = 1.0

            im_w = im_h = None
            # Walk through frames and generate track metrics
            for fn, imset in frameset.iteritems():
                N_framedets = len(imset)
                ts = float(filebase(fn)) / 1.e3 # milliseconds to seconds
                for im in imset:
                    if im_w is None: # only load images once if reading cached data
                        im_w = im.width()
                        im_h = im.height()
                    bb = im.boundingbox()
                    track_id = im.attributes['TRACK_ID']
                    if track_id not in self.track_metrics:
                        self.track_metrics[track_id] = dict(vid_secs=self.video_seconds, vidset=track_visets[track_id],
                                                       track_start=ts, track_end=ts,
                                                       num_dets=0, num_dets_weighted=0.0,
                                                       xdists=[], ymin_dists=[], ymax_dists=[], lls=[])
                    metrics = self.track_metrics[track_id]
                    # frames are not necessarily in order
                    metrics['track_start'] = min(ts, metrics['track_start'])
                    metrics['track_end'] = max(ts, metrics['track_end'])
                    metrics['num_dets'] += 1
                    metrics['num_dets_weighted'] += 1.0 / N_framedets
                    metrics['xdists'].append(abs(bb.x_centroid()/im_w - 0.5)) # normalized distance from centroid_x
                    metrics['ymin_dists'].append(abs(bb.ymin/im_h - 0.2)) # normalized distance from idea ymin==.2
                    metrics['ymax_dists'].append(abs(bb.ymax/im_h - 0.75)) # normalized distance from idea ymin==.2
                    metrics['lls'].append(mahalanobis([bb.x_centroid()/im_w, 0.5],
                                                      [bb.y_centroid()/im_h, 0.47],
                                                      np.linalg.inv(np.eye(2) * [xweight, yweight])))

            for track_id, metrics in self.track_metrics.iteritems():
                for k in ['xdists', 'ymin_dists', 'ymax_dists', 'lls']:
                    metrics[k[:-1]] = np.mean(metrics[k])
                    del metrics[k]
                metrics['track_id'] = str(track_id)
                metrics['wr'] = metrics['num_dets_weighted'] / float(metrics['num_dets'])
                metrics['extdets'] = float(metrics['num_dets']) * metrics['wr'] ** 3
                metrics['track_duration'] = metrics['track_end'] - metrics['track_start']
                track_start = int(floor(100. * metrics['track_start'] / self.video_seconds))
                track_end = int(ceil(100. * metrics['track_end'] / self.video_seconds))
                dur = np.zeros((10, 100, 3)).astype(np.uint8)
                dur[3:,track_start:track_end,1] = 196
                imdur = Image()
                imdur.data = dur
                metrics['imdur'] = imdur
                metrics['xstd'] = np.std([im.boundingbox().x_centroid() for im in track_visets[track_id]])
                metrics['ystd'] = np.std([im.boundingbox().y_centroid() for im in track_visets[track_id]])

            yield self.track_metrics


    def dometrics(self):
        metrics = {}
        track_lens = [len(vid) for vid in self.videodetections]

        urlfile = self.videofile[:-4] + '.url'
        if not os.path.isfile(urlfile):
            print "[janus.video.videopipeline] Can't find url file: [%s]" % urlfile
        else:
            with open(urlfile, 'r') as f:
                metrics['url'] = next(f).strip()

        metrics['num_tracks'] = len(self.videodetections)
        metrics['num_frames'] = self.num_frames
        metrics['fps'] = self.fps
        metrics['target_framerate'] = self.target_framerate
        metrics['video_seconds'] = self.video_seconds

        extdets = [self.track_metrics[t.attributes['TRACK_ID']]['extdets'] for t in self.videodetections if self._passes_metrics(self.track_metrics[t.attributes['TRACK_ID']])]
        metrics['max_extdets'] = np.max(extdets) if len(extdets) > 0 else 0.0

        if len(track_lens) > 0:
            max_track_length = np.max(track_lens)
            metrics['track_length_max'] = max_track_length
            metrics['track_length_mean'] = np.mean(track_lens)
            metrics['track_length_std'] = np.std(track_lens)
            metrics['coverage'] = float(sum(track_lens)) / float(self.num_frames) if self.num_frames > 0 else 0

        print '[videopipeline.metrics]: Writing %s' % self.metricsfile
        with open(self.metricsfile, 'w') as mf:
            mf.write('%s: %r\n' % ('filename: ', self.videofile))
            for k, v in metrics.iteritems():
                try:
                    print '[videopipeline.metrics]: %s: %.2f' % (k, v)
                    mf.write('%s: %.2f\n' % (k, v))
                except TypeError:
                    try:
                        print '[videopipeline.metrics]: %s: %s' % (k, v)
                        mf.write('%s: %s\n' % (k, v))
                    except:
                        print '[videopipeline.metrics]: Error writing video metrics: {%r: %r}' % (k, v)
            track_metrics = sorted([(int(tid), m) for tid, m in self.track_metrics.iteritems()], key=lambda x: x[0])
            for tid, tm in track_metrics:
                for k, v in tm.iteritems():
                    try:
                        print '[videopipeline.metrics]: %d.%s: %.2f' % (tid, k, v)
                        mf.write('%d.%s: %.2f\n' % (tid, k, v))
                    except TypeError:
                        # Skip non-float values
                        pass
                pass
            mf.flush()
        self.video_metrics = metrics
        return self

    def writetrackdetections(self):
        SCHEMA = TRACK_SCHEMA

        # imdets = [im for t in self.videodetections if self._passes_metrics(self.track_metrics[t.attributes['TRACK_ID']]) for im in t]
        imdets = [im for t in self.videodetections for im in t]

        # Write file sorted primarily by time, then by track number
        imdets = sorted(imdets, key=lambda im: (filebase(im.filename()), int(im.attributes['TRACK_ID'])))

        if imdets and self.write_images:
            # print 'debug path: %s' %(filepath(imdets[0].filename()))
            remkdir(filepath(imdets[0].filename()))

        with open(self.trackscsvfile, 'w') as f:
            writer = DictWriter(f, fieldnames=SCHEMA)
            writer.writeheader()

            for im in imdets:
                if self.write_images and not os.path.isfile(im.filename()):
                    im.saveas(im.filename())
                fn = relimfile(im)
                im = im.clone().setattribute('FILENAME', fn)
                writer.writerow(im.attributes)
            f.flush()
        print '[janus.video.videopipeline.writetrackdetections]: Done writing %s' % self.trackscsvfile
        return self

    def writesubsample(self):
        if self.subsampler is None:
            return self
        good_tracks = [t for t in self.videodetections if self._passes_metrics(self.track_metrics[t.attributes['TRACK_ID']])]
        if not good_tracks:
            return self
        good_tracks = sorted(good_tracks, reverse=True, key=lambda t: self.track_metrics[t.attributes['TRACK_ID']]['extdets'])
        best_track = good_tracks[0]
        best_vid = [v for v in self.videodetections if v.attributes['TRACK_ID'] == best_track.attributes['TRACK_ID']]
        vid = best_vid[0]

        # Landmarks
        f = Frontalizer()
        # Normalization
        imset = [im.clone() for im in vid]
        imset = [im.crop(bbox=im.boundingbox().dilate(1.1)).resize(224, 224) for im in imset]
        lms = [np.array(f._estimate_dlib_landmarks(im)).astype(np.float32).flatten().tolist() for im in imset]

        # Sample
        k = self.subsampler.clusterassign(lms)
        sampled_vid = np.array(vid)[k].tolist() # sample from original video
        quietprint('[janus.video.VideoPipeline.writesubsample]: Selected [%d/%d] subsamples for %s' % (len(sampled_vid), len(vid), self.basename))

        # Images for montage
        imset = [im.clone().crop(bbox=im.boundingbox().dilate(1.1)) for im in sampled_vid]

        im = Image() # new image to hold montage
        im.data = montage(imset, 50, 50, grayscale=False, do_flush=True)

        channel_id = '_'.join(self.basename.split('_')[1:-1]) # handle channels with underscores
        channel_dir = os.path.join(self.outdir, channel_id)
        remkdir(channel_dir)
        imgfile = os.path.join(channel_dir, '%s.jpg' % self.basename)
        print '[janus.video.VideoPipeline]: Saving montage: %s' % imgfile
        im.saveas(imgfile)

        # Write images and track detections
        remkdir(filepath(sampled_vid[0].filename()))

        with open(self.trackscsvfile, 'w') as f:
            SCHEMA = TRACK_SCHEMA
            writer = DictWriter(f, fieldnames=SCHEMA)
            writer.writeheader()

            for im in sampled_vid:
                im.saveas(im.filename())
                fn = relimfile(im)
                im = im.clone().setattribute('FILENAME', fn)
                writer.writerow(im.attributes)
            f.flush()
        print '[janus.video.videopipeline.writesubsample]: Done writing %s' % self.trackscsvfile
        return self

    def writemontage(self):
        if not self.write_montage:
            return self
        good_tracks = [t for t in self.videodetections if self._passes_metrics(self.track_metrics[t.attributes['TRACK_ID']])]
        if not good_tracks:
            return self
        good_tracks = sorted(good_tracks, reverse=True, key=lambda t: self.track_metrics[t.attributes['TRACK_ID']]['extdets'])
        best_track = good_tracks[0]
        best_vid = [v for v in self.videodetections if v.attributes['TRACK_ID'] == best_track.attributes['TRACK_ID']]
        vid = best_vid[0]

        # get a random sample of long tracks, or all samples for short tracks
        num_images = 144
        randset = np.random.choice(vid, min(num_images, len(vid)), replace=False).tolist()
        randset = sorted(randset, key=lambda im: im.filename()) # re-sort in time order
        imset = [im.crop() for im in randset]
        im = Image() # new image to hold montage
        im.data = montage(imset, 50, 50, grayscale=False, do_flush=True)

        channel_id = '_'.join(self.basename.split('_')[1:-1]) # handle channels with underscores
        channel_dir = os.path.join(self.outdir, channel_id)
        remkdir(channel_dir)
        imgfile = os.path.join(channel_dir, '%s.jpg' % self.basename)
        print '[janus.video.VideoPipeline]: Saving montage: %s' % imgfile
        im.saveas(imgfile)

class VideoPipelineDownload(VideoPipeline):
    def __init__(self, outdir, url, videofile, ext='.jpg', target_framerate=5, max_video_seconds=300, duration_threshold=15, write_images=True, write_montage=False, subsampler=None, save_video_files=False):
        super(VideoPipelineDownload, self).__init__(outdir=outdir, videofile=videofile, ext=ext, target_framerate=target_framerate, max_video_seconds=max_video_seconds, duration_threshold=duration_threshold, write_images=write_images, write_montage=write_montage, subsampler=subsampler)
        self.url = url
        self.save_video_files = save_video_files

    def download(self):
        vidlist = [self.url]
        quietprint('[janus.video.VideoPipelineDownload]: Downloading %s...' % self.basename)
        videosearch_download(vidlist, self.videofile)
        quietprint('[janus.video.VideoPipelineDownload]: Download complete for %s' % self.basename)
        return self

    def process(self):
        try:
            super(VideoPipelineDownload, self).process()
        finally:
            if os.path.isfile(self.videofile) and not self.save_video_files:
                quietprint('[janus.video.VideoPipelineDownload]: Removing %s...' % self.videofile)
                os.remove(self.videofile)


class UserVideo(object):
    def __init__(self, user_id, dl_dir, dets_dir, subsampler=None, save_video_files=False):
        self.user_id = user_id
        self.dl_dir = dl_dir
        self.dets_dir = dets_dir
        self.videos = []
        self.video_urls = []
        self.video_files = []
        self.sum_ext_dets = 0.0
        self.subsampler = subsampler
        self.save_video_files = save_video_files

    def process(self, do_filter=True, **kwargs):
        self.videos = [VideoPipeline(outdir=self.dets_dir, videofile=vf, subsampler=self.subsampler, **kwargs).process() for vf in self.video_files]
        if not self.save_video_files:
            for fn in self.video_files:
                if os.path.isfile(fn):
                    quietprint('[janus.video.UserVideo]: Removing %s...' % fn)
                    os.remove(fn)
        if do_filter:
            self.videos = [v for v in self.videos if v.filter_no_first_good()]
        self.sum_ext_dets = np.sum([float(v.video_metrics['max_extdets']) for v in self.videos])
        return self

    def filter(self, ext_dets_threshold, keep_video_count=None):
        passes = True
        if self.sum_ext_dets >= ext_dets_threshold:
            if keep_video_count is not None:
                found = 0
                max_dets = [md for k, md in enumerate(sorted([v.video_metrics['max_extdets'] for v in self.videos], reverse=True)) if k < keep_video_count]
                to_del = []
                for k, v in enumerate(self.videos):
                    if found < keep_video_count and v.video_metrics['max_extdets'] in max_dets:
                        found += 1
                    else:
                        v.remove()
                        to_del.append(k)
                for k in reversed(to_del):
                    del self.videos[k]
        else:
            print 'Removing bad channel: %s: sum_extdets: [%.1f] num_vids: [%d]' % (self.user_id, self.sum_ext_dets, len(self.video_files))
            for v in self.videos:
                v.remove()
            passes = False
        return passes

    #def subsample(self, write_detections=True):
    #    if self.subsampler is None:
    #        return self

    #    # Retrieve landmarks from image attributes
    #    imset = [im for v in self.videos for videt in v.videodetections for im in videt]
    #    lm = [landmarks(im) for im in imset]

    #    k = self.subsampler.clusterassign(lm) # indexes of 1024 images in trainlist assigned to each cluster
    #    sampled_imset = np.array(imset)[k].tolist()
    #    quietprint('[janus.video.UserVideo.subsample]: Selected [%d/%d] subsamples' % (len(sampled_imset), len(imset)))

    #    if write_detections:
    #        SCHEMA = TRACK_SCHEMA
    #        csvfile = os.path.join(self.dets_dir, self.user_id + '.csv')
    #        user_dir = os.path.join(self.dets_dir, self.user_id)
    #        remkdir(user_dir)

    #        # Write file sorted primarily by media_id, time, then by track number
    #        sorted_imset = sorted(sampled_imset, key=lambda im: (im.attributes['MEDIA_ID'], filebase(im.filename()), int(im.attributes['TRACK_ID'])))

    #        with open(csvfile, 'w') as f:
    #            writer = DictWriter(f, fieldnames=SCHEMA)
    #            writer.writeheader()

    #            for im in sorted_imset:
    #                # dets_dir/user_id/media_id_timestamp.jpg
    #                old_fn = im.filename()
    #                ts = filebase(old_fn)
    #                im.filename(os.path.join(user_dir, '%s_%s.jpg' % (im.attributes['MEDIA_ID'], ts)))
    #                im.saveas(im.filename())

    #                # Use relative path in csv file
    #                fn = relimfile(im)
    #                im = im.clone().setattribute('FILENAME', fn)
    #                writer.writerow(im.attributes)
    #            f.flush()
    #        print '[janus.video.uservideo.subsample]: Done writing %s' % csvfile
    #    return self



class YouTubeUserVideo(UserVideo):
    def __init__(self, user_id, dl_dir, dets_dir, expected_vid_list=None, subsampler=None):
        super(YouTubeUserVideo, self).__init__(user_id=user_id, dl_dir=dl_dir, dets_dir=dets_dir, subsampler=subsampler)
        self.expected_vid_list = expected_vid_list

    def check_user_correct(self, max_videos, channel=True):
        if not self.expected_vid_list:
            return False
        if not isactiveyoutuber(self.user_id):
            print '[janus.video.UserVideo] Skipping inactive user_id[%s]' % self.user_id
            return False
        else:
            print '[janus.video.UserVideo] Found active user_id[%s]' % self.user_id
            self.video_urls = youtube(self.user_id, outdir=self.dl_dir, channel=channel, video_limit=max_videos, expected_vid_list=self.expected_vid_list)
            if len(self.video_urls) > 0:
                return True
        return False

    def download(self, max_videos, channel=True):
        if isactiveyoutuber(self.user_id):
            print '[janus.video.UserVideo] Found active user_id[%s]' % self.user_id
            self.video_urls, self.video_files = youtube(self.user_id, outdir=self.dl_dir, channel=channel, video_limit=max_videos)
            print '[janus.video.UserVideo] Found %d videos for  user_id [%s]' % (len(self.video_files), self.user_id)
        else:
            print '[janus.video.UserVideo] Skipping inactive user_id[%s]' % self.user_id
        return self
