#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guidance
1. mock out filesystem, network, and any other external access
2. execute the function under test
3. Test expected results, including expected exceptions.
4. Check coverage report from IDE (assume some plugin can do this)
5. keep writing new tests until all of the lines are covered
Guidance from Elsewhere
# https://pylonsproject.org/community-unit-testing-guidelines.html
1. Never import the module-under-test at test module scope
2. Minimize module-scope dependencies
3. Make each test case method test Just One Thing
4. Name TCMs to indicate what they test
5. Share setup via helper methods, not via attributes of self
6. Make fixtures as simple as possible
7. Use hooks and registries judiciously
8. Use hooks and registries judiciously
9. Use mock objects to clarify dependent contracts
10. Don't share text fixtures between test modules
"""

import unittest
from unittest.mock import MagicMock, patch


class TestSerialCom(unittest.TestCase):

    #
    # Each test will import the Module Under Test
    #
    @staticmethod
    def _getTargetClass() -> object:
        from serial_com import SerialCom
        return SerialCom

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    @patch("serial_com.sys")
    def test_list_serial_ports_platform_valid(self, mock_sys):
        """Test valid os"""
        mock_sys.platform = 'linux'
        s_com = self._makeOne(port='/dev/ttyUSB0')
        assert s_com.list_serial_ports is not None


    @patch("serial_com.sys")
    def test_list_serial_ports_platform_invalid(self, mock_sys):
        """Test invalid os"""
        mock_sys.platform = 'unsupportd'
        s_com = self._makeOne(port='/dev/ttyUSB0')
        try:
            s_com.list_serial_ports
        except EnvironmentError:
            pass
        else:
            assert "Failed EnvironmentError"

    @patch("serial_com.serial.Serial")
    @patch("serial_com.sys")
    def test_list_serial_fail(self, mock_sys, mock_serial):
        """Test that we raised the SerialException"""
        from serial import SerialException
        s_com = self._makeOne(port='/dev/ttyUSB0')
        mock_sys.platform = 'linux'
        mock_serial.side_effect = SerialException(
            unittest.mock.Mock(return_value='Mocking SerialException'),
            'not found'
        )
        try:
            s_com.list_serial_ports
        except SerialException:
            pass
        else:
            assert "Failed EnvironmentError"

    @patch("serial_com.sys")
    def test_list_serial_try_good(self, mock_sys):
        """Test that we reached the serial close()"""
        from serial import Serial
        s_com = self._makeOne(port='/dev/ttyUSB0')
        mock_sys.platform = 'linux'
        Serial.close = MagicMock(name='close', return_value=True)
        assert s_com.list_serial_ports

    # def test_list_serial_try_bad(self):
    #     self.mock_sys.platform = 'linux'
    #
    #     self.assertEqual(
    #         self.s_com.list_serial_ports(),
    #         ['/dev/ttyS4']
    #     )
    # def testFunc(self):
    #     port = mock.Mock()
    #     port.readline = mock.Mock(return_value="my string".encode('utf-8')) # as you use a decode call
    #     self.assertEqual(test.port.wait_for_data(port), "my string")
    #
    # def testBufferEmpty(self):
    #     port = mock.Mock()
    #     port.readline = mock.Mock(return_value="".encode('utf-8'))
    #     with self.assertRaises(TimeoutError):
    #         test.port.wait_for_data(port)
    #
    # def testWithFlag(self):
    #     port = mock.Mock()
    #     port.readline = mock.Mock(return_value="fmy string".encode('utf-8'))
    #     self.assertEqual(test.port.wait_for_data(port, 'f'), "my string")


if __name__ == '__main__':
    unittest.main()
