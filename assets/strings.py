error = 'Incorrect syntax, use /help\n'

help = "These are the available commands:\n" \
        "\t@[username/group] [message] - send a message to a user or a group\n" \
        "\t/help - get help\n" \
        "\t/users - lists existing usernames with status\n" \
        "\t/groups - lists your available groups\n" \
        "\t/group [groupname]- lists the users and admins in that specific group\n" \
        "\t/create group [groupname] - creates an empty group with you as admin\n" \
        "\t/add [groupname] [username]- adds a user to a group, if you are an admin there\n" \
        "\t/make admin [groupname] [username] - adds username to admin group for specific group\n" \
        "\t/remove [groupname] [username] - remove user from specific group\n" \
        "\t/delete [groupname] - delete group if empty\n" \
        "\t/rename [groupname] [newgroupname] - rename group if new name is available\n" \
        "\t/sendfile [filepath] [username] - send file to desired user\n"