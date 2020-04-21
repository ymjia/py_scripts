from winreg import *

macro_list = [
    ["apply_all_select", "Ctrl+S"],
    ["apply_all_visible", "Ctrl+V"],
    ["compare_data", "Ctrl+C"],
    ["rep_surface", "1"],
    ["rep_sur_edge", "2"],
    ["rep_points", "3"],
    ["rep_wireframe", "4"],
    ["break_apart", "Ctrl+B"],
    ["add_light", "Ctrl+A"],
    ["time_next", "Right"],
    ["time_prev", "Left"],
    ["time_play", "Down"],
    ["time_stop", "Up"],
    ["center_to_selection", "Space"],
    ["rename_view", ""],
    ["rep_texture", "5"],
    ["hausdorff_dist", "Ctrl+X, Ctrl+H"],
    ["save_select", "Ctrl+X, Ctrl+S"],
    ["clip_helper", "Ctrl+X, Ctrl+C"],
    ["dental_desk_post", "Ctrl+X, Ctrl+D"],
    ["registration", "Ctrl+X, Ctrl+R"],
    ["rename_source", "Ctrl+R"],
    ["group_together", "Ctrl+G"]]

edit_list = [
    ["Rename_Window", ""],
    ["Camera_Undo", "Alt+Z"],
    ["Camera_Redo", "Alt+Y"],
    ["Reset_Session", ""],
    ["Redo", "Ctrl+Y"]]

file_list = [
    ["Save_Data...", ""],
    ["Exit", ""]]


def set_macro_shortcuts(type_str, type_list):
    reg = ConnectRegistry(None, HKEY_CURRENT_USER)
    key = None
    try:
        key = CreateKey(reg, r"Software\ParaView\ParaView\pqCustomShortcuts\{}".format(type_str))
    except WindowsError:
        print("cannot find keys in register")
        return
    if key is None:
        return
    for ki in type_list:
        SetValueEx(key, ki[0], 0, REG_SZ, ki[1])
    CloseKey(key)


set_macro_shortcuts("Macros", macro_list)
set_macro_shortcuts("File", file_list)
set_macro_shortcuts("Edit", edit_list)
