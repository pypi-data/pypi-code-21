# coding=utf-8
import os
import tkFileDialog
import wave
from Tkconstants import LEFT
from datetime import datetime
from Tkinter import Button, Label, mainloop, Frame, Entry, StringVar, Tk
from pyaudio import PyAudio, paInt16


class Record:
    def __init__(self):
        # define of params
        self.NUM_SAMPLES = 2000
        self.framerate = 16000
        self.channels = 1
        self.sampwidth = 2
        # record time
        self.TIME = 10

        root = Tk()
        root.resizable(False, False)
        self.center_window(root, 300, 110)
        chose_file_path_frm = Frame(root)
        chose_file_path_top_frm = Frame(chose_file_path_frm)
        labe_choose_path = Label(chose_file_path_top_frm, text="chose a path:        ")
        labe_choose_path.pack()
        chose_file_path_top_frm.pack()
        chose_file_path_down_frm = Frame(chose_file_path_frm)
        path_entry = Entry(chose_file_path_down_frm)
        self.contend_path_entry = StringVar()
        self.contend_path_entry.set('record/zhangxulong')
        path_entry.config(textvariable=self.contend_path_entry, state='disabled', highlightbackground='red')
        path_entry.pack(side=LEFT)
        file_chose_button = Button(chose_file_path_down_frm, text='chose', command=self.chose_file_path)
        file_chose_button.pack(side=LEFT)

        chose_file_path_down_frm.pack()
        set_a_file_name_for_record_frm = Frame(chose_file_path_frm)

        set_a_file_name_for_record_top_frm = Frame(set_a_file_name_for_record_frm)
        labe_file_nam = Label(set_a_file_name_for_record_frm, text="set a file name:        ")
        labe_file_nam.pack()
        set_a_file_name_for_record_top_frm.pack()

        name_entry_frm = Frame(set_a_file_name_for_record_frm)

        name_entry = Entry(name_entry_frm)
        self.contend_name_entry = StringVar()
        self.contend_name_entry.set(datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))
        name_entry.config(textvariable=self.contend_name_entry)
        name_entry.pack(side=LEFT)
        start_button = Button(name_entry_frm, text='record', command=self.record_wave)
        start_button.pack(side=LEFT)
        name_entry_frm.pack()
        set_a_file_name_for_record_frm.pack()
        chose_file_path_frm.pack()

    def chose_file_path(self):

        files = tkFileDialog.askdirectory()
        self.contend_path_entry.set(files)

        return 0

    def save_wave_file(self, filename, data):
        '''save the date to the wav file'''
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.framerate)
        wf.writeframes("".join(data))
        wf.close()
        return 0

    def file_path(self, FILE_PATH='/home/2'):
        if os.path.isdir(FILE_PATH):
            print 'dir %s exists' % (FILE_PATH)
            pass
        else:
            print  'dir %s not exists' % (FILE_PATH)
            os.makedirs(FILE_PATH)
        return 0

    def record_wave(self):
        wav_path = self.contend_path_entry.get()
        wav_name = self.contend_name_entry.get()
        if wav_path == "" or wav_name == "":
            filename = datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ".wav"
        else:
            self.file_path(wav_path)
            filename = wav_path + "/" + wav_name + ".wav"
        # open the input of wave
        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=1,
                         rate=self.framerate, input=True,
                         frames_per_buffer=self.NUM_SAMPLES)
        save_buffer = []
        count = 0
        while count < self.TIME * 4:
            # read NUM_SAMPLES sampling data
            string_audio_data = stream.read(self.NUM_SAMPLES)
            save_buffer.append(string_audio_data)
            count += 1
            print '.'

        self.save_wave_file(filename, save_buffer)
        save_buffer = []
        print filename, "saved"
        self.contend_name_entry.set("☆☆☆☆ saved at: " + filename)
        return 0

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        print(size)
        root.geometry(size)
        return 0


def recordAudio():
    Record()
    mainloop()
