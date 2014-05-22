# coding: utf-8

import codecs


def is_order(password):

    def to_int(c):
        if c in 'abcdefghijklmnopqrstuvwxyz':
            c = ord(c)
        elif c in '0123456789':
            c = int(c)
        else:
            c = 0
        return c

    password = password.lower()

    # 正序，如： abcdef 123456
    def positive_sequence():
        c = to_int(password[0])
        for x in password:
            x = to_int(x)
            if c != x:
                return False
            c += 1
        return True

    # 反序，如： 654321
    def inverted_sequence():
        c = to_int(password[0])
        for x in password:
            x = to_int(x)
            if c != x:
                return False
            c -= 1
        return True

    if ( positive_sequence() or 
         inverted_sequence() ):
        return True

    return False


def complex_factor(password):

    sum_char = 0
    sum_int  = 0
    sum_spec = 0

    for x in password:
        if x in 'abcdefghijklmnopqrstuvwxyz':
            sum_char += 1
        if x in '0123456789':
            sum_int += 1
        if x in '''~`!@#$%^&*()_-+={[}]|\:;"'<,>.?/''':
            sum_spec += 1

    # TODO: 设计一个更完美的复杂系数计算方法
    count = 0
    if sum_char:
        count += 1
    if sum_int:
        count += 1
    if sum_spec:
        count += 1

    if count == 1:
        if not is_order(password):
            count += 1

    return count
    

def is_too_simple(password, simple_password_file=None):

    password = password.strip()

    # 太短不安全
    if len(password) < 6:
        return True

    # 简单的重复不安全
    if password[0] * len(password) == password :
        return True

    # 复杂数
    if complex_factor(password) <= 1:
        return True

    # 未指定文件就不测试
    if not simple_password_file:
        return False

    # 文件中列出的其他形式也不安全
    with codecs.open(simple_password_file, 'r', 'utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            L = line.split()
            for w in L:
                w.strip()
                if not w or w.startswith(';'):
                    continue
                if w == password:
                    return True

    return False


if __name__ == '__main__':

    import sys
    blacklist_file = sys.argv[1]

    for string in [ '666666666',
                    '123456',
                    '1234568888',
                    '654321',
                    '6543219999',
                    'abc123',
                    '3456789',
                    'abc18937',
                    'greatfirewall',
                    'oi19njn4j',
                    'boiea+94204$' ]:
        if is_too_simple(string, blacklist_file):
            print 'Simple: %s' % string
        else:
            print 'Safe: %s' % string

