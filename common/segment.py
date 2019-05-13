import moz_sql_parser
import sqlparse
import re


class Segment:
    punctuation = ']!"#$%&\'()*+,\-/:;<=>?@[\\^`{|}~'
    pattern_punctuation = re.compile('(<>|>=|<=|!=|==|[' + punctuation + '])')

    @staticmethod
    def is_number(word: str):
        if word.isdecimal():
            return True
        try:
            float(word)
            return True
        except:
            return False

    @staticmethod
    def is_word(word: str):
        if Segment.is_number(word) or word.strip('_').isalpha() or word.count('.') == 1:
            return True
        else:
            return False

    @staticmethod
    def count_dict(data):
        count = 0
        if type(data) != dict:
            return 1
        for k, v in data.items():
            count += 1
            if type(v) in [str, int, float]:
                count += 1
            elif type(v) == list:
                for i in v:
                    count += Segment.count_dict(i)
            elif type(v) == dict:
                count += Segment.count_dict(v)
        return count

    @staticmethod
    def split_word(sql: str):
        span = sql.split()
        segment_span = []
        segment_word = []

        for segment in span:
            if Segment.is_word(segment):
                segment_span.append(segment)
                segment_word.append(segment)
            else:

                _split = Segment.pattern_punctuation.split(segment)
                _split = filter(lambda x: x != '', _split)
                for s in _split:
                    segment_word.append(s if Segment.pattern_punctuation.fullmatch(s) is None else None)
                    segment_span.append(s)
        return segment_span, segment_word

    def __init__(self, sql: str, format=True):
        self.origin_sql = sql
        sql = self.origin_sql
        if format:
            sql = sqlparse.format(sql, keyword_case='upper')
        self.format_sql = sql
        self.segment_span, self.segment_word = Segment.split_word(self.format_sql)

    @staticmethod
    def handle_list(segment_list: list, current_index: int, data: list):
        result_list = []
        for i in data:
            if type(i) == dict:
                temp_list, current_index = Segment.handle_dict(segment_list, current_index, i)
                if temp_list is not None:
                    result_list.extend(temp_list)
            elif type(i) == list:
                temp_list, current_index = Segment.handle_list(segment_list, current_index, i)
                if temp_list is not None:
                    result_list.extend(temp_list)
            else:
                result_list.append(current_index)
                current_index += 1
        return None if len(result_list) == 0 else result_list, current_index

    @staticmethod
    def handle_dict(segment_list: list, current_index, data: dict):
        result_list = []
        for k, v in data.items():
            if k == 'value':
                if type(v) == str:
                    return [current_index], current_index + 1
                elif type(v) == dict:
                    result_list.extend([i for i in range(current_index, current_index + Segment.count_dict(v))])
                    current_index += Segment.count_dict(v)
                else:
                    raise Exception('value key is not dic or str')

            elif type(v) == list:
                index = len(segment_list)
                segment = []
                if k not in ['eq', 'neq', 'gt', 'lt', 'gte', 'lte']:
                    segment = [current_index]
                    current_index += 1
                if k in ['and', 'or', 'eq', 'neq', 'lt', 'gte', 'lte']:
                    handle_list_ret, current_index = Segment.handle_list(segment_list, current_index, v)
                    if handle_list_ret is not None:
                        segment.extend(handle_list_ret)
                    result_list.extend([] if len(segment)==0 else segment)
                else:
                    index = len(segment_list)
                    segment_list.append(segment)
                    handle_list_ret, current_index = Segment.handle_list(segment_list, current_index, v)
                    if handle_list_ret is not None:
                        segment_list[index].extend(handle_list_ret)
                # else:
                #     handle_list_ret, current_index = Segment.handle_list(segment_list, current_index, v)
                #     result_list.extend([] if handle_list_ret is None else handle_list_ret)

            elif type(v) == dict:
                index = len(segment_list)
                segment = [current_index]
                current_index += 1
                segment_list.append(segment)
                handle_dict_ret, current_index = Segment.handle_dict(segment_list, current_index, v)
                if handle_dict_ret is not None:
                    segment_list[index].extend(handle_dict_ret)

            elif type(v) in [str, int, float]:
                segment_list.append([current_index, current_index + 1])
                current_index += 2
            else:
                raise Exception('error type:{} data:{}'.format(type(v), v))
        return None if len(result_list) == 0 else result_list, current_index


if __name__ == '__main__':
    sql = 'SELECT COUNT(DISTINCT student_class) FROM t_student'
    sql = 'select name,sb from student'
    sql = 'select * from sc,student where sc.Sno=student.Sno and sc.Cno=sc.Sno'
    sql = 'SELECT student_class,AVG(student_age) FROM t_student GROUP BY (student_class) HAVING AVG(student_age)>=20'
    print(Segment.split_word(sql))
    ret = []
    data = moz_sql_parser.parse(sql)
    data = {'having': {'gte': [{'avg': 'student_age'}, 20]}}
    print(data)
    Segment.handle_dict(ret, 0, data)
    print(ret)
