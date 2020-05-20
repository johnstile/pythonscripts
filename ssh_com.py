#!/usr/bin/env python
"""
Provide convinent interface to issue remote commands and tranferring files over ssh transport
"""

__author__ = 'John Stile'

#------------------------------------------------------------------------------
# Python imports
#------------------------------------------------------------------------------
import os         # for access to environment variables and arguments
import paramiko   # for ssh
from paramiko.ssh_exception import SSHException, AuthenticationException
import socket     # for tcp socket exception
import logging    # adds logging signal facility
import time       # for time.time()
import hashlib    # for testing file integrety
from scp import SCPClient  # Provides scp if sftp doesn't work


#------------------------------------------------------------------------------
# Begin Classes
#------------------------------------------------------------------------------
class SshCom(object):
    """Communicate to a remote host over ssh
    
    Handles ssh and scp transport
    to issue commands copy files"""

    def __init__(
        self,
        username = None,
        password = None,
        key_filename = None,
        address = None,
        log = None
    ):
        self.username = username
        self.password = password
        self.address = address
        self.key_filename = key_filename
        self.log = log
        self.con = None

    def open(self):
        """Create the object"""
        #
        # Create instance of ssh client in paramiko
        #
        self.con = paramiko.SSHClient()
        self.con.blocking = 1
        #
        # Set a magic policy to avoids known_hosts file error
        #
        self.con.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )
        #
        # Loops until connection established or timeout
        #
        stop = False
        timeout = 35.0
        start_time = time.time()
        while not stop:
            #
            # Catch timeout
            #
            if (time.time() - start_time) > timeout:
                self.log.error( "[!!] Exceeded timeout" )
                stop = True
                self.con = None
                break
            #
            # Try to connect 
            #
            try:

                self.log.info("[>>] Try to connect to {}".format(self.address))
                if self.key_filename:
                    self.log.info("[>>] Connect with key_filename:{}".format(self.key_filename))
                    self.con.connect(
                        self.address,
                        username = self.username,
                        key_filename = self.key_filename,
                        timeout = timeout
                    )

                else:
                    self.log.info("[>>] Connect with password:{}".format(self.address))
                    self.con.connect(
                        self.address,
                        username = self.username,
                        password = self.password,
                        timeout = timeout
                    )
                stop = True

            except AuthenticationException:
                self.log.error(
                    "[!!] Authentication Failed."
                )
                stop = True
                ssh = None
                raise

            except SSHException as msg:
                # not sure what to do with this yet.
                # http://www.lag.net/paramiko/docs/paramiko.SSHException-class.html
                pass

            except socket.error as msg:
                self.log.error( "[!!] Can't connect: {}".format(msg))

            except Exception as msg:
                self.log.error( "[!!] Some other error: {}".format(msg))

        if self.con is not None:
            self.log.info( "[OK] Connected established")
        else:
            self.log.error( "[!!] Can not ssh to host")
            raise Exception("Can not ssh to host!")

    def close(self):
        """Close and cleanup

        Close the connection
        """

        self.log.info("[--] Close connection.")

        self.con.close()

    def run(self, cmd):
        """Issue a command on the remote host

        Returns tuple (stdout,stdout,stderror)
        """
        debug = True 
        if debug:
            self.log.debug("cmd: {}".format(cmd))
        exit_status = ""
        lines = ""
        retry_count = 0
        retry_limit = 10
        stop = False
        while not stop:
            try:
                if self.con is None:
                    self.log.info("[!!] Open a connection first. Connection closed.")
                    exit_status = "No connection to run command"
                    lines = ""
                    break

                # issue command and record output
                stdin, stdout, stderr = self.con.exec_command(cmd)

                # check for a fail
                exit_status = stdout.channel.recv_exit_status()
                lines = stdout.readlines()
                if  exit_status is not 0:
                    self.log.error( "[!!] Command Failed!!! Exit status {}".format(exit_status))
                    for line in lines:
                        self.log.error( "[!!] Error message: {}".format(line.rstrip('\n')))

                # If we made it to here, command must have gone though, so end loop
                stop = True

            except socket.error as msg:
                retry_count += 1
                self.log.error( "[!!] Error socket.error: retry_count={}".format(retry_count))
                if retry_count >= retry_limit:
                    break

        # return the result
        return (exit_status, lines)

    def get_file(self, remote_file, local_file):
        """Get file

        Over sftp get a file from the remote host
        """
        self.log.debug(
            (
                "[--] get_file(con,log,remote_file={},local_file={})"
            ).format(
                remote_file,
                local_file
            )
        )

        get_failed_counter = 0
        end = False
        while not end:
            try:
                self.log.debug(
                    "[--] Try to get file"
                )
                if self.con is None:
                    self.log.info("[!!] Open a connection first. Connection closed.")
                    return "No connection to run command", ""
                #
                # Transfer the file
                # -------------------------------
                # Only works if sftp libraries are present on remote host
                # -------------------------------
                # ftp = self.con.open_sftp()
                # ftp.get(remote_file, local_file)
                # ftp.close()
                # --------------------------------------------
                # Alternative  to sftp
                # But requires: pip install scp
                # --------------------------------------------
                scp = SCPClient(self.con.get_transport())
                scp.get(remote_file, local_file)
                scp.close()
                end = True
                self.log.debug(
                    "[OK] Got file"
                )
                continue

            except paramiko.SSHException as msg:
                #
                # Transferr failed
                #
                get_failed_counter += 1
                if get_failed_counter > 10:
                    end = True
                    self.log.error(
                        "[!!] Failed to get file 10 times. Give up."
                    )
                else:
                    self.log.error(
                        "[!!] Failed to get file. retry"
                    )

    def put_file(self, remote_file, local_file):
        """Put file

        Over sftp put a file on remote system
        """

        self.log.debug(
            (
                "[--] put_file(remote_file={},local_file={})"
            ).format(
                remote_file,
                local_file
            )
        )

        if self.con is None:
            self.log.info("[!!] Open a connection first. Connection closed.")
            return ( "No connection to run command", "")


        #
        # Transfer the file
        # -------------------------------
        # Only works if remote has sftp support 
        # -------------------------------
        # ftp = self.con.open_sftp()
        # ftp.put(local_file, remote_file)
        # ftp.close()
        # --------------------------------------------
        # Alternative file copy
        # But requires: pip install scp
        # --------------------------------------------
        scp = SCPClient(self.con.get_transport())
        scp.put(local_file, remote_file)
        scp.close()

        return True

#------------------------------------------------------------------------------
if __name__ == '__main__':
    #------------------------------------------------------------------------------
    # CONSTANTS
    #------------------------------------------------------------------------------
    REMOTE_IP = 'fe80::fced:faff:fece:f00d%eth0' #'192.168.0.1' '192.168.0.100'
    REMOTE_USER = 'pi'
    REMOTE_PASS = 'raspberry'
    REMOTE_KEY_FILE = os.path.join(
        str(Path.home()),
        ".ssh",
        "id_rsa"
    )
    #
    # setup logging
    #
    # Logging instance
    log = logging.getLogger()
    # Console Handler object
    ch = logging.StreamHandler()
    # Attach handler to log instance
    log.addHandler(ch)
    # set log level
    log.setLevel(logging.DEBUG)
    log.debug("Initialized Logger")

    #
    # this is the level for this program
    #
    log.setLevel(logging.INFO)
    #
    # For some reason paramiko is too verbose, so just watch errors
    #
    logging.getLogger("paramiko").setLevel(logging.ERROR )
    #
    # Create connector to remote host
    #
    ssh_com = SshCom(
        username = REMOTE_USER,
        #password = REMOTE_PASS,
        key_filename = REMOTE_KEY_FILE,
        address = REMOTE_IP,
        log = log
    )

    log.info("Open ssh connection")
    ssh_com.open()


    log.info("[>>] issue command and read results")
    (exit_status, lines) = ssh_com.run( 'uname -a' )
    if exit_status is 0:
        for line in lines:
            log.info( "{}".format(line) )

    log.info("[>>] transfer file, transfer it back, verify nothing changed")
    # make a test file
    Path('test_put_file.txt').touch()

    ssh_com.put_file(remote_file="/tmp/test_file_put.txt", lossh_com_file="test_file_put.txt")
    ssh_com.get_file(remote_file="/tmp/test_file_put.txt", lossh_com_file="test_file_get.txt")

    md5_test_file_put = hashlib.md5(open('test_file_put.txt','rb').read()).hexdigest()
    md5_test_file_get = hashlib.md5(open('test_file_get.txt', 'rb').read()).hexdigest()

    if md5_test_file_put != md5_test_file_get:
        log.critical(
            (
                "[!!] Round trip Failed!!! md5 put:{}, get:{}"
            ).format(
                md5_test_file_put,
                md5_test_file_get
            )
        )
    else:
        log.info("[OK] Round trip file transfer success")

    log.info("[--] Close ssh connection")
    ssh_com.close()
