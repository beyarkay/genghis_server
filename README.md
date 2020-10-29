# Genghis Server
## A bot-battling game system


## Bot action possibilities

### Walk to an empty cell
```
{
    "action": "walk",
    "direction": One of l, u, r, d or a combination of two of them
}
```

### Attack another bot
When your bot makes an attack on an adjacent bot (in one of the 8
adjacent cells to your own), the attack can either hit or miss.

If an attack misses, nothing happens and your turn is over. If the 
attack hits, then your opponent will randomly drop one coin onto an adjacent
cell to itself that is either the cell you are in, or contains air. 



```
{
    "action": "attach",
    "direction": One of l, u, r, d or a combination of two of them
}
```

### Port between battlegrounds
To do this is the same as walking into a cell that has a port
```
{
    "action": "walk",
    "direction": One of l, u, r, d or a combination of two of them
}
```
### Drop a coin
The bot will remain in the same spot, but one coin will be dropped
in the direction you choose. You can only drop coins onto air blocks
or onto other bots
```
{
    "action": "drop",
    "currency": "drop",
    "direction": One of l, u, r, d or a combination of two of them
}
```

## Future Features


## TODOs

### Important for getting people play-testing
1. Get things synchronous properly
2. Update D3 plots, don't recreate D3 plots
3. Get a live badge working
4. Get a schedule of games going
6. Something's wrong with the attacking code. The graphs look like something is funky

### Performance
* TODO Get synchronous Server updates working, so you get 'push' notifications on the website client
* TODO instead of re-creating the svg files, just update them with new data

### Mobile
* TODO Doesn't work with the long game names
* TODO Battleground / graphs don't react properly to the thin format

### UI/UX
* TODO Give more RIGHT NOW information (who's move is it?, what tick is it?)
* TODO Add in all the hyperlinks to bots / battlegrounds
* TODO Add in hover info
* TODO Dark mode

### Features
* TODO able to follow either: battleground, bot, or whoever's turn it is at the moment
* TODO Enable the LIVE NOW dialogue to be accurate somehow
* TODO Get games going regularly with 

### Nice to have
* TODO Allow NN training
* TODO Make a client version of the monitoring system
