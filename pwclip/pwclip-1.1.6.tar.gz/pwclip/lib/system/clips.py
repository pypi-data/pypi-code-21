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
from os import name as osname

from platform import system

from time import sleep, time

from subprocess import Popen, PIPE, DEVNULL

def clips():
	"""return `copy`, `paste` as system independent functions"""
	def winclips():
		"""windows clipboards - the ugliest thing i've ever seen"""
		from ctypes import \
            windll, memmove, c_size_t, \
            sizeof, c_wchar_p, get_errno, c_wchar
		from ctypes.wintypes import \
            INT, HWND, DWORD, LPCSTR, HGLOBAL, \
            LPVOID, HINSTANCE, HMENU, BOOL, UINT, HANDLE
		from contextlib import contextmanager
		GMEM_MOVEABLE = 0x0002
		CF_UNICODETEXT = 13
		class CheckedCall(object):
			"""fancy windows callchecker"""
			def __init__(self, f):
				super(CheckedCall, self).__setattr__("f", f)
			def __call__(self, *args):
				ret = self.f(*args)
				if not ret and get_errno():
					raise RuntimeError("Error calling %s"%self.f.__name__)
				return ret
			def __setattr__(self, key, value):
				setattr(self.f, key, value)
		mkwin = CheckedCall(windll.user32.CreateWindowExA)
		mkwin.argtypes = [
            DWORD, LPCSTR, LPCSTR, DWORD, INT, INT,
            INT, INT, HWND, HMENU, HINSTANCE, LPVOID]
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
			"""context that provides a valid window (hwnd)"""
			hwnd = mkwin(0, b"STATIC", None, 0, 0, 0, 0, 0,
									   None, None, None, None)
			try:
				yield hwnd
			finally:
				delwin(hwnd)
		@contextmanager
		def clipboard(hwnd):
			"""windows clipboard context manager"""
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
			"""windows copy function"""
			if mode == 'b':
				return
			with window() as hwnd:
				with clipboard(hwnd):
					delclip()
					if text:
						count = len(text) + 1
						handle = allock(GMEM_MOVEABLE, count*sizeof(c_wchar))
						locked_handle = dolock(handle)
						memmove(
						    c_wchar_p(locked_handle),
                            c_wchar_p(text), count*sizeof(c_wchar))
						unlock(handle)
						setclip(CF_UNICODETEXT, handle)
		def _paste(_=None):
			"""windows paste function"""
			with clipboard(None):
				handle = getclip(CF_UNICODETEXT)
				if not handle:
					return "", ""
			return c_wchar_p(handle).value, c_wchar_p(handle).value
		return _copy, _paste

	def osxclips():
		""""OSX clipboards"""
		def _copy(text, mode=None):
			"""osx copy function"""
			text = text if text else ''
			if mode == 'b':
				return
			with Popen(['pbcopy'], stdin=PIPE, close_fds=True) as prc:
				prc.communicate(input=text.encode('utf-8'))
		def _paste(_=None):
			"""osx paste function"""
			with Popen(['pbpaste'], stdout=PIPE, close_fds=True) as prc:
				out, _ = prc.communicate()
				return out.decode('utf-8'), None
		return _copy, _paste

	def linclips():
		"""linux clipboards"""
		xsel = ['xsel', '-l', '/dev/null']
		def _copy(text, mode='p'):
			"""linux copy function"""
			_xsel = xsel + ['-i']
			text = text if text else ''
			for m in mode:
				with Popen(
                      _xsel + ['-%s'%m], stdin=PIPE, stderr=DEVNULL) as prc:
					prc.communicate(input=text.encode('utf-8'))
		def _paste(mode='p'):
			"""linux paste function"""
			_xsel = xsel + ['-o']
			if mode == 'p':
				out, _ = Popen(
                    _xsel + ['-p'], stdout=PIPE, stderr=DEVNULL).communicate()
				return out.decode()
			elif mode == 'b':
				out, _ = Popen(
                    _xsel + ['-b'], stdout=PIPE, stderr=DEVNULL).communicate()
				return out.decode()
			elif mode in ('pb', 'bp'):
				pout, _ = Popen(
                    _xsel + ['-p'], stdout=PIPE, stderr=DEVNULL).communicate()
				bout, _ = Popen(
                    _xsel + ['-b'], stdout=PIPE, stderr=DEVNULL).communicate()
				return pout.decode(), bout.decode()
		return _copy, _paste
	# decide which copy, paste functions to return [windows|mac|linux] mainly
	if osname == 'nt' or system() == 'Windows':
		return winclips()
	elif osname == 'mac' or system() == 'Darwin':
		return osxclips()
	return linclips()

copy, paste = clips()
