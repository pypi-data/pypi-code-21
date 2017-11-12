"""Simple shell interface for Paramiko"""
import codecs
import re
import socket
import sys
if sys.version_info > (3,):
    long = int
#
from paramiko.channel import Channel as ParamikoChannel
#
from .exception import PromptError, RecvError, ResponseError
from .prompt import ShellPrompt

def debug(func):
    def func_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        hex_result = ''
        if isinstance(result, str):
            hex_result = codecs.encode(result.encode(), 'hex')
        elif isinstance(result, list):
            if len(result) == 1 and isinstance(result[0], str):
                hex_result = result[0].encode('hex')
        sys.stderr.write(
            'DEBUG: {}({}, {}) = [{}][{}]\n'.format(
                func.__name__,
                args,
                kwargs,
                result,
                hex_result
            )
        )
        return result
    return func_wrapper


class Shell(object):
    """Shell class over Paramiko Channel"""
    def __del__(self):
        self.exit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.exit()

    def __init__(self, paramiko_channel, shell_prompt, **kwargs):
        assert isinstance(paramiko_channel, ParamikoChannel)
        assert isinstance(shell_prompt, ShellPrompt)

        self.paramiko_channel = paramiko_channel
        self.shell_prompt = shell_prompt

        self.paramiko_channel.settimeout(kwargs.get('timeout', 0.2))
        self.paramiko_channel.set_combine_stderr(kwargs.get('combine_stderr', False))
        self.paramiko_channel.get_pty(
            term=kwargs.get('terminal_type', 'dumb'),
            width=kwargs.get('terminal_width', 80),
            height=kwargs.get('terminal_height', 25)
        )
        self.paramiko_channel.invoke_shell()

        self.ansi_escape_code_regexp = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        self.exit_command = kwargs.get('exit_command', 'exit')
        self.last_prompt = ''
        self.line_separator = kwargs.get('line_separator', '\n').encode()
        self.recv_bufsize = kwargs.get('recv_buffer_size', 4096)

        banner, retries_left = self.read_until_prompt()
        if retries_left == 0:
            if len(banner) == 0:
                raise PromptError('Cannot auto-detect prompt')
            timeout_prompt = banner.pop()
            self.shell_prompt.add_prompt(timeout_prompt)
            self.command('\n', 5)
        self.on_banner(banner)

        for command in kwargs.get('initial_commands', []):
            self.command(command)

    def __repr__(self):
        return 'Shell @ {} ({})'.format(
#            hex(long(id(self)) & long(0xffffffff)),
            hex(id(self) & 0xffffffff),
            repr(self.paramiko_channel)
        )

    def command(self, command, timeout_retries=40):
        send_command = command.rstrip('\r\n')
        if self.paramiko_channel.recv_ready():
            # Flush buffer before sending command
            self.paramiko_channel.recv(self.recv_bufsize)
        self.paramiko_channel.sendall(send_command + '\r')
        output, retries_left = self.read_until_prompt(timeout_retries)
        if len(output) == 0:
            raise ResponseError('Command not echoed')
        if output[0] != send_command:
            raise ResponseError('Command echo mismatch')
        if timeout_retries != 0 and retries_left == 0:
            raise PromptError('Prompt not seen')
        output.pop(0)
        return output

    def exit(self, exit_command=None):
        if exit_command is None:
            exit_command = self.exit_command
        if hasattr(self, 'paramiko_channel'):
            if self.paramiko_channel.get_transport().is_active():
                self.paramiko_channel.send(exit_command)
                self.paramiko_channel.shutdown(2)
                self.paramiko_channel.close()
            del self.paramiko_channel

    @classmethod
    def from_transport(cls, paramiko_transport, shell_prompt=None, **kwargs):
        if shell_prompt is None:
            shell_prompt = ShellPrompt()
        return cls(paramiko_transport.open_session(), shell_prompt, **kwargs)

    def on_banner(self, banner):
        """Override to do something with the banner"""
        pass

    def on_prompt(self, prompt):
        """Override to do something with each prompt"""
        self.last_prompt = prompt

    def read_until_prompt(self, timeout_retries=25):
        """Read from channel until prompt is seen"""
        read_buffer = b''
        separator_rfind_start = 0
        while timeout_retries > 0:
            if self.paramiko_channel.exit_status_ready():
                break
            if self.paramiko_channel.recv_ready():
                recv_bytes = self.paramiko_channel.recv(self.recv_bufsize)
            else:
                try:
                    recv_bytes = self.paramiko_channel.recv(self.recv_bufsize)
                except socket.timeout:
                    timeout_retries -= 1
                    continue
            if len(recv_bytes) == 0:
                raise RecvError('Channel closed during recv()')
            read_buffer += recv_bytes
            separator_position = read_buffer.rfind(self.line_separator, separator_rfind_start)
            if separator_position != -1:
                separator_rfind_start = separator_position
                candidate_prompt = self.tidy_output_line(read_buffer[separator_position + 1:])
                if self.shell_prompt.is_prompt(candidate_prompt):
                    self.on_prompt(candidate_prompt)
                    read_buffer = read_buffer[:separator_position]
                    break
        output = []
        for raw_output in read_buffer.split(self.line_separator):
            output_line = self.tidy_output_line(raw_output)
            if self.shell_prompt.is_prompt(output_line):
                raise PromptError('Unexpected prompt')
            output.append(output_line)
        return (output, timeout_retries)

    def tidy_output_line(self, output_line):
        """Override to remove device specific cruft"""
        return self.ansi_escape_code_regexp.sub('', output_line.decode()).strip('\r')
