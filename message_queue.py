#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Object based Message Queue system
This class pulls the queue processing logic out of the middle our boss/worker code.
It makes it easier to add a new message type.
It is better than string parsing to figure out message types.
It uses meaningful variable names, instead of list indices

The class reading the queue implements the handler
The class writing to the queue writes the proper message type
"""


class QueueMessage(object):
    """Base class"""

    def handle(self, receiver):
        raise NotImplementedError


class QuitMessage(QueueMessage):
    """Worker tells Boss it is ending"""
    def __init__(self, id, this_exit_code):
        self.id = id
        self.this_exit_code = this_exit_code

    def handle(self, receiver):
        receiver.on_quit(self.id, self.this_exit_code)


class LogMessage(QueueMessage):
    """Worker tells Boss to write to it's log"""
    def __init__(self, id, log_level, msg):
        self.id = id
        self.log_level = log_level
        self.msg = msg

    def handle(self, receiver):
        receiver.on_log(self.id, self.log_level, self.msg)


class StatusMessage(QueueMessage):
    """Worker tells Boss to update status.json"""
    def __init__(self, id, data):
        self.id = id
        self.data = data

    def handle(self, receiver):
        receiver.on_status(self.id, self.data)

class RebootMessage(QueueMessage):
    """Boss Tell Worker pause for reboot
    state  "down" or "up"
    """
    def __init__(self, state):
        self.state = state
    
    def handle(self, receiver):
        receiver.on_galaxy_reboot(self.state)


class FinishedMessage(QueueMessage):
    """Tell Boss that the test is over"""

    def __init__(self, ipv6):
        self.ipv6 = ipv6

    def handle(self, receiver):
        receiver.on_finished(self.ipv6)
