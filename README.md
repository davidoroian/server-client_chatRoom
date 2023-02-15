# Server application

This is a client-server chat application that accepts multiple connections and has the following functionalities (can be also seen using '/help' command in the chat):

```
"These are the available commands:\n" \
        "\t@[username/group] [message] - send a message to a user or a group\n" \
        "\t/help - get help\n" \
        "\t/users - lists existing usernames with status\n" \
        "\t/groups - lists your available groups\n" \
        "\t/group [groupname]- lists the users and admins in that specific group\n" \
        "\t/create group [groupname] - creates an empty group with you as admin\n" \
        "\t/add [groupname] [username]- adds a user to a group, if you are an admin there\n" \
        "\t/make admin [groupname] [username] - adds username to admin group for specific group\n"
```