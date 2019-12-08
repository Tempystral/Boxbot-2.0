import glob
import json
import anyconfig
import scalpl
from datetime import datetime
from .logger_setup import logger

#    Class: ConfigManager
# Function: To store and load settings for BoxBot 2.0
#         : 
#         : - Register a setting to the bot's config model
#         : - Retrieve a value from the bot's config model
#         : - Load a config file into the bot's config model
#         : - Save the model into a file


class ConfigManager:
  def __init__(self, filepath="./config/settings.toml", max_backups=10):
    self._settings_file = filepath
    self._max_backups = max_backups
    self.config = scalpl.Cut(self.loadConfig())

  # To do: Limit total number of backups
  #      : Check to see if backup is redundant
  #      : Add code to maintain up to max_backups number of backup configs
  def __backupConfigFile(self):
    '''Backup existing config file to a new timestamped file'''
    anyconfig.dump(self.config, f"./config/config.backup_{datetime.now()}".replace(":", "_") + ".toml")
  
  def saveConfig(self):
    '''Save config model to a file'''
    self.__backupConfigFile()
    anyconfig.dump(self.config.data, self._settings_file)
  
  def loadConfig(self) -> dict():
    '''Load config model from a file'''
    try:
      config = anyconfig.load(self._settings_file)
    except FileNotFoundError:
      config = {}
    return config

  ## Accessors ##

  def put(self, keys:str, value):
    '''Register a value in config to a period-delimited property string'''
    try:
      self.config[keys] = value
    except KeyError as e:
      logger.warning(f"No value for property {keys}!\n{e}")
      return None
    return self.config.data

  def get(self, keys:str, default=None):
    '''Retrieve the value in config registered to a period-delimited property string'''
    return self.config.get(keys, default=default)

  def __unfold(self, properties:str) -> list():
    '''Turns a period-delimited property name into a list of property strings'''
    return properties.strip().split(".")

boxconfig = ConfigManager()
