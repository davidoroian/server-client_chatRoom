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

string_make_admin = r'/make\sadmin\s(\w+)\s(\w+)'
pat_make_admin = re.compile(string_make_admin)

string_remove = r'/remove\s(\w+)\s(\w+)'
pat_remove = re.compile(string_remove)

string_delete_group = r'/delete\s(\w+)'
pat_delete_group = re.compile(string_delete_group)

string_rename_group = r'/rename\s(\w+)\s(\w+)'
pat_rename_group = re.compile(string_rename_group)

string_send_file = r'/sendfile\s([^\s]+)\s(\w+)'
pat_send_file = re.compile(string_send_file)

string_request_file_access = r'/sendfile\s([^\s]+)\s(\w+)\s(\w+)'
pat_request_file_access = re.compile(string_request_file_access)

string_accept = r'/accept'
pat_accept = re.compile(string_accept)

string_size = r'.*USER:\s([^|]+)\s\|\sFILE:\s([^|]+)\s\|\sSIZE:\s(\d+).*'
pat_size = re.compile(string_size)