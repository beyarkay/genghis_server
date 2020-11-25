# Genghis Competitive Bot System - Server
## A bot-battling game system for coders
Genghis is a framework that allows bots built by Computer Science 
students compete for resources, trade, and fight each other across 
multiple different battlegrounds. 
See the [Genghis Client](https://github.com/beyarkay/genghis_client) to get started.

## TODO - Front End revamp
* TODO instead of re-creating the D3 files, just update them with new data
* TODO Give more RIGHT NOW information (who's move is it?, what tick is it?)
* TODO make it more obvoius which game it is (and maybe simplify the game name?)
* TODO make the schedule of games more obvoius
* TODO flip the graph direction, so that the past is to the left
* TODO add more info about connection (connected to game, loading data, data failed, etc)
* Game Info: Starts out as being very general
    * ie: order of turn, which bots are which icons
    * Can click on a bot/bg to get more detailed info

### TODO - unclassified
* TODO When the game ends, add a marker so that the client stops requesting.
* TODO Add in some error checking for step 5 in the introduction


### Gameplay
* TODO Bots have health points.
* TODO attacking a bot decreases it's health points.
* TODO A bot with 0hp is removed from the game
* TODO Games end either when there are no bots left or when the timer runs out
* TODO Bots can spend coins at certain points in the map in order to heal
* TODO more coins will periodically spawn in throughout the game, on random bgs

### New Player Welcoming
* TODO Add in an explanation of what genghis is
* TODO Add in an explanation fro people who haven't setup nightmare before at all
* Add workflow for developing with genghis
* Maybe add something to explain new features?

### Development
* TODO add in some way of the user's starting up a game at will, with custom bgs, bots, etc

### Performance

### brk bot
* Fix the fast A* algorithm

### UI/UX
* TODO add in a health-points graph
* TODO add in a port-network graph
* TODO Clicking on a plot brings it to the front
* TODO Dark mode

### Nice to have
* TODO Users don't bother reading the full game timestamp. where possible, abbreviate it on the front end
* TODO Better support for NN training 
* TODO Make a client version of the monitoring system
