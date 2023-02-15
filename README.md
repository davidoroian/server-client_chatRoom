# Server application

This is a client-server chat application that accepts multiple connections and has the following functionalities (can be also seen using '/help' command in the chat):

```
These are the available commands: 
        @[username/group] [message] - send a message to a user or a group
        /help - get help
        /users - lists existing usernames with status
        /groups - lists your available groups
        /group [groupname]- lists the users and admins in that specific group
        /create group [groupname] - creates an empty group with you as admin
        /add [groupname] [username]- adds a user to a group, if you are an admin there
        /make admin [groupname] [username] - adds username to admin group for specific group
```