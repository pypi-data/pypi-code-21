import pyotp
import time
import xerox as clipboard


class KeyringOTP():

    def __init__(self, secret, console_output=False, run_duration=30):
        self.secret = secret
        self.console_output = console_output
        self.run_duration = run_duration

    def run(self):
        if not self.console_output:
            original_clipboard_content = clipboard.paste()
        totp = pyotp.TOTP(self.secret)
        previous_password = ""
        start_time = time.time()
        try:
            while time.time() - start_time < self.run_duration:
                password = totp.now()
                if previous_password != password:
                    if self.console_output:
                        previous_password = password
                        print(
                            "Current TOTP {} at {}".format(
                                password, time.ctime())
                        )
                    else:
                        clipboard.copy(password)
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            if not self.console_output:
                clipboard.copy(original_clipboard_content)
