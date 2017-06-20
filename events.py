import asyncio

import discord

import config
from config import bot


@bot.event
@asyncio.coroutine
def on_ready():
    print("Logged in")
    print("Name: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("Discord version: " + discord.__version__)
    print("Bot version: " + config.version)
