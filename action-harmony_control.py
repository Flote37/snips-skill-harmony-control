#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from os.path import expanduser
import os

from harmony_controller.harmony_controller import HarmonyController
from snipshelpers.thread_handler import ThreadHandler
from snipshelpers.config_parser import SnipsConfigParser
import Queue

CONFIGURATION_ENCODING_FORMAT = "utf-8"

CONFIG_INI = "config.ini"
CACHE_INI = expanduser("~/.harmony_cache/cache.ini")
CACHE_INI_DIR = expanduser("~/.harmony_cache/")

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

_id = "snips-skill-harmony_control"

AIOHARMONY_PATH = "aioharmony_path"
HARMONY_IP_CONFIG_KEY = "harmony_ip"
WATCH_FILM_ACTIVITY_CONFIG_KEY = "watch_film_activity_id"


class SkillHarmonyControl:
    def __init__(self):
        try:
            config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except:
            config = None

        aioharmony_path=None
        harmony_ip = None
        watch_film_activity_id = None
        if config and config.get('secret', None) is not None:
            # Add Lib aioharmony to Path
            if config.get('global').get(AIOHARMONY_PATH, None) is not None:
                aioharmony_path = config.get('global').get(AIOHARMONY_PATH)
                if aioharmony_path == "":
                    aioharmony_path = None

            # Get Harmony IP from Config
            if config.get('secret').get(HARMONY_IP_CONFIG_KEY, None) is not None:
                harmony_ip = config.get('secret').get(HARMONY_IP_CONFIG_KEY)
                if harmony_ip == "":
                    harmony_ip = None

            # Get Activities ID from Config
            if config.get('secret').get(WATCH_FILM_ACTIVITY_CONFIG_KEY, None) is not None:
                watch_film_activity_id = config.get('secret').get(WATCH_FILM_ACTIVITY_CONFIG_KEY)
                if watch_film_activity_id == "":
                    self.WATCH_FILM_ACTIVITY_ID = None
                else:
                    self.WATCH_FILM_ACTIVITY_ID = watch_film_activity_id

        if harmony_ip is None or watch_film_activity_id is None:
            print('No configuration')

        self.harmony_controller = HarmonyController(harmony_ip=harmony_ip, aioharmony_path=aioharmony_path)
        self.update_config(CACHE_INI, config, harmony_ip, watch_film_activity_id)
        self.queue = Queue.Queue()
        self.thread_handler = ThreadHandler()
        self.thread_handler.run(target=self.start_blocking)
        self.thread_handler.start_run_loop()

    # section -> handlers of intents
    def callback(self, hermes, intent_message):
        print("[HARMONY] Received")
        # all the intents have a house_room slot, extract here

        intent_name = intent_message.intent.intent_name
        if ':' in intent_name:
            intent_name = intent_name.split(":")[1]
        if intent_name == 'watchFilm':
            self.queue.put(self.start_watch_film(hermes, intent_message))

        if intent_name == 'powerOff':
            self.queue.put(self.power_off(hermes, intent_message))

    def start_watch_film(self, hermes, intent_message):
        self.start_activity(hermes, intent_message, self.WATCH_FILM_ACTIVITY_ID)

    def start_activity(self, hermes, intent_message, activity_id):
        self.harmony_controller.start_activity(activity_id)
        self.terminate_feedback(hermes, intent_message)

    def power_off(self, hermes, intent_message):
        self.harmony_controller.power_off()
        self.terminate_feedback(hermes, intent_message)

    def terminate_feedback(self, hermes, intent_message, mode='default'):
        if mode == 'default':
            hermes.publish_end_session(intent_message.session_id, "")
        else:
            # more design
            hermes.publish_end_session(intent_message.session_id, "")

    def update_config(self, filename, data, harmony_ip, watch_film_activity_id):
        if not os.path.exists(CACHE_INI_DIR):
            os.makedirs(CACHE_INI_DIR)
        if 'secret' not in data or data['secret'] is None:
            data['secret'] = {}
        data['secret'][HARMONY_IP_CONFIG_KEY] = harmony_ip
        data['secret'][WATCH_FILM_ACTIVITY_CONFIG_KEY] = watch_film_activity_id
        SnipsConfigParser.write_configuration_file(filename, data)

    def start_blocking(self, run_event):
        while run_event.is_set():
            try:
                self.queue.get(False)
            except Queue.Empty:
                with Hermes(MQTT_ADDR) as h:
                    h.subscribe_intents(self.callback).start()


if __name__ == "__main__":
    SkillHarmonyControl()
