import moz_sql_parser
import sqlparse
import re


class Segment:
    punctuation = ']!"#$%&\'()+,\-/:;<=>?@[\\^`{|}~'
    pattern_punctuation = re.compile(r'(<>|>=|<=|!=|==|[' + punctuation + '])')

    @staticmethod
    def filter_segment_punctuation(segment_str: str) -> str:
        ret = segment_str.replace(')', '')
        ret = ret.replace('(', '')
        ret = ret.strip()
        return ret

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
        if Segment.is_number(word) or word.strip('_').isalpha():
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
        sql = sql.replace('GROUP BY', 'GROUP_BY')
        sql = sql.replace('ORDER BY', 'ORDER_BY')
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
        self.segment_index = []
        self.origin_sql = sql
        self.segment = []
        self.segment_str = []
        sql = self.origin_sql
        if format:
            sql = sqlparse.format(sql, keyword_case='upper')
        self.format_sql = sql
        print('format sql: ', self.format_sql)
        self.segment_span, self.segment_word = Segment.split_word(self.format_sql)
        print('segment span', self.segment_span)
        print('segment word', self.segment_word)
        self.moz_data = moz_sql_parser.parse(self.origin_sql)
        print('moz_data', self.moz_data)
        Segment.handle_dict(self.segment_index, 0, self.moz_data)
        print('segment index', self.segment_index)
        self.gen_segment()

    def gen_segment(self):
        idx_word_map = {}
        idx = 0
        for i, word in enumerate(self.segment_word):
            if word is not None:
                idx_word_map[idx] = word
                idx += 1
        idx_sql_span = 0
        print('idx_word_map ', idx_word_map)
        for segment in self.segment_index:
            self.segment.append([])
            for word_idx in segment:
                while self.segment_word[idx_sql_span] is None:
                    self.segment[-1].append(self.segment_span[idx_sql_span])
                    idx_sql_span += 1
                self.segment[-1].append(idx_word_map[word_idx])
                idx_sql_span += 1
            while idx_sql_span < len(self.segment_span) and self.segment_span[idx_sql_span] in [')', '"', "'", '>', '}',
                                                                                                ']']:
                self.segment[-1].append(self.segment_span[idx_sql_span])
                idx_sql_span += 1
        self.segment_str.extend([' '.join(i) for i in self.segment])
        print('segment result')
        for i in self.segment_str:
            print(i)

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
            if k in ['value', 'literal']:
                if type(v) == str:
                    return [current_index], current_index + 1
                elif type(v) == dict:
                    result_list.extend([i for i in range(current_index, current_index + Segment.count_dict(v))])
                    current_index += Segment.count_dict(v)
                else:
                    raise Exception('value key is not dic or str')

            elif type(v) == list:
                segment = []
                if k not in ['eq', 'neq', 'gt', 'lt', 'gte', 'lte']:
                    segment = [current_index]
                    current_index += 1
                if k in ['and', 'or', 'eq', 'neq', 'lt', 'gte', 'lte', 'gt']:
                    handle_list_ret, current_index = Segment.handle_list(segment_list, current_index, v)
                    if handle_list_ret is not None:
                        segment.extend(handle_list_ret)
                    result_list.extend([] if len(segment) == 0 else segment)
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
                if k in ['avg', 'count']:
                    result_list.extend([current_index, current_index + 1])
                else:
                    segment_list.append([current_index, current_index + 1])
                current_index += 2
            else:
                raise Exception('error type:{} data:{}'.format(type(v), v))
        return None if len(result_list) == 0 else result_list, current_index


if __name__ == '__main__':
    sql = 'SELECT COUNT(DISTINCT student_class) FROM t_student'
    sql = 'select name,sb from student'
    sql = 'select * from sc,student where sc.Sno=student.Sno and sc.Cno=sc.Sno'
    sql = "select ename,deptno,sal from emp where deptno=(select deptno from dept where loc='NEWYORK')"
    sql = 'SELECT student_class,AVG(student_age) FROM t_student GROUP BY (student_class) HAVING AVG(student_age)>=20'
    # print(Segment.split_word(sql))
    # ret = []
    # data = moz_sql_parser.parse(sql)
    # # data = {'having': {'gte': [{'avg': 'student_age'}, 20]}}
    # print(data)
    # Segment.handle_dict(ret, 0, data)
    # print(ret)
    sql = 'select * from sc where sc.Sno=1'
    # sql = 'select * from sc join student on sc.Sno in (select Sno from student) '
    sql = ' SELECT * FROM sc, student WHERE sc.Sno=student.Sno AND sc.Grade >60'
    s = Segment(sql)
    import json

    print(json.dumps({'select': [{'value': 'student_class'}, {'value': {'avg': 'student_age'}}], 'from': 't_student',
                      'groupby': {'value': 'student_class'}, 'having': {'gte': [{'avg': 'student_age'}, 20]}},
                     indent=4))
