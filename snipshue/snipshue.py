# -*-: coding utf-8 -*-
""" Philips Hue skill for Snips. """

import requests
import json
import time
from hue_setup import HueSetup
from color_utils import colors


class SnipsHue:
    """ Philips Hue skill for Snips. """

    colormap = colors

    def __init__(self, hostname=None, username=None, locale=None):
        """ Initialisation.

        :param hostname: Philips Hue hostname
        :param username: Philips Hue username
        :param light_ids: Philips Hue light ids
        """
        self.username  = username
        self.hostname  = hostname
        if hostname is None or username is None:
            setup = HueSetup(hostname, username)
            url = setup.bridge_url
            self.username  = setup.get_username()
            self.hostname  = setup.get_bridge_ip()
            print(setup.bridge_url)
            print str(url)
        else:
            url = 'http://{}/api/{}'.format(hostname, username)

        self.lights_endpoint = url + "/lights"
        self.groups_endpoint = url + "/groups"
        self.config_endpoint = url + "/config"
        self.lights_from_room = self._get_rooms_lights()

    def light_on(self, location=None):
        """ Turn on Philips Hue lights in [location] """

        self._post_state_to_ids({"on": True}, self._get_light_ids_from_room(location))

    def light_off(self, location=None):
        """ Turn off all Philips Hue lights in [location] """

        self._post_state_to_ids({"on": False}, self._get_light_ids_from_room(location))

    def light_brightness(self, location=None, percent):
        """ Set a specified brightness [percent] to a hue light in [location] """
        brightness = int(round(percent * 255))

        self._post_state_to_ids({"on": True, "bri": brightness}, self._get_light_ids_from_room(location))

    def light_color(self, location=None, color):
        """ Set a specified [color] to a hue light in [location] """
        hue = color_name.split('x')[0]
        sat = color_name.split('x')[1]

        self._post_state_to_ids({"on": True, "sat": sat, "hue", hue}, self._get_light_ids_from_room(location))

    def light_scene(self, location=None, scene):
        """ Set a specified [scene] to a hue light in [location] """

        # more info


    def light_up(self, location, percentage):
        """ Increase Philips Hue lights' intensity. """
        brightness = int(round(percent * 255))

        light_ids = self._get_light_ids_from_room(location)
        lights_config = self._get_lights_config(light_ids)

        for light_id in light_ids:
            intensity = lights_config[light_id]["bri"]

            intensity += brightness

            if intensity > 254:
                intensity = 254
            if intensity < 0:
                intensity = 0
                
            self._post_state({"on": True, "bri": intensity}, light_id)

    def light_down(self, location, perentage):
        """ Lower Philips Hue lights' intensity. """
        brightness = int(round(percent * 255))

        light_ids = self._get_light_ids_from_room(location)
        lights_config = self._get_lights_config(light_ids)

        for light_id in light_ids:
            intensity = lights_config[light_id]["bri"]
            if intensity < perentage:
                intensity = 0
            else:
                intensity -= perentage
            self._post_state({"bri": intensity}, light_id)

    def _post_state_to_ids(self, params, light_ids):
        """ Post a state update to specyfied Philips Hue lights. """
        try:
            for light_id in light_ids:
                self._post_state(params, light_id)
                time.sleep(0.2)
        except Exception as e:
            return

    def _post_state(self, params, light_id):
        """ Post a state update to a given light.

        :param params: Philips Hue request parameters.
        :param light_id: Philips Hue light ID.
        """
        if (light_id is None) or (params is None):
            return

        print("[HUE] Setting state for light " +
              str(light_id) + ": " + str(params))
        try:
            url = "{}/{}/state".format(self.lights_endpoint, light_id)
            requests.put(url, data=json.dumps(params), headers=None)
        except:
            print("[HUE] Request timeout. Is the Hue Bridge reachable?")
            pass

    def _get_hue_saturation(self, color_name):
        """ Transform a color name into a dictionary represenation
            of a color, as expected by the Philips Hue API.

        :param color_name: A color name, e.g. "red" or "blue"
        :return: A dictionary represenation of a color, as expected
            by the Philips Hue API, e.g. {'hue': 65535, 'sat': 254, 'bri': 254}
        """
        hue = color_name.split('x')[0]
        sat = color_name.split('x')[1]
        return {'hue':hue , 'sat':sat}
        #return self.colormap.get(color_name, {'hue': 0, 'sat': 0})

    def _get_lights_config(self, light_ids):
        """ Make a get request to get infos about the current state of the given lights """
        lights = {}

        for light_id in light_ids:
            current_config = requests.get(self.lights_endpoint + "/" + str(light_id)).json()["state"]
            lights[light_id] = current_config

        return lights

    def _get_all_lights(self):
        lights = requests.get(self.lights_endpoint).json()
        return lights.keys()

    def _get_all_lights_name(self):
        lights = requests.get(self.lights_endpoint).json()
        names = [(key, value.get("name")) for key, value in lights.iteritems()]
        return  names
    def _get_light_ids_from_room(self, room):
        """ Returns the list of lights in a [room] or all light_ids if [room] is None """

        if room is not None:
            room = room.lower()
        if room is None or self.lights_from_room.get(room) is None:
            return self._get_all_lights()

        return self.lights_from_room[room]

    def _get_rooms_lights(self):
        """ Returns a dict {"room_name": {"light1", "light2"}, ...} after calling the Hue API """
        groups = requests.get(self.groups_endpoint).json()
        ids_from_room = {}
        for key, value in groups.iteritems():
            group = value
            if group.get("class") is not None:
                ids_from_room[str.lower(str(group["class"]))] = [str(x) for x in group["lights"]]
            if group.get("name") is not None:
                    ids_from_room[str.lower(str(group["name"].encode('utf-8')))] = [str(x) for x in group["lights"]]
        print "[HUE] Available rooms: \n" + ("\n".join(ids_from_room.keys()))

        return ids_from_room