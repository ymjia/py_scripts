import pdb
import re
import os
import sys
from operator import itemgetter




def read_config_list(config_str, pattern):
    lc = len(config_str)
    lp = len(pattern)
    if lc < lp:
        return None
    if config_str[0:lp] != pattern:
        return None
    return config_str[lp+1:].split(" ")


def read_compare_config(file_config):
    if not os.path.exists(file_config):
        return None
    case_list = []
    ver_list = []
    alg_list = []
    content = None
    with open(file_config, encoding='utf-8') as f:
        content = f.readlines()
    print(content)
    str_list = [l.strip() for l in content]
    for line in str_list:
        if line[0:3] == "cas":
            case_list = read_config_list(line, "cas")
        elif line[0:3] == "ver":
            ver_list = read_config_list(line, "ver")
        elif line[0:3] == "alg":
            alg_list = read_config_list(line, "alg")
    return case_list, ver_list, alg_list


def regex_cid(in_str):
    m = re.search('.*([\d]{8}[\d\+/\-]*).*', in_str)
    if m:
        return m.group(1)
    return ""

t_list = [(1, 0, 2)]
t_list.append((1, 3, 4))
t_list.append((2, 3, 6))
t_list.append((3, 1, 6))
t_list.append((4, 3, 8))
t_list.append((1, 4, 9))
t_list.append((2, 1, 10))
t_list.sort(key=itemgetter(0,1))
print(t_list)


# print(regex_cid("33281812/2/12/3"))
# print(regex_cid("12382918/2+12/3aad"))

# print(regex_cid("25255357SH Florentia  VAT"))
# print(regex_cid("03679595TJOL VAT"))
# print(regex_cid("12579697HZ XiashaVAT"))
# print(regex_cid("12579337HZ XiashaVAT"))
# print(regex_cid("26059211YYC VAT"))
# print(regex_cid("02916156CSOL  VAT"))
# print(regex_cid("01875882TJ Yansha  VAT"))
# print(regex_cid("12929664SH Qingpu  VAT"))
# print(regex_cid("12929204SH Qingpu  VAT"))
# print(regex_cid("23261207+23261631BJOL VAT"))
# print(regex_cid("26843745BJOL VAT"))
# print(regex_cid("69771462BJOL VAT"))
# print(regex_cid("23261632BJOL VAT"))
# print(regex_cid("02695779BJOL VAT"))
# print(regex_cid("11826456JN Bailian VAT"))
# print(regex_cid("11826605JN Bailian VAT"))
# print(regex_cid("01202775SYOL  VAT"))
# print(regex_cid("09825544HF Sesseur VAT"))
# print(regex_cid("00827421+20Harbin VAT"))
# print(regex_cid("49802471-72WXOL VAT"))
# print(regex_cid("49803212-13WXOL VAT"))
# print(regex_cid("32500205NJ Tangshan  VAT"))
# print(regex_cid("32500507NJ Tangshan  VAT"))
# print(regex_cid("01066968+938+7114GZ Yuexiu VAT"))
# print(regex_cid("01066966-97GZ Yuexiu VAT"))
# print(regex_cid("35181881+01071106-05GZ Yuexiu VAT"))
# print(regex_cid("35997827Foshan  VAT"))
# print(regex_cid("35998007Foshan  VAT"))
