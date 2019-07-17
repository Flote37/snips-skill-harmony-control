# -*-: coding utf-8 -*-
""" Harmony controller for calling aioharmony bash command"""
import asyncio
import logging
from aioharmony.harmonyapi import HarmonyAPI


class HarmonyController:
    """ Harmony Controller for calling Harmony Hub action from Snips Intent """

    def __init__(self, harmony_ip):
        self.harmony_ip = harmony_ip
        self.harmony_api = HarmonyAPI(harmony_ip)

        # Some logging conf
        logging.basicConfig(filename='error.log', level=logging.INFO)

    def start_activity(self, activity_id):
        # @var Loop loop
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.__really_start_activity(activity_id))

    async def __really_start_activity(self, activity_id):
        if await self.harmony_api.connect():
            await self.harmony_api.start_activity(activity_id)
            await self.harmony_api.close()

    def power_off(self):
        # @var Loop loop
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.__really_power_off())

    async def __really_power_off(self):
        if await self.harmony_api.connect():
            await self.harmony_api.power_off()
            await self.harmony_api.close()
