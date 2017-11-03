#!/usr/bin/env python
# encoding: utf-8
"""
XML__tests.py

Created by Hywel Thomas on 2011-02-24.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import unittest

from itt_general.utilities import StringReader
from itt_general.utilities import xml

element = xml.XMLElement("""<PhysicalAsset assetName="CAS-CASBNU">
                                <!-- assetName = concatenation of <TypeofElement> and <FormatofElement> above -->
                                <!-- From spec: "List of tape storage formats : BetaSp; DigiBeta; MiniDV; etc."  -->
                                <MediaReferenceName>BL77318</MediaReferenceName>
                                <Appendix>1</Appendix>
                                <Appendix>2</Appendix>
                                <Appendix>3</Appendix>
                                <Appendix>4</Appendix>
                            </PhysicalAsset>""")

element.find(path = [u'PhysicalAsset assetName="CAS-CASBNU"',u'MediaReferenceName'])
element.find(path = [u'PhysicalAsset assetName="CAS-CASBNU"',u'MediaReferenceName']).value
element.find(path = [u'PhysicalAsset assetName="TAPE"',u'MediaReferenceName']) == None

element.find(path = [u'PhysicalAsset',u'Appendix'], whereValue = '2')

element.find(path = [u'PhysicalAsset',u'Appendix'])[2].value


element.remove(path=[u'PhysicalAsset assetName="CAS-CASBNU"',u'Appendix'], value="2")

print element

element.remove(path=[u'PhysicalAsset assetName="CAS-CASBNU"',u'Appendix'])

print element


element.add("""<Appendices/>""")
print element
                            
element.addAtPath(path  = [u'PhysicalAsset',u'Appendices'],
                  bytes = """<title>Appendix 1</title>""")

print element

element.replace(bytes = """<index>
                               <page>1</page>
                               <value>How to use XMLElement</value>
                            </index>""",
                path  = [u'PhysicalAsset',u'Appendices'])
print element

element.replaceValueAtPath(path     = [u'PhysicalAsset',u'index',u'value'],
                           newValue = "Confessions of a Python Developer")
                           
print element 

{'Element'   : """Describes the path to the node of the XML tree
                   e.g. <MediaRequest><VersionNumber>
                   Attributes may also be added, which can help
                   narrow the search when there are many elements
                   of the same type at the same level.
                   e.g. <MediaRequest><AudioTrack trackNumber="1">""",
                 
 'Value'     : """Only nodes with this value will be matched.
                  This is useful for checking that a value
                  is present.""",
                 
 'Attribute' : """If a particular attribute of an element is
                  what we're interested in rather than the
                  whole element, then the named attribute
                  value is returned."""}
                 
element = xml.XMLElement("""<MediaRequest OriginatingSystem="OSCAR">
                                <VersionNumber>12345</VersionNumber>
                                <AudioTrack TrackNumber="1">
                                    <Level>-23</Level>
                                </AudioTrack>
                                <AudioTrack TrackNumber="2">
                                    <Level>-23</Level>
                                </AudioTrack>
                            </MediaRequest>""")

     
print element.search({'Element':'<MediaRequest><AudioTrack TrackNumber="1">'})


print element.search({'Element':'<MediaRequest><VersionNumber>',
                       'Value'  :'12345'})

print element.search({'Element':'<MediaRequest>',
                      'Attribute':'OriginatingSystem'})


print element.exists({'Element':'<MediaRequest><VersionNumber>'})

print element.exists({'Element':'<MediaRequest><SomethingMadeUp>'})



import pprint

xml = xml.XML("""<?xml version = "1.0" encoding = "UTF-8"?>
                 <MediaRequest OriginatingSystem="OSCAR" attribute2="OSCAR">
                     <VersionNumber>12345</VersionNumber>
                     <AudioTrack TrackNumber="1">
                         <Level someattr="x">-1</Level>
                     </AudioTrack>
                     <AudioTrack TrackNumber="2">
                         <Level>-2</Level>
                     </AudioTrack>
                     <AudioTrack TrackNumber="3">
                         <Level>-3</Level>
                     </AudioTrack>
                 </MediaRequest>""")

pprint.pprint(xml.dictionary())

media_request = xml.find({'Element':'<MediaRequest>'})
pprint.pprint(media_request.dictionary())

audio_track_1_element = xml.find({'Element':'<MediaRequest><AudioTrack TrackNumber="1">'})
pprint.pprint(audio_track_1_element.dictionary())
pprint.pprint(audio_track_1_element.dictionary(include_first_tag=True))


class TestNormalisePath(unittest.TestCase):

    def test_with_gt_and_lt(self):
        self.assertTrue(xml.normalisePath("<a><b>") == ['a', 'b'])

    def test_with_forward_slash(self):
        self.assertTrue(xml.normalisePath("a/b") == ['a', 'b'])

    def test_with_already_normalised(self):
        self.assertTrue(xml.normalisePath(['a', 'b']) == ['a', 'b'])






schedule_elements = u"""<!-- pre A -->
                        <A> <!-- part of A -->
      				    </A>
      				    <!-- post A -->"""

schedule_elements = xml.XMLElement(StringReader.StringReader(schedule_elements))

print schedule_elements












#import sys
#sys.path.append('../XENALib')
#import UTF8
#print "x"
#print XML(UTF8.UTF8File('/Users/bob/Dropbox/Coding/Python/XENA/Fake_XENA_Mount/Sony_Test_Media/XENA/Templates/DEFAULT.XML').read())


somexml="""<?xml version = "1.0" encoding = "UTF-8"?>
<tns:MediaRequest xmlns:tns = "http://rsi.com/mediarequest" xmlns:blah = "http://blah.com" xmlns:flob="http://flob.com">
	<tns:MediaId>MediaId</tns:MediaId>
	<tns:AutoQualityControl>
		<tns:DoQualityControl>False</tns:DoQualityControl>
	</tns:AutoQualityControl>
	<tns:MediaMetadata>
		<tns:ProductId>ProductId</tns:ProductId>
		<cdata_test><![CDATA[<the><content><of><the><cdata>]]></cdata_test>
	</tns:MediaMetadata>
</tns:MediaRequest>
"""
print "----"
replace_test = xml.XML(somexml)
print replace_test
replace_test.replace(path = "<tns:MediaRequest><tns:MediaMetadata>",
                     partialXML="""<a>
                                      <b1>b1 value</b1>
                                      <b1>b1 value</b1>
                                   </a>""")    
print replace_test


somexml="""<?xml version="1.0" encoding="UTF-8"?>
            <tns:MediaRequest xmlns:tns="http://rsi.com/mediarequest">
            	<tns:MediaId>MediaId</tns:MediaId>
            	<tns:VersionId>VersionId</tns:VersionId>
            	<tns:VersionName>VersionName</tns:VersionName>
            	<tns:MediaType>FILE</tns:MediaType>
            	<tns:MediaFileName/>
            	<tns:SourceName>POST_PRODUCTION</tns:SourceName>
            	<tns:DestinationName>IS</tns:DestinationName>
            	<tns:Expiration>2011-12-31T12:00:00</tns:Expiration>
            	<tns:JobId>5247896</tns:JobId>
            	<tns:JobResult>COMPLETED</tns:JobResult>
            	<tns:TranscodeAsset>
            		<tns:DoTranscode>false</tns:DoTranscode>
            		<!--<tns:TranscodeFarm>MBC</tns:TranscodeFarm>
            		<tns:TargetWrapper>MXF</tns:TargetWrapper>
            		<tns:TargetFormat>XDCAM</tns:TargetFormat>
            		<tns:TargetResolution>1080i</tns:TargetResolution>
            		<tns:TargetFrameRate>25</tns:TargetFrameRate>-->
            	</tns:TranscodeAsset>
            	<tns:AutoQualityControl>
            		<tns:DoQualityControl>False</tns:DoQualityControl>
            	</tns:AutoQualityControl>
            	<tns:MediaMetadata>
            		<tns:ProductId>ProductId</tns:ProductId>
            		<tns:ProductTitle>ProductTitle</tns:ProductTitle>
            		<tns:Wrapper>MXF</tns:Wrapper>
            		<!--<tns:OperationalPattern>Op1a</tns:OperationalPattern>--><!--2nd comment-->
            		<tns:VideoType>HD</tns:VideoType>
            		<!--<tns:Format>XDCAM</tns:Format>-->
            		<tns:Format>XDCAMHD422</tns:Format>
            		<tns:BitRate>50</tns:BitRate>
            		<!--<tns:Resolution>1080i</tns:Resolution>-->
            		<tns:Resolution>1080I25</tns:Resolution>
            		<!--<tns:FrameRate>25</tns:FrameRate>-->
            		<tns:AspectRatio>16:9</tns:AspectRatio>
            		<tns:NativeAspectRatio>1.33</tns:NativeAspectRatio>
            		<tns:SampleRate>48</tns:SampleRate>
            		<tns:BitDepth>24</tns:BitDepth>
            		<tns:TimeCodeIn>TimeCodeIn</tns:TimeCodeIn>
            		<tns:TimeCodeOut>TimeCodeOut</tns:TimeCodeOut>
            		<tns:SOM>SOM</tns:SOM>
            		<tns:EOM>EOM</tns:EOM>
            		<!--<tns:TypeOfContent>Complete</tns:TypeOfContent>-->
            		<tns:AudioTrackList>
            			<tns:AudioTrack>
            				<tns:TrackNumber>1</tns:TrackNumber>
            				<tns:AudioType>STEREO</tns:AudioType>
            				<tns:ContentDescription>COMPLETE</tns:ContentDescription>
            				<tns:AudioMapping>L</tns:AudioMapping>
            				<tns:Language>ita</tns:Language>
            				<tns:MeasuredLevel>  </tns:MeasuredLevel>
            				<!--<tns:MeasuredLevel>0</tns:MeasuredLevel>-->
            				<!--<tns:LoudnessRange>0</tns:LoudnessRange>
            				<tns:MaxTruePeak>0</tns:MaxTruePeak>
            				<tns:BroadcastAs>VP</tns:BroadcastAs>-->
            			</tns:AudioTrack>
            		</tns:AudioTrackList>
            	</tns:MediaMetadata>
            </tns:MediaRequest>
            """
    
print xml.XML(somexml), '\n'

subset = xml.XML(somexml).subset(([{'Element': '<tns:MediaRequest><tns:MediaId>'},
                                   {'Element':'<tns:MediaRequest><tns:VersionId>'},
                                   {'Element':'<tns:MediaRequest><tns:MediaMetadata><tns:ProductId>'},
                                   {'Element':'<tns:MediaRequest>'}]))
print subset  
print 'value:',subset['Element:<tns:MediaRequest><tns:MediaId>'].value
print 'value:',subset['Element:<tns:MediaRequest><tns:VersionId>'].value
print 'value:',subset['Element:<tns:MediaRequest><tns:MediaMetadata><tns:ProductId>'].value
print 'value:',subset['Element:<tns:MediaRequest>'].attributes['xmlns:tns']
print 'feck'
assert subset['Element:<tns:MediaRequest><tns:MediaId>'].value=='MediaId'
assert subset['Element:<tns:MediaRequest><tns:VersionId>'].value=='VersionId'
assert subset['Element:<tns:MediaRequest><tns:MediaMetadata><tns:ProductId>'].value=='ProductId'
assert subset['Element:<tns:MediaRequest>'].attributes['xmlns:tns']=='http://rsi.com/mediarequest'

    
somexml="""<?xml encoding="utf-8" version="1.0" ?>
<somexml>
        
	        1234 5678
        
        
        
</somexml>"""
print xml.XML(somexml), '\n'

somexml="""<?xml encoding="utf-8" version="1.0" ?>
<tns:MediaRequest> </tns:MediaRequest>"""
print  xml.XML(somexml), '\n'

somexml="""<?xml encoding="utf-8" version="1.0" ?>
<outer>
   <nested>n1</nested>
</outer>"""
print  xml.XML(somexml), '\n'

somexml="""<?xml encoding="utf-8" version="1.0" ?>
<!-- comment -->
<withComment>
   <nested>n1</nested>
</withComment>"""
print  xml.XML(somexml), '\n'


somexml="""<?xml encoding="utf-8" version="1.0" ?>
<!-- comment -->
<withComments>
   <nested>n1</nested><!-- another comment -->
</withComments>"""
print  xml.XML(somexml)


somexml="""<?xml encoding="utf-8" version="1.0" ?>
<outer>
   <nested>n1</nested>
   <empty/>
   <empty attr="some attribute"/>
</outer>"""
print  xml.XML(somexml)


somexml="""<?xml encoding="utf-8" version="1.0" ?>
            <tns:MediaRequest xsi:schemaLocation="http://rsi.ch/mediarequest MediaRequest.xsd" xmlns:tns="http://rsi.ch/mediarequest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            	<tns:MediaId>12345678</tns:MediaId>
            	<tns:VersionId>12345678</tns:VersionId>
            	<tns:VersionName/>
            	<tns:MediaFileName>12345678.mov</tns:MediaFileName>
            	<tns:SourceName>POST_PRODUCTION</tns:SourceName>
            	<tns:DestinationName dummy="x">DESTINATION1</tns:DestinationName>
            	<tns:DestinationName dummy="y">DESTINATION2</tns:DestinationName>
            	<tns:TranscodeAsset>
            		<tns:DoTranscode>false</tns:DoTranscode>
            		<tns:TranscodeFarm>DIPO</tns:TranscodeFarm>
            		<tns:TargetWrapper>MOV</tns:TargetWrapper>
            		<tns:TargetFormat>XDCAMHD422</tns:TargetFormat>
            		<tns:TargetResolution>1080I25</tns:TargetResolution>
            	</tns:TranscodeAsset>
            	<tns:AutoQualityControl>
            		<tns:DoQualityControl>false</tns:DoQualityControl>
            	</tns:AutoQualityControl>
            	<tns:MediaMetadata>
            		<tns:ProductId>12345678</tns:ProductId>
            		<tns:ProductTitle/>
            		<tns:Description>This is the description</tns:Description>
            		<tns:Wrapper>MXF</tns:Wrapper>
            		<tns:VideoType>HD</tns:VideoType>
            		<tns:Format>IMXD10</tns:Format>
            		<tns:Resolution>1080i25</tns:Resolution>
            		<tns:AspectRatio>16:9</tns:AspectRatio>
            		<tns:SampleRate>48</tns:SampleRate>
            		<tns:BitDepth>24</tns:BitDepth>
            		<tns:TimeCodeIn/>
            		<tns:TimeCodeOut/>
            		<tns:AudioTrackList>
            			<tns:AudioTrack>
            				<tns:TrackNumber>1</tns:TrackNumber>
            				<tns:AudioType>STEREO</tns:AudioType>
            				<tns:ContentDescription>Complete</tns:ContentDescription>
            				<tns:AudioMapping>STEREO_L</tns:AudioMapping>
            				<tns:Language>it-CH</tns:Language>
            				<tns:MeasuredLevel>-27</tns:MeasuredLevel>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>2</tns:TrackNumber>
            				<tns:AudioType>STEREO</tns:AudioType>
            				<tns:ContentDescription>Complete</tns:ContentDescription>
            				<tns:AudioMapping>STEREO_R</tns:AudioMapping>
            				<tns:Language>it-CH</tns:Language>
            				<tns:MeasuredLevel>-27</tns:MeasuredLevel>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>3</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>4</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>5</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>6</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>7</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>8</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>9</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>10</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>11</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>12</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>13</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>14</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>15</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            			<tns:AudioTrack>
            				<tns:TrackNumber>16</tns:TrackNumber>
            				<tns:AudioType/>
            				<tns:ContentDescription/>
            				<tns:AudioMapping/>
            				<tns:Language/>
            				<tns:MeasuredLevel/>
            			</tns:AudioTrack>
            		</tns:AudioTrackList>
            	</tns:MediaMetadata>
            </tns:MediaRequest>
            """        
importedXML = xml.XML(somexml)


tempsubset = importedXML.subset([{'Element':'<tns:MediaRequest><tns:DestinationName dummy="x">',
                                  'Attribute':'dummy'},
                                 {'Element':'<tns:MediaRequest><tns:DestinationName>',
                                  'Attribute':'dummy'},
                                 {'Element':'<tns:MediaRequest><tns:VersionId>',
                                  'Value':'12345678'}])
print 'tempsubset',tempsubset
print xml.XMLSubsetString(tempsubset)

importedXML.add("<addThis>data</addThis>")
importedXML.add("<addThis><nested/></addThis>")
morexml="""<VideoType>HD</VideoType>
           <Format>XDCAMHD422</Format>
           <Resolution>1080I25</Resolution>
           <AudioTrackList>
               <AudioTrack>
                   <TrackNumber>1</TrackNumber>
                   <AudioType>STEREO</AudioType>
                   <ContentDescription>COMPLETE</ContentDescription>
                   <AudioMapping>STEREO_L</AudioMapping>
                   <Language>ITA</Language>
                   <MeasuredLevel>-23</MeasuredLevel>
               </AudioTrack>
               <AudioTrack>
                   <TrackNumber>2</TrackNumber>
                   <AudioType>STEREO</AudioType>
                   <ContentDescription>COMPLETE</ContentDescription>
                   <AudioMapping>STEREO_R</AudioMapping>
                   <Language>ITA</Language>
                   <MeasuredLevel>-23</MeasuredLevel>
               </AudioTrack>
           </AudioTrackList>"""

importedXML.add(morexml)
importedXML.replaceValueAtPath(path       ='tns:MediaRequest/tns:DestinationName',
                               whereValue = 'DESTINATION1',
                               newValue   = 'REPLACE1',)
importedXML.replaceValueAtPath(path       ='<tns:MediaRequest><tns:DestinationName>',
                               whereValue = 'DESTINATION2',
                               newValue   = 'REPLACE2',)
print importedXML

importedXML.replaceValueAtPath(path       ='tns:MediaRequest/tns:DestinationName',
                               whereValue = 'REPLACE2',
                               newValue   = None,)
print importedXML

importedXML.find({'Element':'<tns:MediaRequest><tns:MediaMetadata><tns:Wrapper>'}).value='CHANG&ED!'
print '\n',importedXML.find({'Element':'<tns:MediaRequest><tns:MediaMetadata><tns:Wrapper>'})
print importedXML.find({'Element':'<tns:MediaRequest><tns:MediaMetadata><tns:Wrapper>',
                        'Value':'CHANG&ED!'})
#print importedXML.find({'Element':'<tns:MediaRequest><tns:MediaMetadata><tns:Wrapper>',
#                         'Value':'MXF'})
importedXML.remove('tns:MediaRequest/tns:MediaMetadata/tns:Wrapper','MXF')
print "xxx"
try:
    print importedXML.find({'Element':'<tns:MediaRequest><tns:MediaMetadata/tns:Wrapper>',
                            'Value':'CHANGED!'})
    assert False, "Expected XML.XMLElementNotFound to be raised. XML.remove has failed"
except xml.XMLElementNotFound:
    pass

print 'fff'
importedXML.remove(path='<tns:MediaRequest><tns:MediaMetadata/tns:Wrapper>',
                   value='CHANGED!')
print "yyy"
#print importedXML.find({'Element':'<tns:MediaRequest><tns:MediaMetadata><tns:Wrapper>',
#                        'Value':'CHANGED!'})
importedXML.addAtPath('<tns:MediaRequest><tns:MediaMetadata>',
                      '<Added>adding this!</Added>')
print importedXML


if __name__ == '__main__':
    unittest.main()