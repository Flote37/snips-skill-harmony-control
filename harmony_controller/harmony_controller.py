# -*-: coding utf-8 -*-
""" Harmony controller for calling aioharmony bash command"""

import logging
import subprocess32 as subprocess


class HarmonyController:
    """ Harmony Controller for calling Harmony Hub action from Snips Intent """

    def __init__(self, harmony_ip):
        print ("Init Harmony")
        self.harmony_ip = harmony_ip

        # Some logging conf
        logging.basicConfig(filename='error.log', level=logging.WARNING)

    def start_activity(self, activity_id):
        command = ['python3 aioharmony', '--harmony_ip ' + self.harmony_ip, 'start_activity ' + activity_id]
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as e:
            logging.error("Error while call aioharmony : " + str(e))

    def power_off(self):
        command = ['python3 aioharmony', '--harmony_ip ' + self.harmony_ip, 'power_off']
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as e:
            logging.error("Error while call aioharmony : " + str(e))

