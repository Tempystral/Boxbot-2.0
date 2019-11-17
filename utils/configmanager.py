import json, glob, anyconfig
from datetime import datetime

# Currently unused!

#    Class: ConfigManager
# Function: To store and load settings for BoxBot 2.0
#         : 
#         : - Register a setting to the bot's config model
#         : - Retrieve a value from the bot's config model
#         : - Load a config file into the bot's config model
#         : - Save the model into a file
#         : - These functions should be as low-level as possible;
#         :     The interface will handle more complex functionality
#         :
#         : - The interface will pass in a copy of the config model

  # In what ways should we be able to change the model?
  #   - Add a new property / value pair
  #   - Update an existing value for a given property
  #   - Remove a value from a property 
  #     - Value may itself be a property/value pair

class ConfigManager:
  def __init__(self, config_file="./config/settings.toml", max_backups=10):
    self._config_file = config_file
    self._max_backups = max_backups
    self._encoder = json.JSONEncoder(check_circular=True, indent=4)

  # To do: Limit total number of backups
  #      : Check to see if backup is redundant (unlikely)
  def __backupConfigFile(self):
    '''Backup existing config file to a new timestamped file'''
    outStr = self._encoder.encode(self.loadConfig())
    with open(f"config.backup_{datetime.now()}.json".replace(":", "_"), "x") as f:
      f.write(outStr)

  
  def saveConfig(self, config):
    '''Save config model to a file'''
    self.__backupConfigFile()
    outStr = self._encoder.encode(config)
    with open(self._config_file, "w") as f:
      f.write(outStr)

  
  def loadConfig(self) -> dict():
    '''Load config model from a file'''
    try:
      anyconfig.load(self._config_file)
    except FileNotFoundError:
      config = {}
    return config

  ## Accessors ##

  # To do: property get safety on get/set commands
  def put(self, properties, value, config):
    '''Register a value in config to a period-delimited property string'''
    keys = self.__unfold(properties)
    for p in keys[:-1]:
      # Iterate down the chain until the penultimate property
      config = config[p]
    config[keys[-1]] = value

  def get(self, properties, config):
    '''Retrieve the value in config registered to a period-delimited property string'''
    for p in self.__unfold(properties):
      config = config[p]
    return config # Config here is the value of the final property

  def __unfold(self, property=str) -> list():
    '''Turns a period-delimited property name into a list of property strings'''
    return property.strip().split(".")

cm = ConfigManager()