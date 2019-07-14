import re

def regex_cid(in_str):
    m = re.search('.*([0-9]{8}).*', in_str)
    if m:
        return m.group(1)


print(regex_cid("lsajf1234567898a..aslkj"))
print(regex_cid("lsajf 123456781 .12.aslkj"))
print(regex_cid("*lsajf 012345678#..aslkj"))
