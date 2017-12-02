"""文书信息挖掘主文件."""
import collections
import jieba
from entity import LawEntity
from main_tool import clean, get_next_line2, load_dict
from main_parse import process_title, process_type, process_number, \
    extract_relative_person, parse_cause, parse_content
from ronghui.Money.AllMoney import Get_Appeal_Judge_Money


def main_extract(file_path):
    """主入口函数."""
    rawdata = clean(file_path)
    return rawdata, extract_from_rawdata(rawdata)


def extract_from_rawdata(rawdata):
    """副入口函数."""
    data_generator = get_next_line2(rawdata)
    law_entity = extract_main(data_generator)
    return law_entity


def extract_main(data_generator):
    """主文提取."""
    load_dict()
    # 自定义分词样本，法院
    jieba.load_userdict("config/self_dict.txt")
    jieba.initialize()
    law_entity = LawEntity()
    relative_person_list = collections.OrderedDict()
    line, raw_line = next(data_generator)
    if line[-1:] == '书':
        law_entity.title_ = line  # 文书标题
        line, raw_line = next(data_generator)
    # 法院名称, 法院级别, 涉案地区, 是否涉外
    line, raw_lines = process_title(line, law_entity, data_generator)
    # 文书类型,案件性质
    line, raw_lines = process_type(line, law_entity, data_generator)
    # 案号
    line, raw_lines = process_number(line, law_entity, data_generator)
    # PARTIES = ["原告", "被告", "上诉人", "被上诉人", "第三人"]
    line, raw_line = extract_relative_person(
        line, law_entity, data_generator, relative_person_list)
    # for pp in relative_person_list:
    #     print(relative_person_list[pp])
    #     for rp in relative_person_list[pp]:
    #         print(rp.relative_)
    # 正文
    #     案由
    parse_cause(line, law_entity)
    #     专利号 抽取专利复审委的文书号 抽取商标号 抽取商标评审委的文书号 摘要 判决结果
    patentNumber = set()
    trademarkNumber = set()
    line, raw_line = parse_content(
        line, law_entity, data_generator, patentNumber, trademarkNumber)
    for role, role_list in relative_person_list.items():
        law_entity.party_.extend(role_list)
    # print(law_entity.judge_results_)
    return law_entity


if __name__ == '__main__':
    filePath = '/home/jokers/python/projects/_file/广知/5.txt'
    rawdata, law_entity = main_extract(filePath)
    print(law_entity)
    Get_Appeal_Judge_Money(law_entity, rawdata)
    print(law_entity.judge_money)
    print(law_entity.appeal_money)
