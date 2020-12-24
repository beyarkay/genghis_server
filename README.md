# Genghis Competitive Bot System - Server
## A bot-battling game system for coders
Genghis is a framework that allows bots built by Computer Science 
students compete for resources, trade, and fight each other across 
multiple different battlegrounds. 
See the [Genghis Client](https://github.com/beyarkay/genghis_client) to get started.

## Problems to solve
* Before pushing `genghis_server`, should split server-state into:
    * server-config.json and server-state.json
* Need some way to keep each individual game interesting
    * Maybe provide stages / somethign that changes as the game goes from early to mid to late?
* Need to allow for different players to have different strategies
    * With no strategy being definitively better or worse than the others
* Need an ending condition upon which the game will terminate
    * Maybe all players loose health all the time, resulting in all bots dying if they don't actively keep up their health
* make sure the pro players don't have too much incentive to try 'farm' the weaker players
* Need some way of encouraging cooperation in the game - to make it more interesting
    * What if the coin drop mechanism was expanded in some way?
    * Is there a way of creating a promise between players in-game?
        * You agree to do X, I agree to do Y, and if either of us breaks the contract then we have to pay a forfeit.
## Ideas
* Maybe include 'home chests' which bots can deposit coins at. Only home chests would count towards leaderboards
    * Bots can carry a limited number of coins in their personal inventory
* Maybe have 'bounties' go out on different bots throughout the game.
    * So a bounty would be 'kill bot XXX and receive YYY extra coins'
    * Or more generally, give pro-players something to optimise against that the n00bs can safely ignore
  

## TODO - based on talks
* Some method of tracking health
* Ability to hop 2 spaces (over walls) if you leave a coin where you were
* Coin hot-spots, where a large number of coins are spawned throughout the game around certain points
* Meta-graphs, tracking how well bots do over many different games
* Have "playground" games and then "League" games
* Terminate the game after X ticks of no bot-on-bot interactions
* Provide a legend describing what everything on the map is / basic rules

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
* TODO Add in a testing script for the developers
* TODO add in some way of the user's starting up a game at will, with custom bgs, bots, etc

### Performance

### brk bot
* Fix the fast A\* algorithm

### UI/UX
* TODO add in a health-points graph
* TODO add in a port-network graph
* TODO Clicking on a plot brings it to the front
* TODO Dark mode

### Nice to have
* TODO Users don't bother reading the full game timestamp. where possible, abbreviate it on the front end
* TODO Better support for NN training 
* TODO Make a client version of the monitoring system
