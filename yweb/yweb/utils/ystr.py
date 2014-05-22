# coding: utf-8


def count_chars_en_zh( string ):

    '''计算给定字符串中的英文字符和中文字符个数

    注意：字符串必须是 utf-8 编码，非中文字符都当作英文字符

    返回： 英文字符数，中文字符数
    '''
    en_count = 0
    zh_count = 0

    for ch in string: # 此字符串须是 UTF-8 编码
        if u'\u4e00' <= ch <= u'\u9fff':
            zh_count += 1
        else:
            en_count += 1

    return en_count, zh_count
