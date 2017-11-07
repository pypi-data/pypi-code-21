#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: VeriCold.TraceFile
   :synopsis: Read a trace file from VeriCold/EDAX microcalorimeter x-ray detector.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

TraceFile header
    long    m_dwHeaderSize; //(bytes)
    long    m_dwHeaderVersion;//long

    char    m_lpszDetectorNr[_MAX_PATH];//    format "4"
    char    m_lpszSQUIDNr[_MAX_PATH]; //    format "??"
    char    m_lpszElectronicNr[_MAX_PATH];//format "??"
    char    m_lpszPolarisNr[_MAX_PATH];// format "A1-0000-0-000"

    struct _timeb m_tbFileTime; //abs
    tm        m_tmLocalTime;
    long    m_dwClockTime;    //ms
    long    m_dwLiveTime; //ms
    long    m_dwDeadTime; //ms

    long    m_dwTraceLength;
    double    m_dblSampleRate;

    double    m_dblRegTemperature;
    double    m_dblIBias;
    double    m_dblAmpFactor; //(ADCKarte)
    //must put in VoltsPerBin here 10/4096

    double    m_dblAccVoltage;
    double    m_dblAperture;
    double    m_dblWDistance;
    double    m_dblPixelSize;

Trace header.
        long    m_dwSizeInBytes;//size of this struct - written to file
        //things that change from pulse to pulse
        long    m_dwNumber;         //count number - incremented even if no file open!
        long    m_dwType;         //is the pulse artificial?
        long    m_dwTrigBufPos;     //the trigger position in the DAQ buffer
        __int64 m_i64Time;            //a time stamp in ms since the start of gathering
        double    m_dblTemperature; //from res bridge

        double    m_dblPrePulseLevel; //baseline level before the trigger
        double    m_dblPostPulseLevel;//baseline level after the trigger
        long    m_dwMaxPosition;    //pos the max
        double    m_dblMax;         //value of the max
        long    m_dwMinPosition;    //position of the min
        double    m_dblMin;         //value of the min
        double    m_dblPulseHeight; //the calculated height of the pulse

        //static vars in a run
        double    m_dblSampleRate;    //sample rate
        long    m_dwLength;         //how many samples in the trace
        long    m_dwPreTrigger;     //pos in buff of trigger
        double    m_dblTriggerLevel;    //at what level is the trigger set

        long    m_dwBaseLineLength; //not used
        long    m_dwBaseLineStart;    //not used

    // need some post baseline stuff here
        //these are not yet written to the file
        double    m_dblPostBaseLineLevel;//baseline level after the pulse
        long    m_dwPostBaseLineStart;
        long    m_dwPostBaseLineLength;
        double    m_dblXPos;
        double    m_dblYPos;

Trace data
                //make an array of shorts!!!
                short* pi16Buf = new short[m_dwSize];
                for(int i=0; i<m_dwSize; ++i)
                    pi16Buf[i] = pdblBuf[i];
                gcTraceFile.SaveToFile( pi16Buf,
                                        m_dwSize*sizeof(short));
                delete [] pi16Buf;
"""


###############################################################################
# Copyright 2007 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import os
import time
import struct

# Third party modules.
import pylab

# Project modules.

# Globals and constants variables.

class TraceFile(object):
    def __init__(self, filename):
        self.headerSize = 1180

        self.headerFormat = "<2i 260s 260s 260s 260s iH2h2x 9i 4i 4x 8d"

        #print "headerFormat size: %i" % (struct.calcsize(self.headerFormat))

        self.traceHeaderSize = 148

        self.traceHeaderFormat = "4i ii 3d i d i 3d 2i d 2i d 2i 2d 4x"

        #print "traceHeaderFormat size: %i" % (struct.calcsize("<"+self.traceHeaderFormat))

        self.traceDataSize = 1024*2

        self.traceDataFormat = "1024h"

        #print "traceDataFormat size: %i" % (struct.calcsize("<"+self.traceDataFormat))

        self.traceFormat = "<" + self.traceHeaderFormat + self.traceDataFormat

        #print "traceFormat size: %i" % (struct.calcsize(self.traceFormat))

        self.traceSize = self.traceHeaderSize + self.traceDataSize

        #print "Trace size: %i" % (self.traceSize)

        self.filename = filename

        self.header = {}

    def getFileSize(self):
        return os.stat(self.filename).st_size

    def printFileTime(self):
        timeLastAccess = time.localtime(os.stat(self.filename).st_atime)

        timeLastAccess = time.asctime(timeLastAccess)

        timeLastModification = time.localtime(os.stat(self.filename).st_mtime)

        timeLastModification = time.asctime(timeLastModification)

        timeLastChange = time.localtime(os.stat(self.filename).st_ctime)

        timeLastChange = time.asctime(timeLastChange)

        print("Time of the last access: %s" % (timeLastAccess))

        print("Time of the last modification: %s" % (timeLastModification))

        print("Time of the last status change: %s" % (timeLastChange))

    def readTrace(self, traceID):
        if traceID > 0:
            traceFile = open(self.filename, "rb")

            filePosition = self.headerSize + (traceID - 1)*self.traceSize

            #print traceID, filePosition

            traceFile.seek(filePosition)

            traceStr = traceFile.read(self.traceSize)

            values = struct.unpack(self.traceFormat, traceStr)

            #print len(values)

            #for index,value in enumerate(values):
            #    print "%2i: >>%s<<" % (index, value)

            header = {}

            # Trace header.
            header["SizeInBytes"] = int(values[0])

            # Things that change from pulse to pulse.
            header["TraceID"] = int(values[1])
            header["Type"] = int(values[2])
            header["TrigBufPos"] = int(values[3])
            header["Time"] = int(str(values[4])+str(values[5]))
            header["Temperature"] = float(values[6])

            header["PrePulseLevel"] = float(values[7])
            header["PostPulseLevel"] = float(values[8])
            header["MaxPosition"] = int(values[9])
            header["Max"] = float(values[10])
            header["MinPosition"] = int(values[11])
            header["Min"] = float(values[12])
            header["PulseHeight"] = float(values[13])

            # Static vars in a run.
            header["SampleRate"] = float(values[14])
            header["Length"] = int(values[15])
            header["PreTrigger"] = int(values[16])
            header["TriggerLevel"] = float(values[17])

            # Not used.
            header["BaseLineLength"] = int(values[18])
            header["BaseLineStart"] = int(values[19])

            # Need some post baseline stuff here.
            # These are not yet written to the file
            header["PostBaseLineLevel"] = float(values[20])
            header["PostBaseLineStart"] = int(values[21])
            header["PostBaseLineLength"] = int(values[22])
            header["XPos"] = float(values[23])
            header["YPos"] = float(values[24])

            data = []

            for index in range(25, 1025, 1):
                data.append(float(values[index]))

            headerKeys = header.keys()
            headerKeys.sort()

#            for key in headerKeys:
#                print "%s: >>%s<<" % (key, header[key])


            timeStep_ms = 1.0E3/header["SampleRate"]

            times_ms = []
            for index, dummy_value in enumerate(data):
                time_ms = timeStep_ms*index

                times_ms.append(time_ms)

                #print "%0.4f\t%0.4f" % (time_ms, value)

            return header, times_ms, data

    def readHeader(self):
        traceFile = open(self.filename, "rb")

        headerStr = traceFile.read(self.headerSize)

        values = struct.unpack(self.headerFormat, headerStr)

        #print len(values)

#        for index,value in enumerate(values):
#            print "%2i: >>%s<<" % (index, value)

        self.header["Size"] = int(values[0])

        self.header["Version"] = int(values[1])

        self.header["DetectorNumber"] = values[2]

        self.header["SQUIDNumber"] = values[3]

        self.header["ElectronicNumber"] = values[4]

        self.header["PolarisNumber"] = values[5]

        self.header["CurrentSystemTime_64"] = str(values[6]) + str(values[7])

        self.header["CurrentSystemTime_milli"] = int(values[7])

        self.header["CurrentSystemTime_timezone"] = int(values[8])

        self.header["CurrentSystemTime_dstflag"] = int(values[9])

        self.header["Localtime_sec"] = int(values[10])
        self.header["Localtime_min"] = int(values[11])
        self.header["Localtime_hour"] = int(values[12])
        self.header["Localtime_mday"] = int(values[13])
        self.header["Localtime_mon"] = int(values[14])
        self.header["Localtime_year"] = int(values[15])
        self.header["Localtime_wday"] = int(values[16])
        self.header["Localtime_yday"] = int(values[17])
        self.header["Localtime_isdst"] = int(values[18])

        self.header["ClockTime_ms"] = int(values[19])
        self.header["LiveTime_ms"] = int(values[20])
        self.header["DeadTime_ms"] = int(values[21])

        self.header["TraceLength"] = int(values[22])
        self.header["SampleRate"] = float(values[23])

        self.header["RegTemperature"] = float(values[24])
        self.header["IBias"] = float(values[25])
        self.header["AmpFactor"] = float(values[26])

        self.header["AccVoltage"] = float(values[27])
        self.header["Aperture"] = float(values[28])
        self.header["WDistance"] = float(values[29])
        self.header["PixelSize"] = float(values[30])

    def printHeader(self):
        print("Size: ", self.header["Size"])
        print("Version: ", self.header["Version"])

        print("DetectorNumber: >>%s<<" % self.header["DetectorNumber"])
        print("SQUIDNumber: >>%s<<" % self.header["SQUIDNumber"])
        print("ElectronicNumber: >>%s<<" % self.header["ElectronicNumber"])
        print("PolarisNumber: >>%s<<" % self.header["PolarisNumber"])

        print("CurrentSystemTime_64", self.header["CurrentSystemTime_64"])
        print("CurrentSystemTime_milli", self.header["CurrentSystemTime_milli"])
        print("CurrentSystemTime_timezone", self.header["CurrentSystemTime_timezone"])
        print("CurrentSystemTime_dstflag", self.header["CurrentSystemTime_dstflag"])

        print("Localtime_sec", self.header["Localtime_sec"])
        print("Localtime_min", self.header["Localtime_min"])
        print("Localtime_hour", self.header["Localtime_hour"])
        print("Localtime_mday", self.header["Localtime_mday"])
        print("Localtime_mon", self.header["Localtime_mon"])
        print("Localtime_year", self.header["Localtime_year"])
        print("Localtime_wday", self.header["Localtime_wday"])
        print("Localtime_yday", self.header["Localtime_yday"])
        print("Localtime_isdst", self.header["Localtime_isdst"])

        print("ClockTime_ms", self.header["ClockTime_ms"])
        print("LiveTime_ms", self.header["LiveTime_ms"])
        print("DeadTime_ms", self.header["DeadTime_ms"])

        print("TraceLength", self.header["TraceLength"])
        print("SampleRate", self.header["SampleRate"])

        print("RegTemperature", self.header["RegTemperature"])
        print("IBias", self.header["IBias"])
        print("AmpFactor", self.header["AmpFactor"])

        print("AccVoltage", self.header["AccVoltage"])
        print("Aperture", self.header["Aperture"])
        print("WDistance", self.header["WDistance"])
        print("PixelSize", self.header["PixelSize"])

    def computeBaseLine(self, times_ms, data):
        endIndex = 0

        for index,time_ms in enumerate(times_ms):
            if time_ms >= 0.2:
                endIndex = index
                break

        #print endIndex

        total = sum(data[:endIndex])
        number = len(data[:endIndex])

        baseline = total/number

        return baseline

    def getPulse(self, pulseID, gain=1.0/5.0E3):
        dummy_header, times_ms, data = self.readTrace(pulseID)

        baseline = self.computeBaseLine(times_ms, data)

        pulseData = [(xx - baseline)*gain for xx in data]

        return times_ms, pulseData

def run():
    filepath = os.path.expanduser("~/works/prgrms/pythondev/pySpectrumFileFormat/testData/test01.trc")

    traceFile = TraceFile(filepath)

#    for pulseID in range(1,1450,1):
#        header, times_ms, data = traceFile.readTrace(pulseID)
#
#        maximum = max(data)
#
#        if maximum > 1000.0:
#            print pulseID

    #traceFile.readHeader()

    #traceFile.printHeader()

    pulseID = 1

    # First plot.

    dummy_header, times_ms, data = traceFile.readTrace(pulseID)

    dummy_line, = pylab.plot(times_ms, data)

    pylab.title("pulseID: %i" % (pulseID))

    pylab.xlabel(r"Time (ms)")

    pylab.ylabel(r"Pulse height (mV)")

    def click(event):
        global pulseID

        if event.button == 1:
            pulseID += 1
        elif event.button == 3:
            pulseID -= 1

            if pulseID < 1:
                pulseID = 1

        dummy_header, times_ms, data = traceFile.readTrace(pulseID)

        pylab.plot(times_ms, data, hold=False)
#        # update the data.
#        line.set_xdata(times_ms)
#
#        line.set_ydata(data)
#
        # redraw the canvas
        pylab.title("pulseID: %i" % (pulseID))

        pylab.draw()

    #register this function with the event handler.
    pylab.connect('button_press_event', click)

    pylab.show()

    #traceFile.printHeader()

if __name__ == '__main__':  # pragma: no cover
    run()
