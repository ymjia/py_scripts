
# check items with same check id
def filter_same_checkid(ver_list, am_err_list):
    am_err_list.sort(key=lambda x: x.check_id, reverse=False)
    i = 0
    total = len(am_err_list)
    while i < total:
        cur_cid = am_err_list[i].check_id
        cur_am = 0
        cur_start = i
        # collect amount of same cid
        for j in range(cur_start, total):
            if cur_cid != am_err_list[j].check_id:
                break
            cur_am += am_err_list[j].amount
            i += 1
        # compare amount
        if cur_cid not in ver_map:
            continue
        ver_pos = ver_map[cur_cid]
        v_am = ver_list[ver_pos].amount
        if not math.isclose(v_am, cur_am, abs_tol=1e-5):
            continue
        # mark verified
        ver_list[ver_pos].map_id = 0
        ver_rid = ver_list[ver_pos].rid
        for j in range(cur_start, i):
            am_err_list[j].map_id = ver_rid
