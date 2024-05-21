# Discord ConditionsBot for the Hudson Highlands Fjord

A bot that grabs data from various sources to populate discord
with important information for small boats.

Built by Hudson River Expeditions & klb

```
​No Category:
  _water    Display the water tempareture for a location. 
  add       Adds two numbers together.
  alerts    Display the weather forecast for a location. 
  all       Show all of the available data for a location 
  choose    Chooses between multiple choices.
  current   
  currents  
  forecast  
  help      Shows this message
  locations List locations and their available data 
  now       Pin an alert for the location that combines a bunch of data points. 
  roll      Rolls a dice in NdN format.
  tides     Display the tidal height predictions for a location. 
  water     
  weather   Display the weather forecast for a location. 
```
Type ?help command for more info on a command.
You can also type ?help category for more info on a category.

## Getting Started

Clone the source into a new or existing activated python environment–virtualenv, docker, whatever floats your boat–and `pip install -r requirements.txt` to get everything set up. `python bot.py` will start it running.

Register the bot as a new Discord appliation at the (Developer Portal)[https://discord.com/developers/applications]. The last step is to generate an OAuth2 URL that you paste into a browser that will let you choose which channel to load the bot in.

Alternatively, you can start a chat with the bot directly. I will leave that as an exercise for the reader.
