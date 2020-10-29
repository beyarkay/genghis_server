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
* TODO test the bot fighting system
* TODO The mobile display doesn't work with the long game names
* TODO The background doesn't adapt to the mobile display
* TODO Whichever bot is currently making it's move, highlight it somehow
## Nice to have
* Allow NN training
* TODO Revamp the front end
* TODO add nice instructions for beginners to the console
* TODO Add more maps to the default bot client
* TODO Program your own bot
* TODO Make a client version of the monitoring system
