# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_lifx`
================================================================================

A CircuitPython/Python library for communicating with the LIFX HTTP Remote API.

* Author(s): Brent Rubell for Adafruit Industries

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit ESP32SPI or ESP_ATcontrol library:
    https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI
    https://github.com/adafruit/Adafruit_CircuitPython_ESP_ATcontrol
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_lifx.git"

LIFX_URL = 'https://api.lifx.com/v1/lights/'

class LIFX:
    """
    HTTP Interface for interacting with the LIFX API
    """
    def __init__(self, wifi, lifx_token):
        """
        Creates an instance of the LIFX HTTP API client.
        :param wifi_manager wifi: WiFiManager object from ESPSPI_WiFiManager or ESPAT_WiFiManager
        :param str lifx_token: LIFX API token (https://api.developer.lifx.com/docs/authentication)
        """
        wifi_type = str(type(wifi_manager))
        if ('ESPSPI_WiFiManager' in wifi_type or 'ESPAT_WiFiManager' in wifi_type):
            self.wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self._lifx_token = lifx_token
        self._auth_header = {"Authorization": "Bearer %s" % self._lifx_token,}

    @staticmethod
    def _parse_resp(response):
        """Parses and returns the JSON response returned
        from the LIFX HTTP API.
        """
        if response.status_code == 422:
            raise Exception('Error: light(s) could not be toggled: '+ resp['error'])
        try:
            for res in response['results']:
                return res['status']
        except KeyError:
            raise KeyError(response['error'])

    # HTTP Requests
    def _post(self, path, data):
        """POST data to the LIFX API.
        :param str path: Formatted LIFX API URL
        :param json data: JSON data to send to the LIFX API.
        """
        response = self.wifi.post(
            path,
            json=data,
            headers=self._auth_header
        )
        # handle and parse the response
        response = self._parse_resp(response)
        return response

    def toggle_light(self, selector, all_lights=False, duration=0):
        """Toggles current state of LIFX light(s).
        :param dict selector: Selector to control which lights are requested.
        :param bool all: Toggle all lights at once. Defaults to false.
        :param double duration: Time (in seconds) to spend performing a toggle. Defaults to 0.
        """
        if all_lights:
            selector = 'all'
        # compose request URL path
        path = LIFX_URL+selector+'/toggle'
        data = {'duration':duration}
        return self._post(path, data)

    def move_effect(self, selector, move_direction, period, cycles, power_on):
        """Performs a linear move effect on a light, or lights.
        :param str move_direction: Move direction, forward or backward.
        :param double period: Time in second per effect cycle.
        :param float cycles: Number of times to move the pattern.
        :param bool power_on: Turn on a light before performing the move.
        """
        response = self._wifi.post(
            url=LIFX_URL+selector+'/effects/move',
            headers = self._auth_header,
            json = {'direction':move_direction,
                    'period':period,
                    'cycles':cycles,
                    'power_on':power_on},
        )
        resp = response.json()
        # check the response
        if response.status_code == 422:
            raise Exception('Error: '+ resp['error'])
        response.close()
        return resp

    def effects_off(self, selector):
        """Turns off any running effects on the selected device.
        :param dict selector: Selector to control which lights are requested.
        """
        response = self._wifi.post(
            url=LIFX_URL+selector+'/effects/off',
            headers=self._auth_header
        )
        resp = response.json()
        # check the response
        if response.status_code == 422:
            raise Exception('Error: '+ resp['error'])
        response.close()
        return resp

    def set_brightness(self, selector, brightness):
        """Sets the state of the lights within the selector.
        :param dict selector: Selector to control which lights are requested.
        :param double brightness: Brightness level of the light, from 0.0 to 1.0.
        """
        response = self._wifi.put(
            url=LIFX_URL+selector+'/state',
            headers=self._auth_header,
            json={'brightness':brightness}
        )
        resp = response.json()
        # check the response
        if response.status_code == 422:
            raise Exception('Error, light could not be set: '+ resp['error'])
        response.close()
        return resp

    def set_light(self, selector, power, color, brightness):
        """Sets the state of the lights within the selector.
        :param dict selector: Selector to control which lights are requested.
        :param str power: Sets the power state of the light (on/off).
        :param str color: Color to set the light to (https://api.developer.lifx.com/v1/docs/colors).
        :param double brightness: Brightness level of the light, from 0.0 to 1.0.
        """
        response = self._wifi.put(
            url=LIFX_URL+selector+'/state',
            headers=self._auth_header,
            json={'power':power,
                  'color':color,
                  'brightness':brightness
                 }
        )
        resp = response.json()
        # check the response
        if response.status_code == 422:
            raise Exception('Error, light could not be set: '+ resp['error'])
        response.close()
        return resp

    def list_lights(self):
        """Enumerates all the lights associated with the LIFX Cloud Account
        """
        response = self._wifi.get(
            url=LIFX_URL+'all',
            headers=self._auth_header
        )
        resp = response.json()
        response.close()
        return resp


