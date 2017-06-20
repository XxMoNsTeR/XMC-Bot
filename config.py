import sys
import configparser
import json
import constants


class ConfigDefaults:
    owner_id = None
    token = None
    command_prefix = '-'
    xmc_script_path = '~'
    privileged_ids = []

    config_file = "bot.cfg"


class Config:
    def __init__(self, config_file=ConfigDefaults.config_file):
        self.config_file = config_file
        config = configparser.RawConfigParser()
        config.read_file(open(self.config_file))

        try:
            self.owner_id = config.get('data', 'owner_id', fallback=ConfigDefaults.owner_id)
            self.token = config.get('data', 'token', fallback=ConfigDefaults.token)
            self.command_prefix = config.get('data', 'command_prefix', fallback=ConfigDefaults.command_prefix)
            self.xmc_script_path = config.get('data', 'xmc_script_path', fallback=ConfigDefaults.xmc_script_path)
            self.privileged_ids = set(json.loads(config.get('data', 'privileged_ids', fallback=ConfigDefaults.privileged_ids)))
        except configparser.NoSectionError:
            print("[ut-bot-config]: A section is missing in your config file!")
            sys.exit()
        except configparser.NoOptionError:
            print("[ut-bot-config]: An option is missing your config file!")
            sys.exit()
        except configparser.Error:
            print("[ut-bot-config]: Your config file is broken! Please check if the config file has all the needed options inside it.")
            sys.exit()
