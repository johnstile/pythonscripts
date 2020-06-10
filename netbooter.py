#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SNMP control of networked power swtich (Synaccess netBooter NP-16,NP-16s,NP-8)
Module identifies the model to determine the matching MIB
Switches plug state, read current state
"""

import argparse
import time
import sys
import logging
import socket
import retrying
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

__author__ = 'John Stile'

class Error(Exception):
    """Generic Error Exception"""
    pass


class RequestTimedOutError(Error):
    """Specific RequestTimedOut Error"""
    pass


class SnmpEngineError(Error):
    """SnmpEngine Error"""
    pass


class SnmpPduError(Error):
    """SnmpPdu Error"""
    pass


def retry_if_timeout_error(exception):
    """Return True if we should retry (in this case when it's an socket.timeout), False otherwise"""
    return isinstance(
        exception, 
        (
            socket.timeout, 
            RequestTimedOutError, 
            SnmpEngineError, 
            SnmpPduError, 
            error.CarrierError
        )
    )


def retry_if_result_none(result):
    """Use the result of the function to alter the behavior of retrying.
    Return True if we should retry"""
    return result is None or result is ''


def retry_if_result_false(result):
    """Use the result of the mfunction to alter behavior of retrying
    Return True if the result is False"""
    return not result


def get_log():
    """
    Return a console logger if one not provided
    useful in the doctest
    :return:
    """
    # Setup log
    log = logging.getLogger()
    ch = logging.StreamHandler()
    log.addHandler(ch)
    log.setLevel(logging.INFO)
    log.debug("Initialized Logger")
    return log


class NetBooter(object):
    """Return a netbooter object used to control Netbooter remote power switch
    """

    def __init__(self, 
        host, 
        logger=None, 
        port=161, 
        public="public", 
        private="public",
        conn_type="snmp", 
        debug=False
    ):

        self.host = host
        self.port = port
        self.public = public
        self.private = private
        self.debug = debug
        self.conn_type = conn_type
        self.log = logger or get_log()
        self.timeout = 10  # seconds to wait before retrying NP-16 connection
        self.num_retries = 15  # number of times to try connecting
        #
        # Call init method to initialize these variables
        #
        self.status = {}           # dictionary of name:oid for system status
        self.power_outlet_num = None  # number of outlets in this netbooter
        self.outlet_action = ""    # base oid (minus port) for switching outlet
        self.outlet_status = ""    # base oid (minus port) for status of outlet
        self.outlet_range = []     # valid outlet numbering
        self.identify_netbooter()  # initialize these variables

    @retrying.retry(retry_on_result=retry_if_result_none)
    def get_snmp_data(self, oid):
        """Perform snmp get request
        :param string oid: dot separated SET object identifier
        :return string: value of the oid

        1. Perform snmp get, repeat on fail 10 times, pausing 6 sec between.
        2. Repeat if result == None or ''.
        """
        self.log.debug("Called get_snmp_data({})".format(oid))

        # Convert OID to pysnmp OID representation
        # split string on '.' into a list
        # list comprehension to convert list of strings to list of int
        # - pysnmp expects a tuple of ints
        get_oid_split = tuple([int(x) for x in oid.split('.')])

        self.log.debug("BEFORE: get_oid:{}".format(oid))

        try:
            # Create the pysnmp object, and send query
            err_tuple = cmdgen.CommandGenerator().getCmd(
                cmdgen.CommunityData('my-name', self.public, 0),
                cmdgen.UdpTransportTarget(
                    (self.host, 161),
                    timeout=self.timeout,
                    retries=self.num_retries
                ),
                get_oid_split
            )
        except Exception as e:
            self.log.error("Got Exception:{}".format(str(e)))
            raise(e)

        self.log.debug("AFTER: get_oid:{}".format(oid))
        error_indication, error_status, error_index, var_binds = err_tuple

        # If We receive an error, trigger a retry
        if error_indication:
            raise SnmpEngineError("error:{}".format(error_indication))
        elif error_status:
            raise SnmpPduError("error_status:{},error_index:{}".format(error_status, error_index))
        else:
            self.log.debug(var_binds)

        var_bind = var_binds[0]
        oid, value = var_bind
        response = value
        return response

    @retrying.retry(retry_on_result=retry_if_result_false, stop_max_attempt_number=4)
    def set_snmp_data(self, set_oid, get_oid, state):
        """Perform snmp set request
        :param string set_oid: dot separated SET object identifier
        :param string get_oid: dot separated GET object identifier
        :state string state: value to be SET
        :return bool: True on success, False on fail

        1. Perform snmp set request, repeat on fail 4 times, pausing 6 sec between each try.
        2. Wait a few seconds after a successful set
        3. Perform get,
        4. If get value matches set value, result = True; Otherwise result = False
        5. If result == False, retry method 4 times.
        """
        self.log.debug("Called set_snmp_data(set:{},get:{},val:{})".format(set_oid, get_oid, state))

        # Result variable.
        # True if the value set is verified by subsequent get.
        set_value_successful = False

        # Convert OID to pysnmp OID representation
        # - split string on '.' into a list
        # - use list comprehension to converts list of strings to list of int
        # - pysnmp expects a tuple of ints
        set_oid_split = tuple([int(x) for x in set_oid.split('.')])

        self.log.debug("BEFORE: set_oid:{}, state:{}".format(set_oid, state))

        try:
            # Create the pysnmp object, and send query
            err_tuple = cmdgen.CommandGenerator().setCmd(
                cmdgen.CommunityData('my_name', self.public, 0),
                cmdgen.UdpTransportTarget(
                    (self.host, 161),
                    timeout=self.timeout,
                    retries=self.num_retries
                ),
                (set_oid_split, rfc1902.Integer(state))
            )
        except Exception as e:
            self.log.error("Got Exception:{}".format(str(e)))
            raise

        self.log.debug("AFTER: set_oid:{}, state:{}".format(set_oid, state))
        error_indication, error_status, error_index, var_binds = err_tuple

        # BAND AID: Netbooter misreports state immediately after a set
        # The netbooter tries the set, and during that time reports the values to be set.
        # If the plug is not powered, port returns to previous state, and then netbooter
        #   reports the original state.
        # Waiting 2 seconds is not long enough 1/50 tries
        time.sleep(2)

        # If We receive an error, trigger a retry
        if error_indication:
            raise SnmpEngineError("error:{}".format(error_indication))
        elif error_status:
            raise SnmpPduError("error_status:{},error_index:{}".format(error_status, error_index))
        else:
            self.log.debug(var_binds)

        var_bind = var_binds[0]
        oid, value = var_bind
        response = value
        self.log.debug("set response:{}".format(response))

        # Read value
        current_state = self.get_snmp_data(get_oid)

        self.log.debug(
            (
                "get_oid:{}, "
                "current_state:{},"
                "time:{}"
             ).format(
                get_oid,
                current_state,
                time.time()
            )
        )
        self.log.debug(
            (
                "++++++++++++++++++++++++\n"
                "var_binds:{}\n"
                "var_bind:{}\n"
                "value:{}\n"
                "cur_value:{}\n"
                "------------------------"
            ).format(
                var_binds,
                var_bind,
                value,
                current_state
            )
        )
        # For these set states, make list of acceptable current_state
        state_map = {
            1: [1, 257],    # Good ON values
            2: [0, 2, 256]  # Good OFF values
        }
        if current_state in state_map[state]:
            self.log.debug("Value changed value:{}, current_state:{}".format(value, current_state))
            set_value_successful = True

        return set_value_successful

    def identify_netbooter(self):
        """Identify proper OID's for each netbooter model

            Based on response for OID 1.3.6.1.2.1.1.1.0,
            Return nothing.  Intiaizes class level variables
        """

        # -----------------------------------------------------------------------
        # Netbooter 16s MIB
        # -----------------------------------------------------------------------
        #
        # For testing with net-snmp, this should turn off plug 1
        # snmpset -c public -v1 192.168.1.100 .1.3.6.1.4.1.21728.3.2.1.1.4.0 i 2
        # snmpget -c public -v1 192.168.1.100 .1.3.6.1.4.1.21728.3.2.1.1.3.0
        #
        status_16s = {
            "systemModel":                "1.3.6.1.4.1.21728.3.1.1.0",
            "systemName":                 "1.3.6.1.4.1.21728.3.1.2.0",
            "powerOutletNum":             "1.3.6.1.4.1.21728.3.1.3.0",
            "systemUpTime":               "1.3.6.1.4.1.21728.3.1.5.0",
            "swVersion":                  "1.3.6.1.4.1.21728.3.1.6.0",
            "ifPhysAddress":              "1.3.6.1.2.1.2.2.1.6.0",
            "ipAdEntIfIndex":             "1.3.6.1.2.1.4.20.1.2.0",
            "ipAdEntNetMask":             "1.3.6.1.2.1.4.20.1.3.0",
            "ipAddress":                  "1.3.6.1.4.1.21728.3.4.2.0",
            "acCurrentSensorNumber":      "1.3.6.1.4.1.21728.3.1.7.0",
            "currentAlarmThreshold":      "1.3.6.1.4.1.21728.3.3.1.0",
            "currentDrawStatus1":         "1.3.6.1.4.1.21728.3.3.2.0",
            "currentDrawStatus2":         "1.3.6.1.4.1.21728.3.3.3.0",
            "currentDrawMax1":            "1.3.6.1.4.1.21728.3.3.4.0",
            "currentDrawMax2":            "1.3.6.1.4.1.21728.3.3.5.0",
            "temperatureUpThreshold":     "1.3.6.1.4.1.21728.3.3.6.0",
            "temperatureLowThreshold":    "1.3.6.1.4.1.21728.3.3.7.0",
            "temperatureReading":         "1.3.6.1.4.1.21728.3.3.8.0"
        }
        # 1=on, 2=off
        outlet_status_16s = "1.3.6.1.4.1.21728.3.2.1.1.3"
        # 0=none,1=on,2=off,3=reboot
        outlet_action_16s = "1.3.6.1.4.1.21728.3.2.1.1.4"
        # outlet numbering
        starting_plug_16s = 0

        # -----------------------------------------------------------------------
        # Netbooter 16 or 8 MIB
        # -----------------------------------------------------------------------
        #
        # For testing with net-snmp, this should turn off plug 1
        # snmpset -c public -v1 <IP> .1.3.6.1.4.1.21728.2.4.1.2.1.1.4.1 i 2
        # snmpget -c public -v1 <IP> .1.3.6.1.4.1.21728.2.4.1.2.1.1.3.1
        #
        status_16 = {
            "systemModel":                "1.3.6.1.4.1.21728.2.4.1.1.1.0",
            "systemName":                 "1.3.6.1.4.1.21728.2.4.1.1.2.0",
            "powerOutletNum":             "1.3.6.1.4.1.21728.2.4.1.1.3.0",
            "systemUpTime":               "1.3.6.1.4.1.21728.2.4.1.1.5.0",
            "swVersion":                  "1.3.6.1.4.1.21728.2.4.1.1.6.0",
            "currentAlarmThreshold":      "1.3.6.1.4.1.21728.2.4.1.3.1.1.2",
            "currentDrawStatus1":         "1.3.6.1.4.1.21728.2.4.1.3.1.1.3",
            "currentDrawStatus2":         "1.3.6.1.4.1.21728.2.4.1.3.1.1.4",
            "currentDrawMax1":            "1.3.6.1.4.1.21728.2.4.1.3.1.1.5",
            "currentDrawMax2":            "1.3.6.1.4.1.21728.2.4.1.3.1.1.6",
            "temperatureThreshold":       "1.3.6.1.4.1.21728.2.4.1.3.1.1.7",
            "temperatureReading":         "1.3.6.1.4.1.21728.2.4.1.3.1.1.8"
        }
        # 0 OR 2 OR 256=off, 1 OR 257=on
        outlet_status_16 = "1.3.6.1.4.1.21728.2.4.1.2.1.1.3"
        # 0=none,1=on,2=off,3=reboot
        outlet_action_16 = "1.3.6.1.4.1.21728.2.4.1.2.1.1.4"
        # outlet numbering
        starting_plug_16 = 1
        #
        # Us OID SNMPv2-MIB::sysObjectID.0 to identify netbooter.
        #
        identity_string = self.get_snmp_data('1.3.6.1.2.1.1.1.0')
        #
        # Assign the proper oid's for the netbooter
        #
        self.log.debug("identity: {}".format(identity_string))
        if identity_string == 'Power Distribution System':
            # Choose correct MIB
            self.status = status_16
            # Get outlet count
            self.power_outlet_num = self.get_snmp_data(self.status["powerOutletNum"])
            # Set base OID for switching outlet
            self.outlet_action = outlet_action_16
            # Set base OID for reading outlet state
            self.outlet_status = outlet_status_16
            # Create list of outlet numbering
            self.outlet_range = list(range(
                starting_plug_16,
                starting_plug_16 + self.power_outlet_num))

        elif identity_string == 'Synaccess Remote PDU':
            # Choose correct MIB
            self.status = status_16s
            # Get outlet count
            self.power_outlet_num = self.get_snmp_data(self.status["powerOutletNum"])
            # Set base OID for switching outlet
            self.outlet_action = outlet_action_16s
            # Set base OID for reading outlet state
            self.outlet_status = outlet_status_16s
            # Create list of outlet numbering
            self.outlet_range = list(range(
                starting_plug_16s,
                starting_plug_16s + self.power_outlet_num))
        else:
            raise Exception("Can't identify netbooter!")

        self.log.debug(
            (
                "--------------------\n"
                "powerOutletNum:{}\n"
                "outlet_action:{}\n"
                "outlet_status:{}\n"
                "outlet_range:{}\n"
                "status:{}\n"
                "--------------------"
            ).format(
                self.power_outlet_num,
                self.outlet_action,
                self.outlet_status,
                self.outlet_range,
                self.status
            )
        )

    def plug_off(self, plug_id, delay_time=0):
        """Power off outlet range in list

           Takes: plug_id - list of ports ot power off
           Returns nothing.

        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.plug_off([1])
        Plug 1 to Off
        
        """
        self.log.debug("Called plug_off()")
        #
        # For each plug in list
        #
        for plug in plug_id:
            #
            # Announce intent
            #
            self.log.info("Plug {} to Off".format(plug))
            #
            # Delay
            #
            time.sleep(delay_time)
            #
            # Append the plug id
            #
            # int(plug)    - convert string to int
            # subtract 1   - User count from 1, array count from zero
            # outlet_range[] - grab proper OID for identified netbooter
            # str() - converts the resulting number to string
            # join OID for outlet_action with OID for this plug
            #
            set_oid = self.outlet_action + "." + str(self.outlet_range[int(plug)-1])
            get_oid = self.outlet_status + "." + str(self.outlet_range[int(plug) - 1])
            #
            #
            # plug off state
            #
            my_state = 2
            #
            # Issue snmp set
            #
            self.set_snmp_data(set_oid, get_oid, my_state)

        #
        # return to main
        #
        return

    def plug_on(self, plug_id, delay_time=0):
        """Power on outlet range in list

           Takes: plug_id - list of the plugs
                  delay_time - time to sleep before operation.
           Returns nothing.
        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.plug_on([1])
        Plug 1 to On

        """
        #
        # For each plug in list
        #
        for plug in plug_id:
            #
            # Announce intent
            #
            self.log.info("Plug {} to On".format(plug))
            #
            # Delay
            #
            if delay_time == 0:
                pass
            else:
                time.sleep(delay_time)
            #
            # Append the plug id
            #
            # int(plug)    - convert string to int
            # subtract 1   - User count from 1, array count from zero
            # outlet_range[] - grab proper OID for identified netbooter
            # str() - converts the resulting number to string
            # join OID for outlet_action with OID for this plug
            #
            set_oid = self.outlet_action + "." + str(self.outlet_range[int(plug)-1])
            get_oid = self.outlet_status + "." + str(self.outlet_range[int(plug)-1])
            #
            #
            # plug on state
            #
            my_state = 1
            #
            # Issue snmp set
            #
            self.set_snmp_data(set_oid, get_oid, my_state)

        #
        # return to main
        #
        return

    def all_on(self, delay_time=0):
        """Power on all outlets on switch

           Takes: delay_time - time to sleep before operation.
           Returns nothing.

        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.all_on()
        Plug 1 to On
        Plug 2 to On
        Plug 3 to On
        Plug 4 to On
        Plug 5 to On
        Plug 6 to On
        Plug 7 to On
        Plug 8 to On
        Plug 9 to On
        Plug 10 to On
        Plug 11 to On
        Plug 12 to On
        Plug 13 to On
        Plug 14 to On
        Plug 15 to On
        Plug 16 to On
        """
        #
        # We need all plugs on unit, starting from 1 to max
        # x.outlet_range is an array with all elements
        # len tells us how many elements
        # range(1, max+1) gives an appropriate array
        #
        self.plug_on(
            plug_id=list(range(1, len(self.outlet_range)+1)),
            delay_time=delay_time
        )
        return

    def all_off(self, delay_time=0):
        """Power off all outlets on switch

           Takes: delay_time - time to sleep before operation.
           Returns nothing.
        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.all_off()
        Plug 1 to Off
        Plug 2 to Off
        Plug 3 to Off
        Plug 4 to Off
        Plug 5 to Off
        Plug 6 to Off
        Plug 7 to Off
        Plug 8 to Off
        Plug 9 to Off
        Plug 10 to Off
        Plug 11 to Off
        Plug 12 to Off
        Plug 13 to Off
        Plug 14 to Off
        Plug 15 to Off
        Plug 16 to Off
        
        """
        #
        # We need all plugs on unit, starting from 1 to max
        # x.outlet_range is an array with all elements
        # len tells us how many elements
        # range(1, max+1) gives an appropraite array
        #
        self.plug_off(plug_id=list(range(1, len(self.outlet_range)+1)), delay_time=delay_time)

    def run_sequence(self, plug_id, delay_time=0):
        """Power off, then power on a list of outlets

           Takes: plug_id - list of plugs 0-15
                  delay_time - sleep before operation
           Returns: nothing

        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.run_sequence([2,4,6,8])
        Plug 2 to Off
        Plug 2 to On
        Plug 4 to Off
        Plug 4 to On
        Plug 6 to Off
        Plug 6 to On
        Plug 8 to Off
        Plug 8 to On

        """
        for plug in plug_id:
            self.plug_off(plug_id=[plug], delay_time=delay_time)
            time.sleep(delay_time)
            self.plug_on(plug_id=[plug], delay_time=delay_time)

    def get_status(self):
        """Get general system status

           Takes nothing"
           Returns: nothing

        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.get_status()
        Plug 2 is On
        Plug 4 is On
        Plug 6 is On
        Plug 8 is On
        [1, 1, 1, 1]


        """
        # Run the list
        for name, oid in sorted(list(self.status.items()), key=lambda x: x[0]):
            response = self.get_snmp_data(oid)
            self.log.info("{}:{}".format(name, response))

    def current_draw(self, status=None):
        """Get all current information

           Takes: status - a dictionary of OID's for general system"
           Returns: nothing
        """
        if status is None:
            status = self.status

        # Define query list, of keys in the status dictionary
        current = (
            # "acCurrentSensorNumber" ,
            "currentAlarmThreshold",
            "currentDrawStatus1",
            "currentDrawStatus2",
            "currentDrawMax1",
            "currentDrawMax2"
        )

        # Run the list
        for i in current:
            response = self.get_snmp_data(status[i])
            self.log.info("{}: {}".format(i, response))

    def port_status(self, plug_id=None):
        """Get state of each outlet

           Takes: plug_id - list of plugs
           Returns: array holding 0=off, 1=on, None=Unknown
    
        >>> x = NetBooter(host='192.168.60.124')
        >>> x.debug = True
        >>> x.port_status([2,4,6,8])
        Plug 2 is On
        Plug 4 is On
        Plug 6 is On
        Plug 8 is On
        [1, 1, 1, 1]
        
        """
        #
        # If nothing passed, show everything
        #
        if plug_id is None:
            # plug_id = self.outlet_range
            plug_id = list(range(1, len(self.outlet_range)+1))
        #
        # Declare array to be returned
        #
        status_array = []
        #
        # Go through the list of plugs
        #
        for plug in plug_id:
            #
            # Determine oid based on outlet_range[plug]
            # Gives us the proper oid number for the model
            #
            oid = self.outlet_status + "." + str(self.outlet_range[int(plug)-1])

            ######################################################
            # Work around to race condition in Netbooter Firmware
            # with multiple requests
            # and return the most popular answer
            ######################################################
            # Query once
            response = int(self.get_snmp_data(oid))

            # Set status into english
            status = "UNK"
            if response in [1, 257]:
                status = "On"
            elif response in [0, 2, 256]:
                status = "Off"
            else:
                self.log.critical("Unhandled response:{}".format(response))

            self.log.info("Plug {} is {}".format(plug, status))
            #
            # Append to the returned array
            #
            if status == "On":
                status_array.append(1)
            elif status == "Off":
                status_array.append(0)
            else:
                status_array.append(None)
        return status_array


def main():
    """Program used to operate netbooter remote power switch.
    
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--address', '-a',
        required=True,
        help='Destination IP of netbooter.'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=161,
        help='Destination port to send snmp.'
    )
    parser.add_argument(
        '--public',
        default=['public'],
        help='Destination snmp public community string.'
    )
    parser.add_argument(
        '--private',
        default=['public'],
        help='Destination snmp private community string.'
    )
    parser.add_argument(
        '--delay',
        type=int,
        help='Delay between each operation'
    )
    parser.add_argument(
        '--pause',
        type=int,
        default=0,
        help='Pause for user input during test'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Turn on verbose debug output'
    )
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Run doctest (verbose: -t -t).')

    args = parser.parse_args()

    # Assign to local variables
    address = args.address[0]
    port = args.port
    public = args.public[0]
    private = args.private[0]
    delay_time = args.delay
    debug = args.debug
    doctest = args.test
    conn_type = "snmp"

    print((
        "address:{:>20}\n"
        "port:{:>20}\n"
        "public:{:>20}\n"
        "private:{:>20}\n"
        "delay_time:{:>20}\n"
        "debug:{:>20}\n"
        "doctest:{:>20}\n"
        "conn_type:{:>20}"
    ).format(
        address,
        port,
        public,
        private,
        delay_time,
        debug,
        doctest,
        conn_type
    ))

    if doctest:
        print("To Doctest replace ip of netbooter in docstrings in this file")
        import doctest
        doctest.testmod(verbose=debug)
    else:
        nb = NetBooter(host=address)
        nb.port_status()
        nb.all_off()
        nb.port_status()
        nb.all_on()
        nb.port_status()

if __name__ == "__main__":
    main()
