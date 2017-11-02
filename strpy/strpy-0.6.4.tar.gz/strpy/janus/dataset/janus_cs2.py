import os
import csv
from glob import glob
from bobo.cache import Cache
from bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile
from bobo.viset.stream import ImageStream
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate
import bobo.app

VISET = 'Janus_CS2'

cache = Cache()

def splitfile(dataset='train', split=None):    
    visetdir = os.path.join(cache.root(), VISET, 'CS2')
    if split is None:
        csvfile = os.path.join(visetdir, 'protocol', '%s.csv' % (dataset))
    if dataset == 'gallery':
        csvfile = os.path.join(visetdir, 'protocol', 'split%d' % int(split), 'gallery_%d.csv' % (int(split)))
    elif dataset == 'probe':
        csvfile = os.path.join(visetdir, 'protocol', 'split%d' % int(split), 'probe_%d.csv' % (int(split)))            
    elif dataset == 'train':
        csvfile = os.path.join(visetdir, 'protocol', 'split%d' % int(split), 'train_%d.csv' % (int(split)))        
    return csvfile


def subject_id():
    subjectdict = {}
    subjectlist = os.listdir(os.path.join(cache.root(), VISET, 'CS2', 'subjects'))
    for subject in subjectlist:
        try:
            csvfile = os.path.join(os.path.join(cache.root(), VISET, 'CS2', 'subjects'), subject, 'gallery.csv')
            with open(csvfile, 'rb') as f:
                x = f.readline().split(',')  # header
                x = f.readline().split(',')
                subjectdict[int(x[1])] = subject
        except:
            # ignore invalid directories
            print '[janus_cs2.subject_id]: invalid gallery.csv for subject "%s"' % subject
            continue

    #print '[janus_cs2.subject_id]: adding four unknown subject ids FIXME ' % subject
    #subjectdict[1320] = 'UNKNOWN1'
    #subjectdict[3584] = 'UNKNOWN2'
    #subjectdict[79] = 'UNKNOWN3'
    #subjectdict[145] = 'UNKNOWN4'
    
    return subjectdict
        
def rdd(sparkContext=None, dataset='train', split=1):
    """Create a resilient distributed dataset from a split file"""
    sparkContext = bobo.app.init('janus_cs2') if sparkContext is None else sparkContext            
    schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
    visetdir = os.path.join(cache.root(), VISET, 'CS2')
    csvfile = splitfile(dataset, split)
    subjects = subject_id()

    # Parse CSV file based on protocol, all non-detection properties go in attributes dictionary
    return (sparkContext.textFile(csvfile)
            .map(lambda row: row.encode('utf-8').split(','))  # CSV to list of row elements
            .filter(lambda x: x[0] != 'TEMPLATE_ID')  # hack to ignore first row
            .map(lambda x: ImageDetection(url=cache.key(os.path.join(visetdir, x[2])), category=subjects[int(x[1])],
                                          xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                          ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),                                          
                                          xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                          ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                          attributes={k:v for (k,v) in zip(schema,x)}))  # Parse row into
            .keyBy(lambda im: str(im.attributes['MEDIA_ID'])+str(im.category()))  # Construct (TemplateID, x) tuples
            .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct (TemplateID, [x1,x2,...,xk]) tuples for videos
            .map(lambda (k,fr): VideoDetection(frames=fr, attributes=fr[0].attributes) if islist(fr) else fr)) # VideoDetections for multiple frames, otherwise Image Detections


def rdd_as_templates(sparkContext=None, dataset='train', split=1):
    """Create a resilient distributed dataset from a split file"""
    sparkContext = bobo.app.init('janus_cs2') if sparkContext is None else sparkContext                
    schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
    visetdir = os.path.join(cache.root(), VISET, 'CS2')
    csvfile = splitfile(dataset, split)
    subjects = subject_id()

    # Parse CSV file based on protocol, all non-detection properties go in attributes dictionary
    return (sparkContext.textFile(csvfile)
            .map(lambda row: row.encode('utf-8').split(','))  # CSV to list of row elements
            .filter(lambda x: x[0] != 'TEMPLATE_ID')  # hack to ignore first row
            .map(lambda x: ImageDetection(url=cache.key(os.path.join(visetdir, x[2])), category=subjects[int(x[1])],
                                          xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                          ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),                                          
                                          xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                          ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                          attributes={k:v for (k,v) in zip(schema,x)}))  # Parse row into
            .keyBy(lambda im: str(im.attributes['TEMPLATE_ID']))  # Construct (TemplateID, x) tuples
            .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct (TemplateID, [x1,x2,...,xk]) tuples for frames/images
            .map(lambda (k,frames): GalleryTemplate(media=tolist(frames), mediakeys=[fr.attributes['MEDIA_ID']+'_'+fr.category() for fr in tolist(frames)]))) # Janus template as dictionary of media

                        
def rdd_templates_as_video(sparkContext=None, dataset='train', split=1):
    """Create a resilient distributed dataset from a split file"""
    sparkContext = bobo.app.init('janus_cs0') if sparkContext is None else sparkContext                    
    schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
    visetdir = os.path.join(cache.root(), VISET, 'CS2')
    csvfile = splitfile(dataset, split)
    subjects = subject_id()

    # Parse CSV file based on protocol, all non-detection properties go in attributes dictionary
    return (sparkContext.textFile(csvfile)
            .map(lambda row: row.encode('utf-8').split(','))  # CSV to list of row elements
            .filter(lambda x: x[0] != 'TEMPLATE_ID')  # hack to ignore first row
            .map(lambda x: ImageDetection(url=cache.key(os.path.join(visetdir, x[2])), category=subjects[int(x[1])],
                                          xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                          ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),                                          
                                          xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                          ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                          attributes={k:v for (k,v) in zip(schema,x)}))  # Parse row into
            .keyBy(lambda im: str(im.attributes['TEMPLATE_ID']))  # Construct (TemplateID, x) tuples
            .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct (TemplateID, [x1,x2,...,xk]) tuples for videos
            .map(lambda (k,fr): VideoDetection(frames=tolist(fr), attributes=tolist(fr)[0].attributes))) 

            
def splits(sparkContext, split=None, rdd=rdd):
    split = range(1,11) if split is None else split
    return [ [rdd(sparkContext, dataset=d, split=s) for d in ['train', 'gallery', 'probe']] for s in tolist(split) ]
            
            
def stream(dataset='train', split=None):
    csvfile = splitfile(dataset, split)
    visetdir = os.path.join(cache.root(), VISET, 'CS2')
    subjects = subject_id()
    def parser(row):
        x = row.encode('utf-8').split(',') if not islist(row) else row  # CSV to list
        schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
        return (ImageDetection(url=cache.key(os.path.join(visetdir, x[2])), category=subjects[int(x[1])],
                                xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),                                          
                                xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                   attributes={k:v for (k,v) in zip(schema,x)}))
        
    return ImageStream(csvfile, parser=parser, delimiter=',', rowstart=2)


def export():
    # Dataset downloaded?
    if not os.path.isdir(os.path.join(cache.root(), VISET)):
        raise ValueError('Download Janus CS2 dataset manually to "%s" ' % os.path.join(cache.root(), VISET, 'CS2'))



    
