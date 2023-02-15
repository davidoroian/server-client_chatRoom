# Chat application

## Intro

This is a client-server chat application that accepts connections from multiple clients with different functionalities of a regular application of this type.

## Run

In order to run the application,  you have to start the server using `pyhton` command for the `server.py` program from the **root** directory. After you run the command you should see the line `Server started` in the console. 

Once this is done, open another console and go to the root directory of the application and run `python client.py`. After you run this command a message box should appear requesting a username from you, after you enter a username you should be taken to the chat room. 

In order to have multiple clients in the chat, open different terminals and run the `client.py` program on them.

## Functionalities

This is a client-server chat application that accepts multiple connections and has the following functionalities (can be also seen using '/help' command in the chat):

```
        @[username/group] [message] - send a message to a user or a group
        /help - get help
        /users - lists existing usernames with status
        /groups - lists your available groups
        /group [groupname]- lists the users and admins in that specific group
        /create group [groupname] - creates an empty group with you as admin
        /add [groupname] [username]- adds a user to a group, if you are an admin there
        /make admin [groupname] [username] - adds username to admin group for specific group
        /remove [groupname] [username] - remove user from specific group
        /delete [groupname] - delete group if empty
        /rename [groupname] [newgroupname] - rename group if new name is available
```