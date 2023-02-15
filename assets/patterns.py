import re

string_dm = r'@(\w+)\s(.+)'
pat_dm = re.compile(string_dm)

string_help = r'/help'
pat_help = re.compile(string_help)

string_users = r'/users'
pat_users = re.compile(string_users)

string_group_create = r'/create\sgroup\s(\w+)'
pat_group_create = re.compile(string_group_create)

string_group = r'/group\s(\w+)'
pat_group = re.compile(string_group)

string_groups = r'/groups'
pat_groups = re.compile(string_groups)

string_group_add = r'/add\s(\w+)\s(\w+)'
pat_group_add = re.compile(string_group_add)

string_sender = r'(\w+)\s>\s(\w+)'
pat_sender = re.compile(string_sender)