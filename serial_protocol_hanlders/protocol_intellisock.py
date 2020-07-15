#!/usr/bin/env python3
#
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# Modified from rfc2217.py which included copy write notice
# (C) 2001-2009 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt
#
# By John Stile & Alex Bellits At Meyer Sound Laboratories Inc. 
# this is distributed under a free software license, see license.txt
#
# This module implements a Intellisock compatible client. Intellisock descibes a
# protocol to access serial ports over TCP/IP and allows setting the baud rate,
# modem control lines etc.
#
# Port string is expected to be something like this:
# intellisock://host:port
# host may be an IP or including domain, whatever.
# port is 5000:5007 for 8 port device
#
"""Implementation of Intellisock protocol for pySerial.
Intellisock protocol is used by Quatech Serial device servers.
REF: "Intellisock sdk.pdf"
REF: http://pyserial.sourceforge.net/pyserial_api.html#serial.protocol_handler_packages

"""
from serial.serialutil import *
import time
import struct
import socket
import threading
import queue
import logging
import sys

#
# map log level names to constants. used in from_url()
#
LOGGER_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
}
#
# For parsing Intellisock Packets
#
M_READ_HEADER = 0
M_READ_PARAMETERS = 1
M_READ_DATA = 2
#
# For Parsing Status Insertion State Changes
#
DSTATE_READ_NORMAL = 0
DSTATE_READ_HEADER = 1
DSTATE_READ_STATUS_TYPE = 2
DSTATE_READ_REGISTER_VALUE = 3
#
# Intellisock maxiumum packet size
#
MAX_PACKET_SIZE = 1460
#
# Port range
#
PORT_RANGE = list(range(5000, 5007))


#
# Intellisock Commands for Quatech ESE-100D
#


class Command(object):
    """Command bytes in SDS Intellisock SDK
    
    """

    def __init__(self):
        pass

    # Dictionary map bytes to function
    ctrl = {
        'COMMAND_BASE': to_bytes([27, 27, 27, 0, 0, 0]),  # HEADER+RESERVED+SEQ#
        'SET_BAUD_RATE': to_bytes([66]),  # 0x42 # Set SDS baud rate
        'GET_BAUD_RATE': to_bytes([98]),  # 0x62 # Get SDS baud rate
        'HW_FLW_CTRL': to_bytes([72]),  # 0x48 # Enable Hardware Flow ctrl
        'BREAK_CTRL': to_bytes([75]),  # 0x4B # Remove break condition
        'MODIFY_REG': to_bytes([77]),  # 0x4D # Set or Clear Registers
        'COMM_PARAM': to_bytes([80]),  # 0x50 # Word Len, Stop bits, Parity
        'SET_REG': to_bytes([82]),  # 0x52 # Set Registers
        'GET_REG': to_bytes([114]),  # 0x72 # Get Registers
        'SW_FLW_CTRL': to_bytes([83]),  # 0x53 # Enable Software flow ctrl
        'SW_FLW_DIS': to_bytes([115]),  # 0x73 # Disable Software flow ctrl
        'MX_OST_PKTS': to_bytes([65]),  # 0x41 # Max Outstatnding Pkt Count
        'PKT_ACK': to_bytes([97]),  # 0x61 # Acknowledge pkt processed
        'CLOSE': to_bytes([67]),  # 0x43 # Close UART, mark avail
        'TX_DATA': to_bytes([68]),  # 0x44 # Data + LineStat + ModemStat
        'RX_FLUSH': to_bytes([70]),  # 0x46 # Flush Receive FIFO on UART
        'TX_FLUSH': to_bytes([102]),  # 0x66 # Flush Send FIFO on UART
        'OPEN': to_bytes([79]),  # 0x4f # Opens UART, process RX/TX
        'EN_STAT_INS': to_bytes([81]),  # 0x51 # Enable Status Insertion
        'DIS_STAT_INS': to_bytes([113]),  # 0x71 # Disable Status Insertion
        'TX_IMMEDIATE': to_bytes([84]),  # 0x54 # Send Char, Bypass Pueue
        'DIS_HEART': to_bytes([120]),  # 0x78 # Disable Heartbeat Timer.
        'CON_CHK': to_bytes([63]),  # 0x3f # SDS verify connection
        'DEV_INFO': to_bytes([73]),  # 0x49 # Info (HW,FW-major,FW-minor)
        'DEST_PORT': to_bytes([00])  # 0x00 # Destination port Unused
    }


class IntellisockSerial(SerialBase):
    """Serial port implementation for Intellisock remote serial ports."""

    #
    # Supported baudrates
    #
    BAUDRATES = (
        300, 600, 1200, 1800, 2400, 4800,
        9600, 14400, 19200, 38400, 57600,
        115200, 230400, 460800, 921600
    )

    #
    # Create instance of class that contains commands
    #
    com = Command
    #
    # Sequence number incrments for data packets
    #
    packet_sequence_num = 0

    def __init__(self, *args, **kwargs):
        super(IntellisockSerial, self).__init__(*args, **kwargs)
        self._socket = None
        self.logger = None
        self._network_timeout = 3
        self._read_buffer = None
        self._write_lock = None
        self._thread = None

    def open(self):
        """Open port with current settings. This may throw a SerialException
           if the port cannot be opened.
           
        """
        if self._port is None:
            raise SerialException(
                "Port must be configured before it can be used."
            )
        if self.is_open:
            raise SerialException("Port is already open.")
        try:
            if self.logger:
                self.logger.debug("Opening socket")
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect(self.from_url(self.portstr))
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception as msg:
            raise SerialException(
                "Could not open port {}: {}".format(self.portstr, msg)
            )
        self._socket.settimeout(self._network_timeout)

        if self.logger:
            self.logger.info("Creating Queue")

        #
        # use a thread save queue as buffer. it also simplifies implementing
        # the read timeout
        #
        self._read_buffer = queue.Queue()
        #
        # to ensure that user writes does not interfere with internal
        # intellisock options establish a lock
        #
        self._write_lock = threading.Lock()
        #
        # Create thread for each self._intellisock_read_loop
        #
        if self.logger:
            self.logger.info(
                'pySerial Intellisock reader thread for {}'.format(self._port,)
            )
        self._thread = threading.Thread(target=self._intellisock_read_loop)
        self._thread.setDaemon(True)
        self._thread.setName(
            'pySerial Intellisock reader thread for {}'.format(self._port,)
        )
        self._thread.start()
        #
        # Configure serial port and open
        #
        self._reconfigure_port()
        #
        # all things set up get, now a clean start
        #
        self.is_open = True
        if not self._rtscts:
            self.setRTS(True)
            self.setDTR(True)
        self.flushInput()
        self.flushOutput()

    def _reconfigure_port(self):
        """Set communication parameters before opening port."""

        if self._socket is None:
            raise SerialException("Can only operate on open ports")

        # if self._writeTimeout is not None:
        #    raise NotImplementedError('writeTimeout is currently not supported')
        # ----------------------------------------------------------------------
        #
        # Diagnostic Device information
        #
        '''
        if self.logger:
            self.logger.info("Diagnostic Device information")
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['DEV_INFO']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00' # Data size
        )
        '''
        # ----------------------------------------------------------------------
        #
        # Connection Integrity Check
        #
        '''
        if self.logger:
            self.logger.info("Connection Integrity Check")
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['CON_CHK']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00' # Data size
        )
        '''
        # ----------------------------------------------------------------------
        #
        # Disable Heartbeat Timer
        #
        if self.logger:
            self.logger.info("Disable Heartbeat Timer")
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['DIS_HEART']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00'  # Data size
        )
        # ----------------------------------------------------------------------
        #
        # Enable/Disable Status Insertion Cmd
        #
        '''
        if self.logger:
            self.logger.info( "Enable/Disable Status Insertion Cmd" )
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['EN_STAT_INS']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00' # Data size
        )
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['DIS_STAT_INS']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00' # Data size
        )
        '''
        # ----------------------------------------------------------------------
        #
        # Baudrate (default 115200)
        #
        if self.logger:
            self.logger.info("Set Baudrate")
        if not isinstance(self._baudrate, int) \
                or not 0 < self._baudrate < 2 ** 32:
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['SET_BAUD_RATE']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x04'  # Data size
                + struct.pack("!I", str('115200'))
            )
            time.sleep(10)
        else:
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['SET_BAUD_RATE']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x04'  # Data size
                + struct.pack("!I", self._baudrate)
            )
        # ----------------------------------------------------------------------
        #
        # Comm Parameters
        #

        #
        # Odd = 2, Even = 1, No = 0
        #
        if self._parity == "O" or self._parity == "o":
            parity = 2
        elif self._parity == "E" or self._parity == "e":
            parity = 1
        else:
            parity = 0
        #
        # Word length can be 5 through 8, default 8
        #
        if not 5 <= self._bytesize <= 8:
            word_size = 8
        else:
            word_size = self._bytesize
        #
        # Stop bits can be 0 or 1 
        #
        if self._stopbits == 1:
            stop_bits = 0
        else:
            stop_bits = 1
        if self.logger:
            self.logger.info("Set comm Parameters")
        #
        # Send Comm Paratmeters
        #
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['COMM_PARAM']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x03'  # Data size
            + struct.pack("!B B B", parity, word_size, stop_bits)
        )
        # ----------------------------------------------------------------------
        #
        # Enable software flow control
        #
        if self._xonxoff:
            if self.logger:
                self.logger.info("Enable software flow control")
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['SW_FLW_CTRL']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x03'  # Data size
                + '\x13'  # XOFF Char
                + '\x11'  # XOn Char
                + '\x00'  # 0=keep char/1-remove char
            )
            # time.sleep(10)
        else:
            if self.logger:
                self.logger.info("Disable software flow control")
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['SW_FLW_DIS']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x00'  # Data size
            )
        # ----------------------------------------------------------------------
        #
        # Enable Hardware flow control RTS/CTS  vs. DTR/DSR
        #
        if self._rtscts:
            if self.logger:
                self.logger.info("Enable Hardware flow control RTS/CTS")
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['HW_FLW_CTRL']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x02'  # Data size
                + '\x10'  # Modem Stat Reg (DSR=20,CTS=10,CD=00)
                + '\x02'  # Modem Ctrl Reg (RTS=02,DTR=01)
            )
            # time.sleep(10)
        if self._dsrdtr:
            if self.logger:
                self.logger.info("Enable Hardware flow control DTR/DSR")
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['HW_FLW_CTRL']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x02'  # Data size
                + '\x20'  # Modem Stat Reg (DSR=20,CTS=10,CD=00)
                + '\x01'  # Modem Ctrl Reg (RTS=02,DTR=01)
            )
        # ----------------------------------------------------------------------
        #
        # Send Open Cmd - After all port settings 
        #
        if self.logger:
            self.logger.info("Send Open Cmd - After all port settings")
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['OPEN']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x05'  # Data size
            + '\x00'  # Current LSR
            + '\x00'  # Current MSR
            + '\x00'  # 1=acquared,2=failed
            + '\x00\x00'  # heartbeat (0x0000 to 0xFFFE)
        )

    def close(self):
        """Close port"""
        if self.is_open:
            if self._socket:
                try:
                    if self.logger:
                        self.logger.info("Send Close to SDS")
                    # send intellsock serail port close to Quatech SDS
                    self._socket.sendall(
                        self.com.ctrl['COMMAND_BASE']
                        + self.com.ctrl['CLOSE']
                        + self.com.ctrl['DEST_PORT']
                        + '\x00\x00'  # Data size
                    )
                    # close socket
                    self._socket.shutdown(socket.SHUT_RDWR)
                    self._socket.close()
                except socket.errno as e:
                    self.logger.critical("Close Error: {}".format(e))

                self._socket = None

            if self._thread:
                self._thread.join()
            self.is_open = False
            # in case of quick reconnects, give the server some time
            time.sleep(0.3)

    def from_url(self, url):
        """extract host and port from an URL string"""
        if url.lower().startswith("intellisock://"):
            url = url[14:]
        try:
            # is there a "path" (our options)?
            if '/' in url:
                # cut away options
                url, options = url.split('/', 1)
                # process options now, directly altering self
                for option in options.split('/'):
                    if '=' in option:
                        option, value = option.split('=', 1)
                    else:
                        value = None
                    if option == 'logging':
                        logging.basicConfig()
                        self.logger = logging.getLogger('pySerial.intellisock')
                        self.logger.setLevel(LOGGER_LEVELS[value])
                        self.logger.info('enabled logging')
                    elif option == 'timeout':
                        self._network_timeout = float(value)
                    else:
                        raise ValueError('unknown option: %r' % (option,))
            # get host and port
            host, port = url.split(':', 1)
            port = int(port)
            if port not in PORT_RANGE:
                raise ValueError(
                    "port not in range {}...{}".format(PORT_RANGE[0], PORT_RANGE[-1])
                )
        except ValueError as e:
            raise SerialException(
                'expected a string in the form \
                "[intellisock://]<host>:<port>[/option[/option...]]": {}'.format(e)
            )
        return host, port

    @property
    def in_waiting(self):
        """Return the number of characters currently in the input buffer."""
        if not self.is_open:
            raise portNotOpenError
        return self._read_buffer.qsize()

    def read(self, size=1):
        """Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read."""
        if not self.is_open:
            raise portNotOpenError
        data = bytearray()
        try:
            while len(data) < size:
                if self._thread is None:
                    raise SerialException(
                        'connection failed (reader thread died)')
                data.append(self._read_buffer.get(True, self._timeout))
        except queue.Empty:  # -> timeout
            pass
        return bytes(data)

    def write(self, data):
        """Output the given string over the serial port. Can block if the
        connection is blocked. May raise SerialException if the connection is
        closed."""
        #
        # Size of the packet header
        #
        header_len = 10
        #
        # In data Recived from SDS, '\x1B\x1B' reserved for status change,
        # however transmitted data uses no such mechanism
        # Don't substitute data in sending packet.
        # data.replace('\x1B\x1B', '\x1B\x1B\xFF')
        #
        # Check if we can wirte
        #        
        if not self.is_open:
            raise portNotOpenError
        self._write_lock.acquire()
        try:
            try:
                #
                # Write to socket chunks of data, with-in limit:
                # ( 10 byte header + data ) <= MAX_PACKET_SIZE
                # after writing chunck, slice off
                #
                while len(data):
                    #
                    #  Faster method to got largest chunck
                    # 
                    if header_len + len(data) < MAX_PACKET_SIZE:
                        position = len(data)
                    else:
                        position = MAX_PACKET_SIZE - header_len
                    #
                    # Line to be sent 
                    #
                    line = data[:position]
                    #
                    # Cut line off processed data
                    #
                    data = data[position:]
                    #
                    # Increment sequence number 0 to 0xFFFF
                    #
                    self.packet_sequence_num += 1
                    if self.packet_sequence_num >= 0xFFFF:
                        self.packet_sequence_num = 0
                    #
                    # Make note in log
                    #
                    if self.logger:
                        self.logger.info(
                            (
                                "Writing to SDS: sequence:{} size:{} data:{}"
                            ).format(
                                self.packet_sequence_num,
                                position,
                                line,
                            )
                        )
                    #
                    # Send message
                    #
                    self._socket.sendall(
                        '\x1B\x1B\x1B'  # Header
                        '\x00'  # Reseverd
                        + struct.pack('!H', self.packet_sequence_num)
                        + self.com.ctrl['TX_DATA']
                        + self.com.ctrl['DEST_PORT']
                        + struct.pack('!H', len(line))  # Data size
                        + line
                    )

            except socket.error as e:
                # Rais SerialException if conneciton fails,
                # so that caller can catch the exception
                raise SerialException(
                    "connection failed (socket error): {}".format(e)
                )
        finally:
            self._write_lock.release()
        return len(data)

    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if self.logger:
            self.logger.info("Send RX_FLUSH")
        if not self.is_open:
            raise portNotOpenError
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['RX_FLUSH']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00'  # Data Size
        )
        # empty read buffer
        while self._read_buffer.qsize():
            self._read_buffer.get(False)

    def reset_output_buffer(self):
        """Clear output buffer, aborting the current output and
        discarding all that is in the buffer."""
        if self.logger:
            self.logger.info("Send TX_FLUSH")
        if not self.is_open:
            raise portNotOpenError
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['TX_FLUSH']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x00'  # Data Size
        )

    def send_immediate(self, byte=None):
        """Transmit given character, bypassing queue
        
        """
        if self.logger:
            self.logger.info("Send TX_IMMEDIATE")
        if not self.is_open:
            raise portNotOpenError
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['TX_IMMEDIATE']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x01'  # Data Size
            + struct.pack("!B", byte)
        )

    def send_ack(self, sequence=None, size=None):
        """Send acknowledgement that packets have been processed.
        
        """
        if self.logger:
            self.logger.info("Send PKT_ACK")
        if not self.is_open:
            raise portNotOpenError
        if (sequence is not None) and (size is not None):
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['PKT_ACK']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x04'  # Data Size
                + struct.pack('!H', sequence)
                + struct.pack('!H', size)
            )

    def send_con_check(self):
        """Connection Integrity Check
        """
        # Can be seent to refresh Heartbeat timer
        # restarts heartbeat timer.
        if self.logger:
            self.logger.info("Send CON_CHK")
        if not self.is_open:
            raise portNotOpenError
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['CON_CHK']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x04'  # Data Size
            + '\x00\x00'  # Hardware Product ID
            + '\x00'  # Firmware Major Rev
            + '\00'  # Firmware Minor Rev
        )

    def send_mopc(self):
        """Send request for Max Outstanding Packet Count
        
        """
        # The host sends MX_OST_PKTS with buffer size in 16bits.
        # The SDS responds with MX_OST_PKTS with it's buffer size in 16 bits.
        # After this, host must send PKT_ACK before this maxiumum number of
        # packets before transmission is terminated.
        #
        if self.logger:
            self.logger.info("Send Request for Max Outstanding Packet Count")
        self._socket.sendall(
            self.com.ctrl['COMMAND_BASE']
            + self.com.ctrl['MX_OST_PKTS']
            + self.com.ctrl['DEST_PORT']
            + '\x00\x04'  # Data size
            + '\x00\x00'  # host
        )

    def send_break(self, duration=0.25):
        """Send break condition. Timed, returns to idle state after given
        duration."""
        if not self.is_open:
            raise portNotOpenError
        self.set_break(True)
        time.sleep(duration)
        self.set_break(False)

    def set_break(self, level=True):
        """Set break: Controls TXD. When active, to transmitting is
        possible."""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info(
                (
                    'set BREAK to {}'
                ).format(
                    ('inactive', 'active')[bool(level)]
                )
            )
        if level:
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['BREAK_CTRL']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x01'  # Data Size
                + '\x01'  # 1=set, 0=clear
            )
        else:
            self._socket.sendall(
                self.com.ctrl['COMMAND_BASE']
                + self.com.ctrl['BREAK_CTRL']
                + self.com.ctrl['DEST_PORT']
                + '\x00\x01'  # Data Size
                + '\x00'  # 1=set, 0=clear
            )

    def setRTS(self, level=True):
        """Set terminal status line: Request To Send."""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info(
                (
                    'set RTS to {}'
                ).format(
                    ('inactive', 'active')[bool(level)]
                )
            )
        # xxxx Not implemented for Intellisock
        # if level:
        #    self.intellisockSetControl(SET_CONTROL_RTS_ON)
        # else:
        #    self.intellisockSetControl(SET_CONTROL_RTS_OFF)
        pass

    def setDTR(self, level=True):
        """Set terminal status line: Data Terminal Ready."""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info(
                (
                    'set DTR to {}'
                ).format(
                    ('inactive', 'active')[bool(level)]
                )
            )
        # xxxx Not implemented for Intellisock
        # if level:
        #    self.intellisockSetControl(SET_CONTROL_DTR_ON)
        # else:
        #    self.intellisockSetControl(SET_CONTROL_DTR_OFF)
        pass

    def _intellisock_read_loop(self):
        """read loop for the socket.

        This reads packets from the socket

        Data packets have a
        1. header
        2. Parameters (cmd and data-size)
        3. Data

        mode_state: is a state machine that tracks what part
        of the packet is being processed.

        Message queue can contain:
          partial message
          complete message
          multiple messages
          damaged message
        """
        mode_state = M_READ_HEADER
        data_state = DSTATE_READ_NORMAL
        header_counter = 0  # how many 1b's we have seen
        data_counter = 0  # how many bytes received
        parameters = ""  # strings are buffers
        length = 0
        sequence_num = 0

        try:
            while self._socket:
                try:
                    data = self._socket.recv(5)
                except socket.timeout:
                    # just need to get out of recv form time to time to check if
                    # still alive
                    continue
                except socket.error as e:
                    # connection fails -> terminate loop
                    if self.logger:
                        self.logger.error(
                            'socket error in reader thread: {}'.format(e)
                        )
                    break

                if not data:
                    break  # lost connection

                #
                # Parse data into messages,
                # tracking parts of message with state machine
                #
                for byte in data:
                    # print( "data {}".format(struct.unpack("!B", byte)))
                    # print( "mode {}".format(mode) )

                    #
                    # State machine mode starts at M_READ_HEADER
                    #
                    if mode_state == M_READ_HEADER:
                        #
                        # Once we see 0x1b 3 times, we parse M_READ_PARAMETERS
                        #
                        if struct.unpack("!B", byte)[0] == 0x1b:
                            header_counter += 1
                            if header_counter == 3:
                                mode_state = M_READ_PARAMETERS
                                header_counter = 0
                        #
                        # If not 0x1b while M_READ_HEADER, reset header_conter
                        #
                        else:
                            header_conter = 0

                    # Paramters are a 7 byte block
                    # 8bit reseved 
                    # 16bit sequence number
                    # 8bit commnad
                    # 8bit unused (dest port)
                    # 16bit message size
                    #
                    elif mode_state == M_READ_PARAMETERS:
                        # Pack next 7 bytes into  parameters
                        parameters += byte
                        if len(parameters) == 7:
                            #
                            # Get sequence number
                            #
                            (sequence_num,) = struct.unpack_from("!H", parameters, 1)
                            #
                            # Get command - index 3
                            #
                            (command,) = struct.unpack_from("!B", parameters, 3)
                            #
                            # If data was transfered and it ended with \x1b,
                            # process state for the special case that happens
                            # at the end of the buffer
                            #
                            if data_state == DSTATE_READ_HEADER:
                                self._read_buffer.put('\x1b')
                                print("Ends in one escapes")
                            elif data_state == DSTATE_READ_STATUS_TYPE:
                                self._read_buffer.put('\x1b')
                                self._read_buffer.put('\x1b')
                                print("Ends in two escapes")
                                #
                            # Reset because there was a previous data transfer
                            # in progress, it isn't now
                            #
                            data_state = DSTATE_READ_NORMAL
                            #
                            # Get message length,
                            # index 5 and 6,
                            # and unpack to 16bit value...
                            #
                            (length_bin,) = struct.unpack_from("!H", parameters, 5)
                            #
                            # Convert to an int
                            #
                            length = int(length_bin)
                            #
                            # End: Trying to get it.
                            # -----------------------------------
                            parameters = ""  # clear the buffer
                            if length == 0:
                                mode_state = M_READ_HEADER  # no data, goto next header
                            else:
                                mode_state = M_READ_DATA  # have data
                                data_counter = 0

                    elif mode_state == M_READ_DATA:
                        #
                        # Time to collect the data
                        #
                        data_counter += 1
                        #
                        # Command processing
                        #

                        # If the command is 0x44
                        if command and struct.pack("!B", command)[0] == self.com.ctrl['TX_DATA']:
                            #
                            # State machine data_state starts at DSTATE_READ_NORMAL
                            #
                            if data_state == DSTATE_READ_NORMAL:
                                #
                                # Check if bytes follow format of data state
                                #
                                if struct.unpack("!B", byte)[0] == 0x1b:
                                    data_state = DSTATE_READ_HEADER
                                #
                                # If not it is normal data
                                #
                                else:
                                    self._read_buffer.put(byte)

                            elif data_state == DSTATE_READ_HEADER:
                                if struct.unpack("!B", byte)[0] == 0x1b:
                                    data_state = DSTATE_READ_STATUS_TYPE
                                #
                                # If not normal data, and must add previous 0x1b
                                #
                                else:
                                    self._read_buffer.put('\x1b')
                                    self._read_buffer.put(byte)
                                    data_state = DSTATE_READ_NORMAL
                            #
                            #  two 0x1b, followed by 0xff is normal data
                            #
                            elif data_state == DSTATE_READ_STATUS_TYPE:
                                (ds_status,) = struct.unpack("!B", byte)
                                if ds_status == 0xff:
                                    self._read_buffer.put('\x1b')
                                    self._read_buffer.put('\x1b')
                                    data_state = DSTATE_READ_NORMAL
                                else:
                                    data_state = DSTATE_READ_REGISTER_VALUE
                            else:
                                data_state = DSTATE_READ_NORMAL
                                (ds_value,) = struct.unpack("!B", byte)

                        #
                        # Complete message received
                        # Reset mode state machine
                        #
                        if data_counter == length:
                            #
                            # no more data
                            #
                            # Reset state machine to look for next header
                            #
                            mode_state = M_READ_HEADER
                            #
                            # Print the command 
                            #
                            [wcommand, ] = [i for i in list(self.com.ctrl.keys()) if
                                            self.com.ctrl[i] == struct.pack("!B", command)[0]]
                            if self.logger:
                                self.logger.info("Command: {}".format(wcommand))
                            #
                            # Send Acknowledgement
                            #
                            self.send_ack(sequence=sequence_num, size=length)
                    else:
                        pass

        finally:
            self._thread = None
            if self.logger:
                self.logger.debug("read thread terminated")

    def _internal_raw_write(self, data):
        """internal socket write with no data escaping. used to send telnet stuff."""
        self._write_lock.acquire()
        try:
            self._socket.sendall(data)
        finally:
            self._write_lock.release()

    def intellisockSendPurge(self, value):
        # item = self._intellisock_options['purge']
        # item.set(value) # transmit desired purge type
        # item.wait(self._network_timeout) # wait for acknowledge from the server
        pass

    def intellisockSetControl(self, value):
        # item = self._intellisock_options['control']
        # item.set(value) # transmit desired control type
        # if self._ignore_set_control_answer:
        #    # answers are ignored when option is set. compatibility mode for
        #    # servers that answer, but not the expected one... (or no answer
        #    # at all) i.e. sredird
        #    time.sleep(0.1)  # this helps getting the unit tests passed
        # else:
        #    item.wait(self._network_timeout) # wait for acknowledge from the server
        pass


# assemble Serial class with the platform specific implementation and the base
# for file-like behavior. for Python 2.6 and newer, that provide the new I/O
# library, derive from io.RawIOBase
try:
    import io
except ImportError:
    # classic version with our own file-like emulation
    class Serial(IntellisockSerial, FileLike):
        pass
else:
    # io library present
    class Serial(IntellisockSerial, io.RawIOBase):
        pass

# simple client test
if __name__ == '__main__':
    s = Serial('intellisock://localhost:5000', 115200)
    sys.stdout.write('{}\n'.format(s))

    # ~ s.baudrate = 1898

    sys.stdout.write("write...\n")
    s.write("hello\n")
    s.flush()
    sys.stdout.write("read: {}\n".format(s.read(5)))

    # ~ s.baudrate = 19200
    # ~ s.databits = 7
    s.close()
