#!/usr/bin/env python3

import sys, os
import discord
import asyncio
import constants

import discord.ext.commands
from discord.ext.commands.bot import _get_variable
from config import Config, ConfigDefaults
from functools import wraps


class Bot(discord.Client):
    def __init__(self, config_file=ConfigDefaults.config_file):
        self.config = Config(config_file)
        super().__init__()

    def privileged_only(func):
        @wraps(func)
        @asyncio.coroutine
        def wrapper(self, *args, **kwargs):
            msg = _get_variable('message')
            for client_id in self.config.privileged_ids:
                if msg.author.id == client_id or msg.author.id == self.config.owner_id:
                    yield from func(self, *args, **kwargs)
        return wrapper

    def _get_owner(self):
        return discord.utils.find(lambda m: m.id == self.config.owner_id, self.get_all_members())
    
    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.config.token))
        except discord.errors.LoginFailure:
            print("[ut-bot] Invalid token! Please add a valid token inside the config file!")

    @asyncio.coroutine
    def on_ready(self):
        print("Logged in")
        print("Name: " + self.user.name)
        print("ID: " + self.user.id)
        print("Discord version: " + discord.__version__)
        print("Bot version: " + constants.VERSION)

    @asyncio.coroutine
    def cmd_ping(self, channel):
        self.send_message(channel, "Pong!")

    @asyncio.coroutine
    def on_message(self, message):
        yield from self.wait_until_ready()

        message_content = message.content.strip()

        if message_content.startswith(self.config.command_prefix):
            command, *args = message_content.split()
            command = command[len(self.config.command_prefix):].lower().strip()

            try:
                func_command = getattr(self, 'cmd_%s' % command)
                func_command(message.channel, *args)
            except AttributeError:
                print(message.author.name + " has executed an unregistered command!")


bot = Bot()
bot.run()
