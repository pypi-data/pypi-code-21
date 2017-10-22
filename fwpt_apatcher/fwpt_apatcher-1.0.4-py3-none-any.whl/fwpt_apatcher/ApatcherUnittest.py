# Подготовка пакета для тестирования
# apatcherutils
# тестирование
#def main():
    # _, tr_sdk, tr_base, tr_proj = get_all_patch_files_by_nums("D:\\FProjects\\database\\sdk\\database\\patches",
    #                                                           "D:\\FProjects\\database\\billing\\database\\patches",
    #                                                           "D:\\FProjects\\DISCOVERY\\patches",
    #                                                           [189, 190, 191],
    #                                                           [1617, 1618, 1619, 1620],
    #                                                           [31, 32, 33])
    # print(tr_sdk)
    # print(tr_base)
    # print(tr_proj)
    # ls, lp, lk = parse_nums_patches_interval("[s:215-217,b:1691-1693,p:]")
    # print(ls)
    # print(lp)
    # print(lk)


#apatcherclass
#def main():
    # t = PatchPrint()
    # t.parse_from_exists("*Автор:                Куртаков А.Е.  Дата:         "
    #                     "        2016-07-05  Номер патча:          01614  Номер тикета:  "
    #                     "       10801  Новые объекты:   Измененные объекты:   pack_bill  Удаленные объекты: "
    #                     "     Комментарий:    "
    #                     "      Скорректировано определение уровня логирования при массовом выставлении счетов "
    #                     "(ускорено)  "
    #                     "  Создан: 2016-07-05 11:45:08    Список включённых файлов: flexy-525019.sql,"
    #                     " flexy-525051.sql, DIS_BASE_EXCHANGE.pck, DIS_SEARCH_INTERFACE.pck")
    #
    # print(t.name)
    # print(t.list_files)
    # print(t.description)
    # sarg_line = "{s:189-191,b:1617-1620,p:814-817}"
    # p1, p2, p3 = autil.parse_nums_patches_interval(sarg_line)
    # print(p1)
    # print(p2)
    # print(p3)
    # _, tr_sdk, tr_base, tr_proj = autil.get_all_patch_files_by_nums("D:\\FProjects\\database\\sdk\\database\\patches",
    #                                                                 "D:\\FProjects\\database\\billing\\database\\patches",
    #                                                                 "D:\\FProjects\\DISCOVERY\\patches",
    #                                                                 p1,
    #                                                                 p2,
    #                                                                 p3)
    # print(tr_sdk)
    # print(tr_base)
    # print(tr_proj)

#apatchergendocs
# def main():
#     generate_doc_upd_log("Богомолова А.В", "\\2016-01-01_05\\", "16 мая 2016 года", list_patch=["1.txt", "2.txt"])
#     generate_doc_changelist(project_patches=[ac.PatchPrintExt(name=str(x), description="Новый патч 2",
#                                                               list_files=["pacK_sdk.pck", "flexy-5252.sql",
#                                                                           "alma_dw.pck"])
#                                              for x in range(1, 9)],
#                             base_patches=[ac.PatchPrintExt(name=str(x), description="Новый патч 2",
#                                                            list_files=["pacK_sdk.pck", "flexy-5252.sql", "alma_dw.pck"])
#                                           for x in range(1, 20)],
#                             sdk_patches=[ac.PatchPrintExt(name=str(x), description="Новый патч 2",
#                                                           list_files=["pacK_sdk.pck", "flexy-5252.sql", "alma_dw.pck"])
#                                          for x in range(1, 4)]
#                             )


#apatchermenu
# def main():
#     p = ["m1", "m2", "m3"]
#     p = edit_list(p, 1)
#     print(p)