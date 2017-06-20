import asyncio
from random import randint
from subprocess import getoutput

import constants

no_permissions = "`You do not have the required permissions to use this command`"


@bot.command(pass_context=True)
@asyncio.coroutine
def xmc(ctx, *, args: str):
    is_allowed = False
    for server in bot.servers:
        if ctx.message.author.id == server.owner.id:
            is_allowed = True
            break
    if not is_allowed:
        for client_id in config.allowed_client_ids:
            if ctx.message.author.id == client_id:
                is_allowed = True
                break
    if is_allowed:
        print("Executing command 'xmc'")
        output = getoutput("python3.4 " + config.xmc_script_path + "/start.py " + args)
        yield from bot.say('`' + output + '`')
    else:
        yield from bot.say(no_permissions)


@bot.command(pass_context=False)
@asyncio.coroutine
def random(*, args: str):
    print("Executing command 'random'")
    split_args = args.split(' ')
    if split_args[0] in ('s', 'string', 't', 'text', 'm', 'message'):
        split_strings = split_args[1].split(',')
        result = split_strings[randint(0, len(split_strings) - 1)]
        yield from bot.say("`Result: " + result + "`")
    else:
        split_numbers = split_args[1].split(',')
        min_value = int(split_numbers[0])
        max_value = int(split_numbers[1])
        result = str(randint(min_value, max_value))
        yield from bot.say("`Result: " + result + "`")


@bot.command(pass_context=False)
@asyncio.coroutine
def version():
    print("Version: " + constants.VERSION)
    print("Release Date: " + constants.RELEASE_DATE)
    print("Author: " + constants.AUTHOR)


@bot.command(pass_context=False)
@asyncio.coroutine
def ping():
    print("Executing command 'ping'")
    yield from bot.say("Pong!")

