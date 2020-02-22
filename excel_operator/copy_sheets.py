# -*- coding: utf-8 -*-

def copy_sheet(path_from, path_to, sheet_name):
    wb_from = openpyxl.load_workbook(path_from) 
    sheet_list = wb_from.sheetnames
    if sheet_name not in sheet_list:
        print("Error! no sheet {} in file {}".format(sheet_name, excel_from))
        return
    ws_from = wb_from[sheet_name]

    wb = openpyxl.load_workbook(path_to)
    try:
        ws = wb[sheet_name]
        wb.remove(ws)
    except KeyError:
        pass
    sheet = wb.create_sheet(title=sheet_name,index=13)

    for rid, r in enumerate(ws_from.iter_rows(values_only=True)):
        for cid, cell_v in enumerate(r):
            sheet.cell(row=rid+1, column=cid+1).data_type = "s"
            sheet.cell(row=rid+1, column=cid+1).value = cell_v
    wb.save(path_to)
    print("{} copyed from {} to {}".format(sheet_name, path_from, path_to))

for filename_from in filelist_from:
    for filename_to in filelist_to:
        company_from = ""
        company_to = ""
        try:
            company_from = filename_from[0:filename_from.index('2')]
            if filename_to[0:4] != "2020":
                continue
            company_to = filename_to[4:filename_to.index('科')]
        except ValueError:
            continue
            
        if company_from != company_to:
            continue
        excel_from=os.path.join(path_from,filename_from)
        excel_to=os.path.join(path_to,filename_to)
        sheet_name = "TB {}".format(time)
        copy_sheet(excel_from, excel_to, sheet_name)
