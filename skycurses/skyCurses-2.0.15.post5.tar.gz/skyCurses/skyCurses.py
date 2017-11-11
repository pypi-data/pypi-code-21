#!/usr/bin/env python3

from redskyAPI.skychat import SkyChatClient
from winCurses import *

import re
from sys import argv, exit
from html import unescape
import curses
import os, signal
import pafy
from time import sleep
from threading import Thread
import json
from ._audio_wrapper import Sound

# OPTIONNAL MODULES
try:
    from ._mplayer_wrapper import Player
    MPLAYER_ENABLED = True
except ImportError:
    print("""Module \"mplayer.py\" not found
The client will still work, but won't be able to play youtube musics.

To fix that, install the missing package (pip install mplayer.py)""")
    sleep(5)
    MPLAYER_ENABLED = False

try:
    import webbrowser
except ImportError:
    print("""Module \"webbrowser\" not found
Links opening is disabled""")
    sleep(2)
    webbrowser = None


# CONSTANTS
HISTORY_SIZE   = 4096
CHAT_BUFF_SIZE = 256
CONFIG_DIR     = '.skycurses'
KICK_TIMEOUT   = 5
PLAYER_SYMBOLS = {
        'off'  : ['x', "×"],
        'stop' : ['=', "◼"],
        'play' : ['>', "▶"],
        }

color_equiv = {
        '#ef4848' : ('cr', curses.COLOR_RED),
        '#bf00ff' : ('cm', curses.COLOR_MAGENTA),
        '#046380' : ('cb', curses.COLOR_BLUE),
        '#457dbb' : ('cc', curses.COLOR_CYAN),
        '#85c630' : ('cg', curses.COLOR_GREEN),
        '#ffab46' : ('cy', curses.COLOR_YELLOW),
        '#f5a6bf' : ('cr', curses.COLOR_RED),
        '#999999' : ('cw', curses.COLOR_WHITE),
        'grey'    : ('cw', curses.COLOR_WHITE),
        '#666666' : ('cw', curses.COLOR_WHITE),
        }

class SkyCurses(SkyChatClient):
    def on_creation(self):
        """ Used like the __init__ function here, but called after
        SkyChatClient.__init__(self)
        """
        # load mplayer
        self.player      = MPLAYER_ENABLED and Player()
        self.current_vid = ""

        # Curses init
        self.main_win         = Win()
        #                                               |-------POSITION--------|-------DIMENSION---------|
        self.title_win        = WTitle(self.main_win,    Coord(0,0),             Coord(3, (1, True)),      borders=[0]*8)
        self.notif_win        = WNotif(self.main_win,    Coord(3, 0),            Coord(1, (1, True)),      borders=[0]*8)
        self.player_win       = WTitle(self.main_win,    Coord(4, 0),            Coord(3, 3),              borders=[0]*8)
        self.player_bar       = WProgress(self.main_win, Coord(4, 3),            Coord(3, -3),             borders=[0]*8, function=self._get_player_pos)
        self.chat_win         = WDisp(self.main_win,     Coord(7, 0),            Coord(-11, (0.85, True)), borders=[0]*8)
        self.input_win        = WInput(self.main_win,    Coord(-3, 0),           Coord(1, (1, True)),      borders=[0]*8)
        self.clients_list_win = WList(self.main_win,     Coord(7, (0.85, True)), Coord(-11, (0.15, True)), borders=[0]*8)
        self.typelist_win     = WNotif(self.main_win,    Coord(-4, 0),           Coord(1, (0.5, True)),    borders=[0]*8)
        self.link_win         = WNotif(self.main_win,    Coord(-4, (0.5, True)), Coord(1, (0.5, True)),    borders=[0]*8, align=1)
        self.main_win.refresh()
        self.input_win.start()
        self.player_bar.start()
        self.input_win.set_focus()

        # Test if winCurses can display utf-8
        player_status = 'off'
        try:
            self.player_win.set_title(PLAYER_SYMBOLS[player_status][1])
        except Exception:
            self.UTF8_ENABLED = False
            self.player_win.set_title(PLAYER_SYMBOLS[player_status][self.UTF8_ENABLED])
        else:
            self.UTF8_ENABLED = True

        # Multiple chats histories
        self.raw_msg_hist = {
                'main' : [],
                }
        self.chat_list = ['main']
        self.cur_chat  = 0
        self.unread = {}

        # Completion
        self.complete = ('', '', 0) # as in (word_to_complete, completion, position in potential completions list)

        # Sounds
        self.sounds = {
                'nomi' : Sound(self._full_path("sounds/nomi.wav")),
                'msg'  : Sound(self._full_path("sounds/msg.wav")),
                'mp'   : Sound(self._full_path("sounds/mp.wav")),
                'end'  : Sound(self._full_path("sounds/end.wav")),
                }

        # Selected link
        self.selected_link = {}

        # Sent messages history
        self.history     = []
        self.history_pos = 0

        # config
        self.sound_on   = True
        self.player_on  = False
        self.chat_sound = { 'main' : False }

        self._load()

    def on_connect(self):
        # Add youtube sync management
        self.sock.on('yt_sync', self.on_yt_sync)

        self._set_title()
        self.input_win.on_return   = self._process_message
        self.input_win.on_typing   = lambda x : self.set_typing(x) if not self.input_win.input_buff.startswith("/") and self.cur_chat == 0 else None
        self.input_win.on_spec_key = self._handle_spec_key

    def on_old_message(self, msg):
        self._disp_msg(msg)

    def on_message(self, msg):
        self._disp_msg(msg)

    def on_private_message(self, msg):
        msg['message_raw'] = unescape(msg.get('message_raw', ''))
        if msg['pseudo'].lower() == self.pseudo.lower():
            chat = msg['cor'].lower()
        else:
            chat = msg['pseudo'].lower()
        self._disp_msg(msg, chat)

    def on_connected_list(self, msg):
        def prettify_time(seconds):
            if seconds < 10:
                return("actif")
            elif seconds < 60:
                return("%ds" % (seconds))
            elif seconds < 900:
                return("%dm" % (seconds // 60))
            else:
                return("AFK")

        msg['list'].sort(key=lambda x : x['right'], reverse=True)
        self.clients = [ c['pseudo'] for c in msg['list'] ]
        new_cli_list = [
            (
                "%s (%s)" % (cli['pseudo'], prettify_time(cli['last_activity'])),
                (color_equiv[cli['color']][1] if cli['color'] in color_equiv else curses.COLOR_WHITE)
            )
            for cli in msg['list']
            ]
        self.clients_list_win.load(new_cli_list)

    def on_yt_sync(self, msg):
        def _load_video():
            try:
                video = pafy.new("https://www.youtube.com/watch?v=%s" % (msg['id']))
                bestaudio = video.getbestaudio()
                if not bestaudio:
                    return
                self.player.loadfile(bestaudio.url)
                for i in range(10):
                    if self.player.time_pos != None:
                        break
                    sleep(0.5)
                self.player.pause()
                self.player.seek(int(msg['cursor']))
                self.player_win.set_title(PLAYER_SYMBOLS['play'][self.UTF8_ENABLED])
            except Exception as e:
                self._log(str(e), "Player Error")


        if MPLAYER_ENABLED and self.player_on:
            self._log(str(msg), "YT_SYNC")
            if 'id' in msg and msg['id'] != self.current_vid:
                self.current_vid = msg['id']
                Thread(target=_load_video).start()
            elif len(msg) == 0:
                self.player.stop()
                self.player_win.set_title(PLAYER_SYMBOLS['stop'][self.UTF8_ENABLED])

    def on_typing_list(self, msg):
        if msg:
            self.typelist_win.disp("%s %s typing..." % (', '.join(msg), ('is' if len(msg) == 1 else 'are')))
        else:
            self.typelist_win.reset()

    def _disp_msg(self, msg, chat='main'):
        if 'message_raw' in msg or 'quote_msg' in msg: # Some quotes do not have messages
            message = msg.get('message_raw', '').lstrip(' ') # Remove leading spaces
        else:
            message = unescape(re.sub('<[^>]+>', '', msg['message']))
        message = message.replace('\\', '\\\\').replace('\r', '').replace('<', '\\<').replace('>', '\\>')

        # Quotes
        if 'quote_msg' in msg:
            message = "\"[%s] %s\" → %s" % (msg['quote_pseudo'], msg['quote_msg'], message)

        pseudo_color = color_equiv[msg['color']][0] if 'color' in msg and msg['color'] in color_equiv else 'b'

        chat = chat.lower()
        if chat not in self.chat_list:
            self.chat_list.append(chat)
            self.raw_msg_hist[chat] = []
            self.chat_sound[chat]   = True

        if msg.get('message_type') == 'user_me':
            line = "<b>* <%s>%s</%s> %s [%s] *</b>" % (pseudo_color, msg['pseudo'], pseudo_color, message, msg['id'])
        else:
            line = "<b><%s>%s</%s></b> %s %s" % (pseudo_color, msg['pseudo_html'], pseudo_color, " [%d]" % (msg['id']) if msg['id'] else "", message)

        self.raw_msg_hist[chat].append(line)
        if self.chat_list[self.cur_chat] == chat:
            self.chat_win.disp(line)
        else:
            self.unread[chat] = 1 + (self.unread[chat] if chat in self.unread else 0)
            self._refresh_notif_win()

        # Audio notif
        if msg['pseudo'].lower() != self.pseudo.lower() and not msg.get('old'):
            if msg['message'].lower().find('@' + self.pseudo.lower()) != -1:
                self.sounds['nomi'].play()
            elif self.sound_on and self.chat_sound[chat]:
                if chat == 'main':
                    self.sounds['msg'].play()
                else:
                    self.sounds['mp'].play()

    def on_kick(self, msg):
        self._log(str(msg), "KICK")
        self.typelist_win.disp("-= KICKED =-")
        sleep(KICK_TIMEOUT)
        self.typelist_win.reset()
        self._init_socket()

    def _process_message(self, msg):
        msg = msg.lstrip(' ')

        # Aliases
        for i in [ i for i in re.findall("%([^% ]+)%", msg) if i in self.alias ]:
            msg = re.sub('%' + i + '%', self.alias[i], msg)

        self.history.append(msg)
        if len(self.history) > HISTORY_SIZE:
            del self.history[0]
        self.history_pos = 0
        if msg.startswith('/'):
            try:
                if self._execute(msg):
                    return
                else:
                    self.msgsend(msg)
            except Exception as e:
                self._log(str(e), "Error")
            return
        if self.cur_chat == 0:
            self.msgsend(msg)
        else:
            self.pmsend(self.chat_list[self.cur_chat], msg)

    def _execute(self, msg):
        commands = {
                'quit'       : self._quit,
                'quiet'      : lambda : self._set_sound(False),
                'unquiet'    : lambda : self._set_sound(True),
                'player'     : self._set_player,
                'mute'       : lambda : self._set_chat_sound(False),
                'unmute'     : lambda : self._set_chat_sound(True),
                'volume'     : self._set_player_volume,
                'alias'      : self._set_alias,
                'unalias'    : self._del_alias,
                'list'       : lambda : self._show_message(", ".join([ "%s(%d)" % (c, i) for (i, c) in enumerate(self.chat_list) ])),
                'chat'       : self._change_chat,
                'reconnect'  : self._init_socket,
                'loadhist'   : self._load_full_history,
                }
        cmd, *args  = msg[1:].split(' ')
        if cmd in commands:
            commands[cmd](*args)
            return(True)
        return(False)

    def _handle_spec_key(self, key):
        keys = {
                curses.KEY_PPAGE : lambda : self.chat_win.change_offset(-4),
                curses.KEY_NPAGE : lambda : self.chat_win.change_offset(4),
                curses.KEY_HOME  : lambda : self.chat_win.change_offset(0, True),
                curses.KEY_END   : lambda : self.chat_win.change_offset(-1, True),
                'CTRL_N'         : lambda : change_chat(1),
                'CTRL_P'         : lambda : change_chat(-1),
                curses.KEY_UP    : lambda : self._get_history(-1),
                curses.KEY_DOWN  : lambda : self._get_history(1),
                'CTRL_I'         : lambda : autocomplete(),
                'CTRL_L'         : self._get_previous_link,
                'CTRL_O'         : self._open_link,
                'CTRL_R'         : self._reset_link_browsing,
                }

        def move_cursor(move):
            if move:
                self.input_win.buff_pos
            else:
                self.input_win.buff_pos = self.cusor_pos = 0

        def change_chat(shift):
            chat_num = (self.cur_chat + shift) % len(self.chat_list)
            self._change_chat(self.chat_list[chat_num])
            self._reset_link_browsing()

        def autocomplete():
            text = self.input_win.input_buff
            if not text:
                return
            words = list(re.finditer('[^ ,.;:@]+', text))
            selected_words = [ w for w in words if w.start() <= self.input_win.buff_pos <= w.end() ]
            if not selected_words:
                return
            selected_word = selected_words[0]

            if self.complete[1] == selected_word.group():
                prefix = self.complete[0]
                cplt_offset = (self.complete[2] + 1)
            else:
                prefix = selected_word.group()
                cplt_offset = 0

            potential_words = [ c for c in self.clients + ["main"] if c.lower().startswith(prefix.lower()) ]
            if not potential_words:
                return
            cplt_offset %= len(potential_words)
            chosen_word = potential_words[cplt_offset]

            self.complete = (prefix, chosen_word, cplt_offset)

            final_text = text[:selected_word.start()] + chosen_word + text[selected_word.end():]
            self.input_win.set_content(final_text, selected_word.start() + len(chosen_word))
            self.input_win.refresh()

        if key in keys:
            keys[key]()
        else:
            self._log(str(key), "KEY")

    def _change_chat(self, chat_name):
        chat_name = chat_name.lower()
        try:
            chat_num = self.chat_list.index(chat_name)
        except ValueError:
            return
        if chat_num != self.cur_chat:
            self.cur_chat          = chat_num
            self.chat_win.offset   = 0
            self.chat_win.raw_hist = self.raw_msg_hist[chat_name][-CHAT_BUFF_SIZE:]
            self.chat_win.reload_history()
            self.chat_win.refresh()
            if chat_name in self.unread:
                del self.unread[chat_name]
            self._set_title()
            self._refresh_notif_win()

    def _get_previous_link(self):
        """ Selects the previous link in the current message history and
        highlights and stores it
        """
        if self.selected_link:
            rh = self.chat_win.raw_hist[:self.selected_link["msg_num"]] + [ self.chat_win.raw_hist[self.selected_link["msg_num"]][:self.selected_link["begin"]] ]
        else:
            rh = self.chat_win.raw_hist

        for num in range(len(rh) - 1, -1, -1):
            scan = re.match("^.*(https?://[^: ]+).*?$", rh[num])
            if scan:
                self.selected_link = {
                    'msg_num' : num,
                    'begin'   : scan.span(1)[0],
                    'text'    : scan.group(1),
                }
                self.link_win.disp(scan.group(1))
                return

    def _open_link(self):
        """ Opens link selected with _get_previous_link """
        if webbrowser and self.selected_link:
            webbrowser.open(self.selected_link['text'])

    def _reset_link_browsing(self):
        """ Unselect selected link and returns to its "zero".
        Next link returned by _get_previous_link will be the most recent
        """
        self.selected_link = {}
        self.link_win.reset()

    def _refresh_notif_win(self):
        if self.unread:
            self.notif_win.disp(', '.join([ '%s(%d)' % (k, v) for (k, v) in self.unread.items() ]))
        else:
            self.notif_win.reset()

    def _set_title(self):
        self.title_win.set_title("SkyCurses, the official curses SkyChat Client (%s) " % (self.chat_list[self.cur_chat]) + ("(Mute)" if not (self.sound_on and self.chat_sound[self.chat_list[self.cur_chat]]) else ""))

    def _set_sound(self, val):
        self.sound_on = val
        self._set_title()

    def _set_player(self, val):
        if not MPLAYER_ENABLED:
            return
        if type(val) == str:
            val = True if val.lower() == 'on' else False
        if val != self.player_on:
            self.player_on = val
            if not val:
                self.player.stop()
                self.current_vid = ""
                self.player_win.set_title(PLAYER_SYMBOLS['off'][self.UTF8_ENABLED])
            else:
                self.player_win.set_title(PLAYER_SYMBOLS['stop'][self.UTF8_ENABLED])
                self.msgsend("/yt sync")

    def _set_player_volume(self, vol):
        if MPLAYER_ENABLED:
            self.player.volume = float(vol)

    def _set_chat_sound(self, val):
        self.chat_sound[self.chat_list[self.cur_chat]] = val
        self._set_title()

    def _get_player_pos(self):
        if not MPLAYER_ENABLED:
            return(0)
        pos    = self.player.time_pos
        length = self.player.length
        if pos != None and length != None:
            return(pos / length if pos < length else 1)
        return(0)

    def _set_alias(self, name, *value):
        self.alias[name] = ' '.join(value)

    def _del_alias(self, name):
        del self.alias[name]

    def _load_full_history(self):
        self.chat_win.raw_hist = self.raw_msg_hist[self.chat_list[self.cur_chat]]
        self.chat_win.reload_history()
        self.chat_win.refresh()

    def _get_history(self, delta):
        self.history_pos += delta
        if self.history_pos > 0:
            self.history_pos = 0
        elif -self.history_pos > len(self.history):
            self.history_pos = - len(self.history)

        self.input_win.set_content(self.history[self.history_pos] if self.history_pos else "")
        self.input_win.refresh()

    def _full_path(self, path):
        return(os.path.join(os.path.dirname(os.path.realpath(__file__)), path))

    def _get_user_path(self, path):
        user_dir = os.path.join(os.path.expanduser('~'), CONFIG_DIR)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return(os.path.join(user_dir, path))

    def _log(self, text, level="Warning"):
        text = text.replace("\n", " ")
        self._disp_msg({'message' : text, 'pseudo' : level, 'pseudo_html' : level, 'id' : 0, 'old' : True}, "log")

    def _show_message(self, text):
        self._disp_msg({'message' : text, 'pseudo' : '\\>\\>\\>', 'pseudo_html' : '\\>\\>\\>', 'id' : 0}, "main")

    def _load(self):
        with open(self._full_path('alias.json'), 'r') as f:
            self.alias = json.load(f)
        try:
            with open(self._get_user_path('alias.json'), 'r') as f:
                for (k, v) in { k : v for (k, v) in json.load(f).items() if k not in self.alias }.items():
                    self.alias[k] = v
        except FileNotFoundError:
            pass

    def _save(self):
        with open(self._get_user_path('alias.json'), 'w') as f:
            json.dump(self.alias, f)

    def _quit(self):
        self.sock.disconnect()
        curses.endwin()
        MPLAYER_ENABLED and self.player.quit()
        self._save()
        self.sounds['end'].play_wait()
        for s in self.sounds.values():
            s.close()
        os.kill(os.getpid(), signal.SIGKILL)
        exit(0)


def main():
    if 2 < len(argv) < 6:
        sc = SkyCurses(*argv[1:])
        sc.run()
    else:
        print("Usage : %s <username> <password> [room [room_pw]]" % (argv[0]))


if __name__ == "__main__":
    main()
