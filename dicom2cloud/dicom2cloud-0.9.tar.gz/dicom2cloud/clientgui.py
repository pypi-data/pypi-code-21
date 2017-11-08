import csv
import shutil
import threading
import time
from glob import iglob
from hashlib import sha256
from multiprocessing import freeze_support
from os import R_OK, mkdir, access, walk
from os.path import join, isdir,split
from uploadScripts import get_class

import dicom
from dicom.filereader import InvalidDicomError

from runDocker import startDocker, checkIfDone, getStatus, finalizeJob
from noname import *

global_series = {}

# Required for dist?
freeze_support()
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class DockerThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, wxObject, targetdir, seriesid, processname, server):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.wxObject = wxObject
        self.processname = processname
        self.targetdir = targetdir
        self.seriesid = seriesid
        self.server = server

    # ----------------------------------------------------------------------
    def run(self):
        i = 0
        try:
            # event.set()
            # lock.acquire(True)
            # Do work
            container = startDocker(self.targetdir)
            ctr = 0
            print "Started"
            while (not checkIfDone(container)):
                time.sleep(5)
                wx.PostEvent(self.wxObject, ResultEvent((ctr, self.seriesid, self.processname)))
                ctr = 1

            # Check that everything ran ok
            if getStatus(container) != 0:
                raise Exception("There was an error while anonomizing the dataset.")

            # Get the resulting mnc file back to the original directory
            finalizeJob(container, self.targetdir)

            #Upload MNC to server
            mncfile = join(self.targetdir,'output.mnc')
            uploadfile = join(self.targetdir,self.seriesid + '.mnc')
            if access(mncfile,R_OK):
                shutil.copyfile(mncfile,uploadfile)
                uploaderClass = get_class(self.server)
                uploader = uploaderClass(self.seriesid)
                uploader.upload(uploadfile, self.processname)
                wx.PostEvent(self.wxObject, ResultEvent((2, self.seriesid, self.processname)))
                print "Uploaded file: %s to %s" % (uploadfile, self.server)
            print "Finished DockerThread"

        except Exception as e:
            wx.PostEvent(self.wxObject, ResultEvent((-1, self.seriesid, self.processname)))

        finally:
            wx.PostEvent(self.wxObject, ResultEvent((10, self.seriesid, self.processname)))
            # logger.info('Finished FilterThread')
            # self.terminate()
            # lock.release()
            # event.clear()


########################################################################
class HomePanel(WelcomePanel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(HomePanel, self).__init__(parent)
        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # text = wx.TextCtrl(self, style=wx.TE_MULTILINE,value=self.__loadContent())
        # hbox.Add(text, proportion=1, flag=wx.EXPAND)
        # self.SetSizer(hbox)
        self.m_richText1.AddParagraph(r'''***Welcome to the Dicom2Cloud App***''')
        self.m_richText1.AddParagraph(r''' An application to process your MRI scans in the cloud ''')
        # self.m_richText1.BeginNumberedBullet(1, 0.2, 0.2, wx.TEXT_ATTR_BULLET_STYLE)
        self.m_richText1.AddParagraph(
            r"1. Select a Folder containing one or more MRI scans to process in the Files Panel")
        self.m_richText1.AddParagraph(r"2. Select which processes to run and monitor their progress")
        self.m_richText1.AddParagraph(r" ")
        #self.m_richText1.AddParagraph(r"Created by Clinic2Cloud team at HealthHack 2017")
        self.m_richText1.AddParagraph(
            r"Copyright 2017 Dicom2Cloud Team")
        self.m_richText1.AddParagraph(
            r"This is free software, you may use/distribute it under the terms of the Apache license v2")



########################################################################
class ProcessRunPanel(ProcessPanel):
    def __init__(self, parent):
        super(ProcessRunPanel, self).__init__(parent)
        self.processes = [{'caption': 'None', 'href': 'na',
                           'description': ''},
                          {'caption': 'QSM', 'href': 'qsm',
                           'description': 'Estimate quantitative susceptibility map from gradient echo data. Phase and magnitude images required.',
                           },
                          {'caption': 'Atlas', 'href': 'atlas',
                           'description': 'Estimate atlas-based segmentation from T1-weighted image. Magnitude image required.',
                           }
                          ]

        #processes = [p['caption'] for p in self.processes]
        # self.m_checkListProcess.AppendItems(processes)
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.progressfunc)
        # EVT_CANCEL(self, self.stopfunc)
        # Set timer handler
        self.start = {}
        self.toggleval =0
        self.server =''

    def OnShowDescription(self, event):
        print(event.String)
        desc = [p['description'] for p in self.processes if p['caption'] == event.String]

        # Load to GUI
        self.m_stTitle.SetLabelText(event.String)
        self.m_stDescription.SetLabelText(desc[0])
        self.Layout()

    def progressfunc(self, msg):
        """
        Update progress bars in table - multithreaded
        :param count:
        :param row:
        :param col:
        :return:
        """
        (count, seriesid, process) = msg.data
        print("\nProgress updated: ", time.ctime())
        print('count = ', count)
        row = 0
        for item in range(self.m_dataViewListCtrlRunning.GetItemCount()):
            if self.m_dataViewListCtrlRunning.GetValue(row=item,col=1) == seriesid:
                row = item

        status = ''
        if count == 0:
            self.m_dataViewListCtrlRunning.AppendItem([process, seriesid, count, "Pending"])
            self.start[seriesid] = time.time()
        elif count < 0:
            self.m_dataViewListCtrlRunning.SetValue("ERROR", row=row, col=3)
            self.m_btnRunProcess.Enable()
        elif count == 1:
            if self.toggleval == 25:
                self.toggleval = 75
            else:
                self.toggleval =25
            self.m_dataViewListCtrlRunning.SetValue("Running", row=row, col=3)
            self.m_dataViewListCtrlRunning.SetValue(self.toggleval, row=row, col=2)
        elif count == 2:
            self.m_dataViewListCtrlRunning.SetValue("Uploading", row=row, col=3)
            self.m_dataViewListCtrlRunning.SetValue(75, row=row, col=2)
        else:
            if seriesid in self.start:
                endtime = time.time() - self.start[seriesid]
                status = "(%d secs)" % endtime
            print(status)
            self.m_dataViewListCtrlRunning.SetValue(100, row=row, col=2)
            self.m_dataViewListCtrlRunning.SetValue("Uploaded " + status, row=row, col=3)
            self.m_btnRunProcess.Enable()

    def getFilePanel(self):
        """
        Get access to filepanel
        :return:
        """
        filepanel = None

        for fp in self.Parent.Children:
            if isinstance(fp, FileSelectPanel):
                filepanel = fp
                break
        return filepanel

    def OnCancelScripts(self, event):
        """
        Find a way to stop processes
        :param event:
        :return:
        """
        self.shutdown()
        print("Cancel multiprocessor")
        event.Skip()

    def OnRunScripts(self, event):
        """
        Run selected scripts sequentially - updating progress bars
        :param e:
        :return:
        """
        # Clear processing window
        self.m_dataViewListCtrlRunning.DeleteAllItems()
        # Disable Run button
        # self.m_btnRunProcess.Disable()
        btn = event.GetEventObject()
        btn.Disable()
        # Get selected processes
        selection = self.m_checkListProcess.GetStringSelection()
        print("Processes selected: ", selection)
        self.server = self.m_server.GetStringSelection().lower()
        # Get data from other panels
        filepanel = self.getFilePanel()
        msg=''
        filenames = []
        num_files = filepanel.m_dataViewListCtrl1.GetItemCount()
        print('All Files:', num_files)
        try:
            if selection != 'None' and num_files > 0 and filepanel.outputdir is not None and len(filepanel.outputdir)>0:
                self.outputdir = filepanel.outputdir
                if filepanel.inputdir == self.outputdir:
                    msg ='Input and output directories are the same - cannot continue as will overwrite files'
                    raise ValueError(msg)
                csvheader=['Filename','Series','Process','Server']
                with open(join(self.outputdir,'dummydatabase.txt'), 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csvheader)
                    writer.writeheader()

                    for i in range(0, num_files):
                        if filepanel.m_dataViewListCtrl1.GetToggleValue(i, 0):
                            # for each series, create temp dir and copy files
                            seriesid = filepanel.m_dataViewListCtrl1.GetValue(i, 6)
                            self.m_stOutputlog.SetLabelText("Copying DICOM data %s ... please wait" % seriesid)
                            dest = self.copyseries(seriesid)

                            # TODO: Call Docker with series (dest) - then poll
                            t = DockerThread(self, dest, seriesid, selection, self.server)
                            t.start()
                            self.m_stOutputlog.SetLabelText("Docker thread started %s ... please wait" % seriesid)
                            writer.writerow({'Filename': dest, 'Series': seriesid, 'Process': selection, 'Server': self.server})

            else:
                if selection == 'None':
                    msg = "No processes selected"
                elif filepanel.outputdir is None:# or len(filepanel.outputdir)<=0:
                    msg = "No outputdir provided"
                else:
                    msg = "No files selected - please go to Files Panel and add to list"
                raise ValueError(msg)
        except ValueError as e:
            self.Parent.Warn(msg)
        # Enable Run button
        self.m_btnRunProcess.Enable()


    def copyseries(self, seriesnum):
        if seriesnum in global_series:
            subdir = self.generateuid(seriesnum)
            dest = join(self.outputdir, subdir)
            if not access(dest, R_OK):
                mkdir(dest)
            for f in global_series[seriesnum]['files']:
                shutil.copy(f, dest)
            return dest


    def generateuid(self, seriesnum):
        hashed = sha256(seriesnum).hexdigest()
        return hashed


    def checkhashed(self, seriesnum, hashed):
        if hashed == sha256(seriesnum).hexdigest():
            print("It Matches!")
            return True
        else:
            print("It Does not Match")
            return False

########################################################################


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, panel,target):
        super(MyFileDropTarget, self).__init__()
        self.target = target
        self.droppedfiles=[]
        self.panel = panel

    def OnDropFiles(self, x, y, filenames):
        for fname in filenames:
            if not isdir(fname):
                fname = split(fname)[0]
            self.panel.extractSeriesInfo(fname)
            #self.target.AppendItem([True, fname])  # TODO
        return len(filenames)


########################################################################
class FileSelectPanel(FilesPanel):
    def __init__(self, parent):
        super(FileSelectPanel, self).__init__(parent)
        self.filedrop = MyFileDropTarget(self,self.m_dataViewListCtrl1)
        self.m_tcDragdrop.SetDropTarget(self.filedrop)
        self.outputdir=''

    def OnInputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing input files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir = str(dlg.GetPath())
            # self.statusbar.SetStatusText("Loaded: %s" % self.inputdir)
            self.txtInputdir.SetValue(self.inputdir)
            self.extractSeriesInfo(self.inputdir)

        dlg.Destroy()

    def OnOutputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory for upload files")
        if dlg.ShowModal() == wx.ID_OK:
            self.outputdir = str(dlg.GetPath())
            self.txtOutputdir.SetValue(self.outputdir)
        dlg.Destroy()

    def extractSeriesInfo(self, inputdir):
        """
        Find all matching files in top level directory
        :param event:
        :return:
        """
        self.m_status.SetLabelText("Detecting DICOM data ... please wait")
        # allfiles = [y for y in iglob(join(inputdir, '*.IMA'))]
        allfiles = [y for x in walk(inputdir) for y in iglob(join(x[0], '*.IMA'))]
        # series = {}
        for filename in allfiles:
            try:
                dcm = dicom.read_file(filename)
            except InvalidDicomError:
                print("Not DICOM - skipping: ", filename)
                continue

            # Check DICOM header info

            series_num = str(dcm.SeriesInstanceUID)
            imagetype = str(dcm.ImageType[2])
            dicomdata = {'patientid': str(dcm.PatientID),
                         'patientname': str(dcm.PatientName),
                         'series_num': series_num,
                         'sequence': str(dcm.SequenceName),
                         'protocol': str(dcm.ProtocolName),
                         'imagetype': imagetype
                         }
            if series_num not in global_series:
                global_series[series_num] = {'dicomdata': dicomdata, 'files': []}
            global_series[series_num]['files'].append(filename)

        # Load for selection
        for s0 in global_series.items():
            s = s0[1]['dicomdata']
            numfiles= len(s0[1]['files'])

            # Columns:      Toggle      Select
            #               Text        PatientID
            #               Text        Sequence
            #               Text        Protocol
            #               Text        Image Type
            #               Text        Num Files
            #               Text        Series ID
            self.m_dataViewListCtrl1.AppendItem(
                [True, s['patientname'], s['sequence'], s['protocol'],
                s['imagetype'], str(numfiles), s['series_num']])

        # self.col_file.SetMinWidth(wx.LIST_AUTOSIZE)
        msg = "Total Series loaded: %d" % self.m_dataViewListCtrl1.GetItemCount()
        self.m_status.SetLabelText(msg)

    def OnSelectall(self, event):
        for i in range(0, self.m_dataViewListCtrl1.GetItemCount()):
            self.m_dataViewListCtrl1.SetToggleValue(event.GetSelection(), i, 0)
        print("Toggled selections to: ", event.GetSelection())

    def OnClearlist(self, event):
        print("Clear items in list")
        self.m_dataViewListCtrl1.DeleteAllItems()


########################################################################
class AppMain(wx.Listbook):
    def __init__(self, parent):
        """Constructor"""
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=wx.BK_DEFAULT)

        self.InitUI()
        self.Centre(wx.BOTH)
        self.Show()

    def InitUI(self):

        # make an image list using the LBXX images
        # il = wx.ImageList(32, 32)
        # for x in [wx.ArtProvider.]:
        #     obj = getattr(images, 'LB%02d' % (x + 1))
        #     bmp = obj.GetBitmap()
        #     il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_FRAME_ICON, (16, 16))
        # il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_FRAME_ICON, (16, 16))
        # il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_FRAME_ICON, (16, 16))
        # il.Add(bmp)
        # self.AssignImageList(il)

        pages = [(HomePanel(self), 'Welcome'),
                 (FileSelectPanel(self), "Select Files"),
                 (ProcessRunPanel(self), "Upload Processes"),
                 (CloudRunPanel(self), "Check Cloud")]

        imID = 0
        for page, label in pages:
            # self.AddPage(page, label, imageId=imID)
            self.AddPage(page, label)
            imID += 1

        # TODO: This line doesn't work
        self.GetListView().SetColumnWidth(0, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    # ----------------------------------------------------------------------
    def OnPageChanged(self, event):
        # old = event.GetOldSelection()
        # new = event.GetSelection()
        # sel = self.GetSelection()
        # msg = 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        # print(msg)
        event.Skip()

    # ----------------------------------------------------------------------
    def OnPageChanging(self, event):
        # old = event.GetOldSelection()
        # new = event.GetSelection()
        # sel = self.GetSelection()
        # msg = 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        # print(msg)
        event.Skip()

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def OnQuit(self, e):
        self.Close()

    def OnCloseWindow(self, e):

        dial = wx.MessageDialog(None, 'Are you sure you want to quit?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()

########################################################################
class CloudRunPanel(CloudPanel):
    def __init__(self, parent):
        super(CloudRunPanel, self).__init__(parent)

    def OnUpdate( self, event ):
        """
        Load dummydatabase and for each seriesID - poll class
        :param event:
        :return:
        """
        filepanel = self.getFilePanel()
        self.outputdir = filepanel.outputdir
        dbfile = join(self.outputdir,'dummydatabase.txt')
        csvheader = ['Filename', 'Series', 'Process', 'Server']

        self.m_tcResults.AppendText("\n***********\nCloud processing results\n***********\n")
        with open(dbfile) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row['Filename'], row['Server'])
                seriesid= split(row['Filename'])[1]
                server = row['Server'].lower()
                #Get uploader class and query
                uploaderClass = get_class(server)
                uploader = uploaderClass(seriesid)
                done = uploader.isDone()
                if done:
                    uploader.download(join(self.outputdir,seriesid,'download.tar'))
                    msg = 'Series: %s \n\tSTATUS: Complete (%s)\n' % (seriesid,join(self.outputdir,seriesid,'download.tar'))

                else:
                    msg= 'Series: %s \n\tSTATUS: Still processing\n' % seriesid
                self.m_tcResults.AppendText(msg)
        print('Finished cloud panel update')

    def getFilePanel(self):
        """
        Get access to filepanel
        :return:
        """
        filepanel = None

        for fp in self.Parent.Children:
            if isinstance(fp, FileSelectPanel):
                filepanel = fp
                break
        return filepanel


    def OnClearOutput( self, event ):
        """
        Clear output panel
        :param event:
        :return:
        """
        self.m_tcResults.Clear()

########################################################################
class ClinicApp(wx.Frame):
    """
    Frame that holds all other widgets
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Dicom2Cloud App",
                          size=(700, 700)
                          )

        # self.timer = wx.Timer(self)
        # self.Bind(wx.EVT_TIMER, self.update, self.timer)
        panel = wx.Panel(self)

        notebook = AppMain(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        self.Center(wx.BOTH)
        self.Show()

def main():
    app = wx.App()
    frame = ClinicApp()
    app.MainLoop()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()

