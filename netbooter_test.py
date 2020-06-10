#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stress test for netbooter module
Send simultaneous SNMP commands to netbooter to demonstrate when request fails
"""

import multiprocessing
import time
import logging
import argparse
from queue import Queue
import retrying

import message_queue
import netbooter

__author__ = 'John Stile'


class Worker(multiprocessing.Process):
    """
        Workers created for simultaneous SNMP requests 
    """
    def __init__(
            self,
            netbooter_ipv4,
            plug_id,
            queue_from_boss,
            queue_to_boss,
            cycles
    ):
        super(Worker, self).__init__()
        self.netbooter_ipv4 = netbooter_ipv4
        self.plug_id = plug_id
        self.queue_from_boss = queue_from_boss
        self.queue_to_boss = queue_to_boss
        self.cycles = cycles
        self.begin_test = False
        #
        # non-pickle-able objects to be initialized in run()
        # to avoid limitation of multiprocessing on windows
        #
        self.netbooter = None
        self.log = None
        # Result counter
        self.error_count = 0

    def run(self):
        """Initialize Logger and Netbooter,
        message Boss it is ready,
        and poll for a start from the boss"""
        #
        # Setup log
        #
        log_file_name = "{}-worker-plug{}.log".format(self.netbooter_ipv4, self.plug_id)
        rh = logging.FileHandler(log_file_name)
        fmt = logging.Formatter("%(asctime)s (%(levelname)-8s): %(message)s")
        rh.setFormatter(fmt)
        self.log = logging.getLogger()
        self.log.setLevel('INFO')
        self.log.addHandler(rh)
        self.log.info("Log Initialized")
        #
        # Setup Netbooter snmp object
        #
        self.log.info('Creating instance of Netbooter')
        self.netbooter = netbooter.NetBooter(host=self.netbooter_ipv4, logger=self.log)
        #
        # Empty Multiprocessing queue
        #
        while not self.queue_from_boss.empty():
            self.log.info('Inside clear() loop -- getting items from queue')
            self.queue_from_boss.get()
        #
        # Tell boss Worker is ready
        #
        self.queue_to_boss.put(message_queue.StatusMessage(self.plug_id, {'ready': True}))
        #
        # Poll messages from Boss to start test
        #
        self.process_queue()
        #
        # send quit message
        #
        self.log.info("Send Quit to Boss")

        self.queue_to_boss.put(message_queue.QuitMessage(self.plug_id, self.error_count))

    def process_queue(self):
        """Poll the message queue for BeginTest message from Boss
        When message is received, self.begin_test is set to True,
        and the test is run."""

        continue_test = True
        while continue_test:
            # Listen for messages from Boss
            if not self.queue_from_boss.empty():
                try:
                    self.log.debug("reading queue")
                    msg = self.queue_from_boss.get(timeout=0.001)
                    msg.handle(self)
                except Queue.Empty:
                    "Queue unexpectedly empty"

            # Boss sends status message, which toggles this to true
            if self.begin_test:
                self.test()
                continue_test = False
                continue

        self.log.info("Exit while loop.")

    def on_status(self, plug_id, data):
        """Boss will send a BeginTest message once all Workers are ready"""
        self.log.debug('Status({})'.format(plug_id, data))
        if data['BeginTest']:
            self.begin_test = True

    def test(self):
        """Toggle plug on and off, and check state after each operaiton
        If a change fails to take place, terminate test"""
        self.log.info('Run Test')

        try:
            # This is how many times we toggle the plug
            for iteration in range(1, self.cycles+1):
                self.log.info(
                    (
                        "=====Plug: {:>2}, Iteration:{:>3}, Error Count:{:>3}===="
                    ).format(
                        self.plug_id,
                        iteration,
                        self.error_count
                    )
                )
                self.log.info('Power off')
                self.queue_to_boss.put(message_queue.LogMessage(self.plug_id, "INFO", "off"))
                # Change state
                try:
                    self.netbooter.plug_off([self.plug_id])
                    # Read current state
                    status = self.netbooter.port_status([self.plug_id])
                    # If plug not in expected state, count error
                    if status != [0]:
                        self.log.critical("PLUG {} NOT OFF.".format(self.plug_id))
                        # send quit message
                        self.error_count += 1

                except retrying.RetryError as e:
                    self.log.critical("FAILED. plug_off() exception:{}".format(str(e)))
                    self.error_count += 1

                self.log.info('Power on')
                self.queue_to_boss.put(message_queue.LogMessage(self.plug_id, "INFO", "on"))
                # Change state
                try:
                    self.netbooter.plug_on([self.plug_id])
                    # If plug not in expected state, count error
                    status = self.netbooter.port_status([self.plug_id])
                    # If plug not in expected state, count error
                    if status != [1]:
                        self.log.critical("PLUG  {} NOT ON.".format(self.plug_id))
                        # send quit message
                        self.error_count += 1

                except retrying.RetryError as e:
                    self.log.critical("FAILED plug_on(). exception:{}".format(str(e)))
                    self.error_count += 1

            self.queue_to_boss.put(message_queue.QuitMessage(self.plug_id, self.error_count))

        except Exception as e:
            self.log.exception("Exception occurred: {}".format(e))
            raise


class Boss(object):
    """Create workers for each port, and start
        Workers tell boss when they are ready
        Boss monitors the message queue for ready and quit
        Once all the workers are ready, boss has them all start testing
        If any quit message has an error exit_status, boss stops all workers
        Once all workers have quit, boss terminates workers."""

    def __init__(self, netbooter_ipv4):
        self.netbooter_ipv4 = netbooter_ipv4

        # set up multiprocessing logger
        multiprocessing.log_to_stderr()
        self.log = multiprocessing.get_logger()
        fh = logging.FileHandler('{}-boss.log'.format(self.netbooter_ipv4))
        log_format = '%(asctime)s [%(levelname)s/%(processName)s] - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        self.log.addHandler(fh)
        self.log.setLevel('INFO')
        self.log.info('Start Log')

        self.number_of_switch_cycles = 4
        self.plug_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

        self.worker_count = len(self.plug_ids)
        self.workers = []

        # count total number of quit messages
        self.quit_counter = 0
        self.ready_counter = 0

        # processing queue for all DUTs
        self.queue = multiprocessing.Queue()

        # result containers
        self.worker_results = {}
        self.exit_code = 0

        # startup timeout
        self.startup_timeout=15

    def main(self):

        # Create workers, and start
        for plug_id in self.plug_ids:
            # Each worker controls one plug
            w = Worker(
                self.netbooter_ipv4,
                plug_id,
                queue_to_boss=self.queue,
                queue_from_boss=multiprocessing.Queue(),
                cycles=self.number_of_switch_cycles
            )

            # Add worker to our list of workers
            self.workers.append(w)

            # start Worker object run()
            w.start()

        # process messages from Works
        self.process_queue()

        #
        # Block until workers report quit
        #
        while len(self.workers):
            time.sleep(2)

        # # clean up processes and kill any remaining AVBWorkers
        # self.clean_up()

        #
        # Print the result for each worker
        #
        self.log.info("Results for {} cycles".format(self.number_of_switch_cycles))
        for (plug, error_count) in self.worker_results.items():
            if error_count == 0:
                this_log = self.log.info
            else:
                this_log = self.log.critical
            this_log("\tplug:{:>2}, error_count:{:>3}".format(plug, error_count))

    def process_queue(self):

        # loop until we read a 'quit' for worker, or an error
        # When all workers are ready, start the tests
        # If workers are not ready after at time, kill them and quit
        start_time = time.time()
        continue_test = True
        while continue_test:
            # Catch timeout
            if (time.time() - start_time) > self.startup_timeout:
                self.log.error( "[!!] Exceeded startup_timeout. End all worker" )
                for worker in self.workers:
                    self.clean_up(worker)

            # When the number of ready messages == workers, start test
            if self.ready_counter == len(self.workers):
                self.log.info("All Workers ready, start test")

                # Send the message to start testing
                for worker in self.workers:
                    worker.queue_from_boss.put(message_queue.QuitMessage('BOSS', {'BeginTest': True}))
                self.ready_counter = False

            if self.quit_counter == len(self.workers):
                self.log.info("All Workers quit, end program")
                continue_test = False
                continue

            if not self.queue.empty():
                try:
                    msg = self.queue.get(timeout=0.001)
                    msg.handle(self)
                except Queue.Empty as e:
                    self.log.warning(
                        "Queue unexpectedly Empty. {}".format(e)
                    )

    def on_status(self, plug_id, data):
        """Counts the number of workers that are ready
        """
        self.log.debug("plug_id:{}, status: {}".format(plug_id, data))
        self.ready_counter += 1

    def on_quit(self, plug_id, exit_code):
        self.log.info(
            (
                "Quit received from {}, error_count: {}"
            ).format(
                plug_id,
                exit_code
            )
        )
        #
        # Store Exit code
        #
        # if plug_id not in self.worker_results:
        #     self.worker_results[plug_id] = exit_code
        # else:
        self.worker_results[plug_id] = exit_code
        #
        # Force process to end
        #
        w = next((w for w in self.workers if w.plug_id == plug_id), None)
        if w:
            self.clean_up(w)

    def on_log(self, plug_id, log_level, msg):
        self.log.info("[{}][{}] - {}".format(plug_id, log_level, msg))

    def clean_up(self, worker):
        self.log.info("Jobs should be done. Force End if not ended")

        # Must give the children enough time to end, or we kill in the middle of an snmp request.
        timeout = 15

        self.log.critical("plug:{}, exitcode:{}".format(worker.plug_id, worker.exitcode))

        end_time = time.time() + timeout
        continue_cleanup = True
        while continue_cleanup:

            if not worker.is_alive():
                continue_cleanup = False
                continue

            self.log.debug("{} is_alive".format(worker.name))

            # This should end the process
            worker.join(timeout)

            # Force quit the process
            if time.time() >= end_time:
                self.log.warning("{} did not end after {} seconds".format(
                    worker.name,
                    timeout
                ))
                self.log.warning("call terminate on {}".format(worker.name))
                worker.terminate()
                self.log.warning("call final join on {}".format(worker.name))
                worker.join()
        #
        # Remove worker from the workers list
        #
        self.workers.remove(worker)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--ipv4', '-i',
        required=True,
        help='netbooter ipv4 address'
    )
    args = parser.parse_args()
    boss = Boss(args.ipv4)
    boss.main()
