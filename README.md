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
## File structure
TODO


## Future Features
* Include an in-terminal viewing window with
```
tput sc
while :; do
    tput ed
    echo -e "$SECONDS\n$SECONDS\n$SECONDS"
    sleep 1
    tput rc
done
```


## TODO
* When bots port to another bg, they might not get respawned in, and
are only added to the bg.bots list
