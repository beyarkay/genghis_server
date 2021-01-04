# Genghis Competitive Bot System - Server
## A bot-battling game system for coders
Genghis is a framework that allows bots built by Computer Science 
students compete for resources, trade, and fight each other across 
multiple different battlegrounds. 
See the [Genghis Client](https://github.com/beyarkay/genghis_client) to get started.

## Work in progress:
* fix the D3 script to now redraw the bg
* Allow github hosting
* allow control of the bot from the CLI
* Before pushing `genghis_server`, should split server-state into:
    * server-config.json and server-state.json

## Problems to solve
* Need some way to keep each individual game interesting
    * Maybe provide stages / somethign that changes as the game goes from early to mid to late?
* Need to allow for different players to have different strategies
    * With no strategy being definitively better or worse than the others
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
* Coin hot-spots, where a large number of coins are spawned throughout the game around certain points
* Meta-graphs, tracking how well bots do over many different games
* Have "playground" games and then "League" games
* Terminate the game after X ticks of no bot-on-bot interactions

## TODO - Front End revamp
* Clicking on an item will persist the tooltip
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
* TODO Bots can spend coins at certain points in the map in order to heal
* TODO more coins will periodically spawn in throughout the game, on random bgs

### New Player Welcoming
* TODO Add in an explanation of what genghis is
* TODO Add in an explanation fro people who haven't setup nightmare before at all
* Add workflow for developing with genghis
* Maybe add something to explain new features?

### Development
* TODO Add in a testing script for the developers

### Performance

### brk bot

### Logging
* Battleground logs:
    * Number interactions
    * Rate of interactions
    * Number of coins
    * Rate of picking up coins
    * Length spent on BG
    * Which bots spend time on which BG
    * Number of deaths
    * Locations of deaths

* Bot Logs: 
    * Number interactions
    * Rate of interactions
    * Number of coins
    * Rate of picking up coins
    * Number of deaths
        * Also stratify by killer
    * Locations of deaths
* Per game logs:
    * percentil values: [p0, p1, p10, p50, p90, p99, p100]
    * game id, bg id, number of coins, coins [percentiles], deaths [percentiles], interactions [percentiles], durations [percentiles]

### UI/UX
* TODO add in a health-points graph
* TODO add in a port-network graph
* TODO add in a bot-coin graph
* TODO Have a method for 'replaying' interesting interactions
* TODO Dark mode

### Nice to have
* TODO Users don't bother reading the full game timestamp. where possible, abbreviate it on the front end
* TODO Better support for NN training 
* TODO Make a client version of the monitoring system
