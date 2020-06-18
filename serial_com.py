#!/usr/bin/env python
"""
Provide serial port communication
"""
__author__ = 'John Stile'

import sys  # for sys.platform (detect os)
import glob  # to find serial port name
import re  # matching with pexpect
import serial  # to talk to serial port
import pexpect.fdpexpect  # use expect on the serial object
import pexpect  # to access enums
import logging  # for log facility
import unicodedata  # for filtering out terminal formatting chars


def _write(*args):
    """Called by the pexpect object to log"""
    content = args[0]
    # Ignore other params, pexpect only use one arg
    if content in [' ', '', '\n', '\r', '\r\n']:
        return  # don't log empty lines
    for eol in ['\r\n', '\r', '\n']:
        # remove ending EOL, the logger will add it anyway
        content = re.sub(r'{}$'.format(eol), '', content)
    return logging.info(content)  # call the logger info method with the reworked content


# our flush method
def _do_nothing():
    pass


class SerialCom(object):
    """Communicate to a remote host over serial
    Using pyserial for access to the serial port
    Using fdpexpect to handle communication decisions
    Using logging.logger to record serial port output
    """

    def __init__(
            self,
            port=None,
            baudrate=115200,
            timeout=None,
            logger=None,
            debug=False
    ):
        self.debug = debug  # print extra stuff
        self.com = None
        self.logger = logger or logging.getLogger('default-logger')

        # Extend logging such that pexpect can use it
        self.logger.write = self.pexpect_write
        self.logger.flush = self.pexpect_flush

        # Buffer to aggregate chunks read by pexpect from the serial console.
        self.console_chunk_buffer = b""

        self.baudrate = baudrate
        self.timeout = timeout
        self.p_expect = None

        if self.debug:
            # On debug, list the serial ports
            self.list_serial_ports

        if port is not None:
            self.logger.info("Using port: {}".format(port))
            self.port = port
        else:
            self.logger.debug("Find serial port")
            # List everything
            port_list = self.list_serial_ports
            self.logger.debug("ports: {}".format(port_list))
            # Modern way of finding first available port
            try:
                first_serial_device = serial.serial_for_url('hwgrep://.*&skip_busy')
            except serial.serialutil.SerialException as e:
                self.logger.critical("***Check cables: Serial Not found***")
                raise e
            self.port = first_serial_device.port
            self.logger.debug("Using port: {}".format(self.port))
            # Old way of finding port
            if not self.port:
                port_re = re.compile('.*(USB|COM).*')
                for i in port_list:
                    self.logger.debug("Using port: {}".format(i))
                    if re.match(port_re, i):
                        self.port = i
                        break

    @property
    def list_serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM{}'.format(i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def init_com(self):
        """Create serial object, but don't attache to the port"""
        self.logger.debug("Call init_com()")

        serial_url = r'spy://{}?color=True&raw=True&all=True'.format(self.port)
        self.logger.debug('serial_url:{}'.format(serial_url))
        # Attach to serial port
        self.com = serial.serial_for_url(
            serial_url,
            baudrate=self.baudrate,
            timeout=self.timeout,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            rtscts=False
        )

        # # Attach to Quatech serial port
        # self.conn = serial.serial_for_url(
        #     'intellisock://192.168.60.107:5000',
        #     port = '/dev/ttyUSB0',
        #     baudrate =115200,
        #     rtscts = False,
        #     dsrdtr = False,
        #     xonxoff = False,
        #     do_not_open=True,
        #     timeout=60,
        # )

        # As pexpect collects data, send to stdout or logger
        self.p_expect = pexpect.fdpexpect.fdspawn(self.com, logfile=self.logger)
        if not self.p_expect.isalive():
            raise Exception("Bad file descriptor")

    def close(self):
        """Detach serial port"""
        self.logger.debug("Call close()")
        if self.p_expect:
            self.p_expect.close()
        if self.com and self.com.is_open():
            self.com.close()

    def logout(self):
        """Logout connections, and do cleanup"""
        self.logger.debug("Call logout()")
        self.logger.debug("Send logout (ctrl-d)")
        self.p_expect.sendline('\x04')

    def send_null(self):
        """force login message by sending newline"""

        self.init_com()

        if not self.p_expect:
            self.p_expect = pexpect.fdpexpect.fdspawn(self.com, logfile=self.logger)
        self.p_expect.sendline('\0')

    def login(self):
        """Login to the getty on the serial port"""
        self.logger.debug("Call login()")

        username = 'pi'
        password = 'raspberry'
        retry = 5

        # force login message by sending newline
        self.p_expect.sendline('\n')

        # Pexpect Pattern List:
        pattern_list = [r"login: $", r"Password:", r"root.*[#]"]
        compiled_pattern_list = self.p_expect.compile_pattern_list(pattern_list)

        # Loop through log-in conversation until we get the prompt
        self.logger.debug("Begin Conversation")
        while True:
            # Matched index in pattern_list
            index = self.p_expect.expect_list(compiled_pattern_list)

            # We retry 5 times and then give up 
            if retry <= 0:
                raise Exception("Can't Log in")
            retry -= 1

            # Check for match
            if index == 0:
                self.logger.info("Send login username")
                self.p_expect.sendline(username)
            elif index == 1:
                self.logger.info("Send login passwd")
                self.p_expect.sendline(password)
                self.p_expect.sendline('\n')
            elif index == 2:
                self.logger.info("Got shell prompt")
                break
        self.logger.info("End Conversation")

    def run(self, cmd):
        """Issue a command and wait for command prompt
        :param cmd: Command to run
        """
        self.logger.debug("Call run(cmd):{}".format(cmd))
        exit_status = 0

        # Send the command
        self.p_expect.sendline(cmd)

        # Wait for output, look for cmd prompt, return what is before it.
        index = self.p_expect.expect([r"\r\nroot.*[#\$] ", pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            lines = self.p_expect.before
            self.logger.info("Show lines before match:.{}".format(lines))
        elif index == 1:
            lines = "EOF"
        elif index == 2:
            lines = "TIMEOUT"
        else:
            lines = ''

        return exit_status, lines

    def read_until(self, stop_string=None, read_again_limit=120):
        """Read data from the serial port, stop when we see stop_string.
        :param stop_string: terminate read when string is found.
        :param read_again_limit: Allow this many timeouts before giving up
        :return Ture if stop_string found, False if read_again_limit reached
        """

        self.logger.debug(
            (
                "Call read_until(stop_string:{}, read_again_limit:{}"
            ).format(
                stop_string,
                read_again_limit
            )
        )
        result = False
        read_again = True
        read_again_counter = 0

        # spinner = self.spinning_cursor()

        while read_again:

            if not self.com.readable():
                self.logger.debug("not readable")
                read_again = False

            # FIX LATER: This is delaying serial port buffer until it is full.
            # # Spin the spinner
            # for _ in range(8):
            #     sys.stdout.write(spinner.next())
            #     sys.stdout.flush()
            #     time.sleep(0.01)
            #     sys.stdout.write('\b')

            # This will be the matched element in the list passed to .expect()
            # First element is our stop_string is our pattern
            # Second element is hit if nothing matches an expected pattern after a time, we keep a counter
            # Third element is hit if the child died and all output has been read.
            matches = [pexpect.TIMEOUT, pexpect.EOF]
            if isinstance(stop_string, str):
                matches.append(stop_string)
            else:
                matches.extend(stop_string)

            i = self.p_expect.expect(matches, timeout=1)
            if i == 0:
                # On Timeout: increment
                read_again_counter += 1
            elif i == 1:
                # On EOF: Let user know of problem
                self.logger.error("Serial disconnected, or port in use by another program.")
                raise Exception("Serial disconnected, or port in use by another program.")
            elif i > 1:
                found_stop = matches[i]
                self.logger.debug("On stop_string match: end while loop. mach:{}".format(found_stop))
                read_again = False
                result = True
            # give up at the retry limit
            if read_again_counter >= read_again_limit:
                self.logger.error("Retry Limit Exceeded! Giving up, Moving on.")
                read_again = False

        return result

    def pexpect_write(self, *args):
        """write method used by pexpect to writes to logging.logger"""

        #
        # pexpect reads in small chunks
        # group chunks into one buffer
        #
        self.console_chunk_buffer += args[0]
        #
        # split the buffer based on CR+LF
        #
        lines_buffer = self.console_chunk_buffer.split(b"\r\n")

        #
        # Read up to the last line, writing to the logger
        # INFO SHOWS WHAT CAME OVER THE SERIAL PORT
        #
        for lines in lines_buffer[:-1]:
            # Some output has \r or \r\n which does not display corectly.
            if (b'\n' in lines) or (b'\r' in lines):
                lines = lines.replace(b'\r', b'\n').replace(b'\n\n', b'\n')
                for line in lines.split(b'\n'):
                    l_strip = self.remove_control_characters(line)
                    if l_strip:
                        self.logger.info("{}".format(l_strip))
            else:
                l_strip = self.remove_control_characters(lines)
                if l_strip:
                    self.logger.info("{}".format(l_strip))

        # last element is partial line
        self.console_chunk_buffer = lines_buffer[-1]

    def pexpect_flush(self):
        """Flush method called by pexpect does nothing"""
        pass

    @staticmethod
    def remove_control_characters(s):
        """Should filter unprintable control characters
        :param s: string literal
        :return: string
        """
        s = str(s, "utf-8")
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    def spinning_cursor(self):
        """Show a spinner """
        while True:
            for cursor in '|/-\\':
                yield cursor


def login_and_run_command(s_com=None):
    """Expects a log-in prompt, and will issue commands on the shell
    :param s_com: Serial port instance"""

    # Open serial port and login to remote shell
    s_com.init_com()

    s_com.login()

    # cmd1
    cmd_hostname = 'hostname -a'
    (exit_status, _) = s_com.run(cmd_hostname)

    # cmd2
    cmd_dirlist = 'ls -laF /'
    (exit_status, _) = s_com.run(cmd_dirlist)

    # Don't Clean up
    s_com.logout()


def follow_console_until(s_com=None, stop_string=None):
    """Follow console output.  No command issued. Stop when string is read.
    :param s_com: Serial port instance
    :param stop_string: Instance of SerialCom class
    """

    s_com.init_com()

    # Not sure what to put here... read() plus some pExpect?
    s_com.read_until(stop_string=stop_string)

    s_com.logout()


def follow_until_timeout(s_com=None, stop_string=None):
    """Follow console output.  No command issued. Stop when string is read.
    :param s_com: Serial port instance
    :param stop_string: Instance of SerialCom class
    """

    s_com.init_com()

    # Not sure what to put here... read() plus some pExpect?
    s_com.read_until(stop_string=stop_string, read_again_limit=3600)


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # --------------------
    # Logging setup
    # --------------------
    log = logging.getLogger()

    # Console Handler object
    ch = logging.StreamHandler()

    # # File Handler object
    # date = strftime("%Y%m%d-%H%M%S", time.localtime())
    # log_dir = os.path.abspath('.')
    # log_file_rel = os.path.join( log_dir, "my_serial.{}.log".format(date) 
    # log_file = os.path.expanduser(log_file_rel)
    # fh = logging.FileHandler(log_file)

    # Attach handler to log instance
    log.addHandler(ch)

    # set log level
    log.setLevel(logging.DEBUG)

    # Set log formatting
    log.debug("Initialized Logger")
    # --------------------
    # Serial setup
    # --------------------
    SERIAL_PORT = '/dev/ttyUSB0'
    SERIAL_BAUD = 115200
    # SERIAL_BAUD = 9600
    SERIAL_TIMEOUT = 1

    # Create serial instance on specific interface
    s_com = SerialCom(
        port=SERIAL_PORT,
        baudrate=SERIAL_BAUD,
        timeout=SERIAL_TIMEOUT,
        logger=log,
        debug=True
    )

    # Create serial instance on auto-detected interface
    # s_com = SerialCom(baudrate=SERIAL_BAUD, timeout=SERIAL_TIMEOUT, logger=log, debug=True)

    # --------------------
    # Run the tests
    # --------------------

    # Testing system in Running mode (expects to see a login prompt
    # login_and_run_command(s_com)

    # Monitor system when booted to initialized UTP device interface
    # follow_console_until(s_com, stop_string="g_mass_storage gadget: high-speed config #1: Linux File-Backed Storage")
    follow_until_timeout(s_com, stop_string='login:')

    # # this works:
    # # ssh shell, do: for ((n=0;n<5000;n++)); do echo "${n}Foo" > /dev/ttyS0; done; echo "Done" > /dev/ttyS0
    # follow_console_until(s_com, stop_string="Done")

    # ssh shell, do: apt-get update  > /dev/ttyS0
    # follow_console_until(s_com, stop_string="Done")
