# IgKnite: Available Commands
IgKnite currentry has a total of 36 available bot commands, roughly distributed among four categories. All the commands are built on Discord's bleeding edge API and use the latest features.

The following is a list of all the available commands (updated: October 11, 2022).

## The Customization Commands
### /makerole [name]
Creates a new server role with the specified *name*.

### /assignrole [member] [role]
Assigns a server *role* to the specified *member*.

### /removerole [role]
Removes a *role* from the server.

### /makeinvite [max_age] [max_uses] [reason]
Creates an invitation link to the server with the specified parameters.

| Parameter | Required | Default |
|---|---|---|
| max_age | No | 0 |
| max_uses | No | 1 |
| reason | No | No reason provided. |

### /nick [member] [nickname]
Changes the server *nickname* of the specified *member*

### /makechannel [name] [category] [topic]
Creates a new channel in the server with the given *name*, inside the given *category*, and sets the given *topic* to it.

| Parameter | Required | Default |
|---|---|---|
| name | Yes |  |
| category | No | None |
| topic | No | None |

### /makevc [name] [category]
Creates a new voice channel with the given *name* in the given *category*.

| Parameter | Required | Default |
|---|---|---|
| name | Yes |  |
| category | No | None |

### /makecategory [name]
Creates a new channel category with the specified *name*.

### /removechannel [channel]
Deletes the given *channel* from the server.

### /reset
Deletes all the messages from the current channel.