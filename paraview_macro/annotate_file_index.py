# -*- coding: utf-8 -*-
## @file annotate_file_index.py
## @brief show file_index of selected point in
## @author jiayanming


def get_field_data(vtk_obj, attr_name):
    if hasattr(data, 'GetBlock'): # multiblock data
        for b in range (0, data.GetNumberOfBlocks()):
            b_data = data.GetBlock(b)
            if not b_data: continue
            for p in range (0, b_data.GetNumberOfPoints()):
                cur_pt = b_data.GetFieldData(p)
                for j in range(0, 3):
                    avg_pt[j] += cur_pt[j]
        for j in range(0, 3):
            avg_pt[j] /= pt_num
        return avg_pt


# get selection
cur_sel = cur_source.GetSelectionOutput(cur_source.Port)
sel_data = servermanager.Fetch(cur_sel)
