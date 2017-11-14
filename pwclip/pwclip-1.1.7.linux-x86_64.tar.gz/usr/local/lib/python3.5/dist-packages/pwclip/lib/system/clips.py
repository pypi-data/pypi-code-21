#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
#
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
"""
clips - clipboard for various systems
"""
import sys

from os import name as osname, environ

from platform import system

from time import sleep, time

from subprocess import Popen, PIPE, DEVNULL

def clips():
	"""return `copy`, `paste` as system independent functions"""
	def winclips():
		"""windows clipboards - the ugliest thing i've ever seen"""
		from ctypes import \
            windll, memmove, \
            c_size_t, sizeof, \
            c_wchar_p, get_errno, c_wchar
		from ctypes.wintypes import \
            INT, HWND, DWORD, \
            LPCSTR, HGLOBAL, LPVOID, \
            HINSTANCE, HMENU, BOOL, UINT, HANDLE
		from contextlib import contextmanager
		GMEM_MOVEABLE = 0x0002
		CF_UNICODETEXT = 13
		class CheckedCall(object):
			def __init__(self, f):
				super(CheckedCall, self).__setattr__("f", f)
			def __call__(self, *args):
				ret = self.f(*args)
				if not ret and get_errno():
					raise PyperclipWindowsException("Error calling " + self.f.__name__)
				return ret
			def __setattr__(self, key, value):
				setattr(self.f, key, value)
		mkwin = CheckedCall(windll.user32.CreateWindowExA)
		mkwin.argtypes = [
            DWORD, LPCSTR,
            LPCSTR, DWORD,
            INT, INT,
            INT, INT,
            HWND, HMENU,
            HINSTANCE, LPVOID]
		mkwin.restype = HWND
		delwin = CheckedCall(windll.user32.DestroyWindow)
		delwin.argtypes = [HWND]
		delwin.restype = BOOL
		clip = windll.user32.OpenClipboard
		clip.argtypes = [HWND]
		clip.restype = BOOL
		clsclip = CheckedCall(windll.user32.CloseClipboard)
		clsclip.argtypes = []
		clsclip.restype = BOOL
		delclip = CheckedCall(windll.user32.EmptyClipboard)
		delclip.argtypes = []
		delclip.restype = BOOL
		getclip = CheckedCall(windll.user32.GetClipboardData)
		getclip.argtypes = [UINT]
		getclip.restype = HANDLE
		setclip = CheckedCall(windll.user32.SetClipboardData)
		setclip.argtypes = [UINT, HANDLE]
		setclip.restype = HANDLE
		allock = CheckedCall(windll.kernel32.GlobalAlloc)
		allock.argtypes = [UINT, c_size_t]
		allock.restype = HGLOBAL
		dolock = CheckedCall(windll.kernel32.GlobalLock)
		dolock.argtypes = [HGLOBAL]
		dolock.restype = LPVOID
		unlock = CheckedCall(windll.kernel32.GlobalUnlock)
		unlock.argtypes = [HGLOBAL]
		unlock.restype = BOOL
		@contextmanager
		def window():
			"""
			Context that provides a valid Windows hwnd.
			"""
			hwnd = mkwin(0, b"STATIC", None, 0, 0, 0, 0, 0,
									   None, None, None, None)
			try:
				yield hwnd
			finally:
				delwin(hwnd)
		@contextmanager
		def clipboard(hwnd):
			"""
			Context manager that opens the clipboard and prevents
			other applications from modifying the clipboard content.
			"""
			t = time() + 0.5
			success = False
			while time() < t:
				success = clip(hwnd)
				if success:
					break
				sleep(0.01)
			if not success:
				raise Exception("could not open clipboard")
			try:
				yield
			finally:
				clsclip()
		def _copy(text, mode=None):
			with window() as hwnd:
				with clipboard(hwnd):
					delclip()
					if text:
						count = len(text) + 1
						handle = allock(GMEM_MOVEABLE, count*sizeof(c_wchar))
						locked_handle = dolock(handle)
						ctypes.memmove(
						    c_wchar_p(locked_handle),
                            c_wchar_p(text), count*sizeof(c_wchar))
						unlock(handle)
						setclip(CF_UNICODETEXT, handle)
		def _paste(mode=None):
			with clipboard(None):
				handle = getclip(CF_UNICODETEXT)
				if not handle:
					return ""
				return c_wchar_p(handle).value

		return _copy, _paste

	def osxclips():
		def _copy(text, mode=None):
			text = text if text else ''
			p = Popen(['pbcopy', 'w'], stdin=subprocess.PIPE, close_fds=True)
			p.communicate(input=text.encode('utf-8'))
		def _paste(mode=None):
			p = subprocess.Popen(['pbpaste', 'r'],
                    stdout=subprocess.PIPE, close_fds=True)
			out, _ = p.communicate()
			return out.decode('utf-8')
		return _copy, _paste

	def linclips():
		"""linux clipboards"""
		def _copy(text, mode='p'): # mode in ('p', 'b', 'pb')
			"""linux copy function"""
			text = text if text else ''
			if 'p' in mode:
				with Popen(['xsel', '-p', '-i'], stdin=PIPE, stderr=DEVNULL
                      ) as prc:
					prc.communicate(input=text.encode('utf-8'))
			if 'b' in mode:
				with Popen(['xsel', '-b', '-i'], stdin=PIPE, stderr=DEVNULL
                      ) as prc:
					prc.communicate(input=text.encode('utf-8'))

		def _paste(mode='p'):
			"""linux paste function"""
			if mode == 'p':
				out, _ = Popen([
                    'xsel', '-p', '-o'], stdout=PIPE, stderr=DEVNULL
                    ).communicate()
				return out.decode()
			elif mode == 'b':
				out, _ = Popen([
                    'xsel', '-b', '-o'], stdout=PIPE, stderr=DEVNULL
                    ).communicate()
				return out.decode()
			elif mode in ('pb', 'bp'):
				pout, _ = Popen([
                    'xsel', '-p', '-o'], stdout=PIPE, stderr=DEVNULL
                    ).communicate()
				bout, _ = Popen([
                    'xsel', '-b', '-o'], stdout=PIPE, stderr=DEVNULL
                    ).communicate()
				return pout.decode(), bout.decode()
		return _copy, _paste
	# decide which copy, paste functions to return [windows|mac|linux] mainly
	if osname == 'nt' or system() == 'Windows':
		return winclips()
	elif osname == 'mac' or system() == 'Darwin':
		return osxclips()
	return linclips()

copy, paste = clips()
