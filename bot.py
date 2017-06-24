#!/usr/bin/env python3

import sys, os
import discord
import asyncio
import constants

import discord.ext.commands
from discord.ext.commands.bot import _get_variable
from config import Config, ConfigDefaults
from functools import wraps
from random import randint
from subprocess import getoutput


class Bot(discord.Client):
    def __init__(self, config_file=ConfigDefaults.config_file):
        self.config = Config(config_file)
        super().__init__()

    def privileged_only(func):
        @wraps(func)
        @asyncio.coroutine
        def wrapper(self, *args, **kwargs):
            msg = _get_variable('message')
            allowed = False
            for client_id in self.config.privileged_ids:
                if msg.author.id == client_id:
                    allowed = True
                    yield from func(self, *args, **kwargs)
            if msg.author.id == self.config.owner_id:
                allowed = True
                yield from func(self, *args, **kwargs)
            if not allowed:
                yield from self.send_message(msg.channel, "`You are not allowed to use this command!`")

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
        print("Discord API version: " + discord.__version__)
        print("Bot version: " + constants.VERSION)

    @asyncio.coroutine
    def cmd_help(self, msg, command=None):
        """
        Usage: {command_prefix}help [command]

        Prints this help message and can show help for other commands.

        List of available commands:
            {command_prefix}xmc (privileged only)
            {command_prefix}reload (privileged only)
            {command_prefix}setgame (privileged only)
            {command_prefix}random
            {command_prefix}ping
        """

        if command is None:
            yield from self.send_message(msg.channel, "```\n" + self.cmd_help.__doc__.format(command_prefix=self.config.command_prefix) + "```")
        else:
            try:
                cmd = getattr(self, 'cmd_%s' % command, None)
                yield from self.send_message(msg.channel, "```\n" + cmd.__doc__.format(command_prefix=self.config.command_prefix) + "```")
            except AttributeError:
                yield from self.send_message(msg.channel, "`That command doesn't exist!`")

    @privileged_only
    @asyncio.coroutine
    def cmd_xmc(self, msg, *args):
        """
        Usage: {command_prefix}xmc [arg]

        To check detailed help about this command use {command_prefix}xmc -h
        """

        args = ' '.join(list(args))
        output = getoutput("python3.4 " + self.config.xmc_script_path + "/start.py " + args)
        if len(output) > 2000:
            yield from self.send_message(msg.channel, "Because the output contains " + str(len(output)) +
                                         " characters (over 2000 characters), it will only show the first"
                                         " 20 lines and the last 20 lines of the output")
            output_lines = output.split('\n')
            output = '\n'.join(output_lines[:20]) + '\n.........\n' + '\n'.join(output_lines[-20:])

        yield from self.send_message(msg.channel, '`' + output + '`')

    @privileged_only
    @asyncio.coroutine
    def cmd_reload(self, msg):
        """
        Usage: {command_prefix}reload

        Reloads the configuration of the bot.
        """
        self.config = Config(ConfigDefaults.config_file)
        yield from self.send_message(msg.channel, "`Reloaded configuration.`")

    @privileged_only
    @asyncio.coroutine
    def cmd_setgame(self, msg, *args):
        """
        Usage: {command_prefix}setgame [game name]

        Sets the game name for the bot.
        """
        game = ' '.join(list(args))
        g = discord.Game(name=game)
        yield from self.change_presence(game=g)
        yield from self.send_message(msg.channel, "`Game changed to '" + g.name + "'`")

    @asyncio.coroutine
    def cmd_random(self, msg, *args):
        """
        Usage: {command_prefix}random [choice (c), number (n)] c[choice 1, choice 2, ...]/n[min value, max value]

        Gives you a random number or chooses between a set of choices
        """
        if args[0] in ('c', 'choice'):
            split_strings = args[1].split(',')
            result = split_strings[randint(0, len(split_strings) - 1)]
            yield from self.send_message(msg.channel, "`Result: " + result + "`")
        elif args[0] in ('n', 'number'):
            split_numbers = args[1].split(',')
            min_value = int(split_numbers[0])
            max_value = int(split_numbers[1])
            result = str(randint(min_value, max_value))
            yield from self.send_message(msg.channel, "`Result: " + result + "`")

    @asyncio.coroutine
    def cmd_ping(self, msg):
        """
        Usage: {command_prefix}ping

        Shows the ping of the bot.
        """
        yield from self.send_message(msg.channel, "`Pong!`")

    @asyncio.coroutine
    def on_message(self, message):
        yield from self.wait_until_ready()

        message_content = message.content.strip()

        if message_content.startswith(self.config.command_prefix):
            command, *args = message_content.split()
            command = command[len(self.config.command_prefix):].lower().strip()

            try:
                handler = getattr(self, 'cmd_%s' % command)
                yield from handler(message, *args)
            except AttributeError:
                pass
