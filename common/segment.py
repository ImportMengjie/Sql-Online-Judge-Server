import moz_sql_parser
import sqlparse
import re


class Segment:

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
    def split_word(sql: str):
        span = sql.split()
        print('origin', span)
        segment_span = []
        segment_word = []
        punctuation = ']!"#$%&\'()*+,\-/:;<=>?@[\\^`{|}~'
        pattern_punctuation = re.compile('(<>|>=|<=|!=|==|[' + punctuation + '])')

        for segment in span:
            if Segment.is_word(segment):
                segment_span.append(segment)
                segment_word.append(segment)
            else:

                _split = pattern_punctuation.split(segment)
                _split = filter(lambda x: x != '', _split)
                for s in _split:
                    segment_word.append(s if pattern_punctuation.fullmatch(s) is None else None)
                    segment_span.append(s)
        return segment_span, segment_word

    def __init__(self, sql: str):
        self.origin_sql = sql


if __name__ == '__main__':
    print(Segment.split_word('select * from sc,student where sc.Sno=student.Sno'))
