import moz_sql_parser
from common.segment import Segment

sql1 = 'select * from sc join student on (student.Sno=sc.Sno)'

sql2 = 'select * from student'

sql3 = 'select name,sb from student'

sql4 = 'select * from sc,student where sc.Sno=student.Sno'

sql5 = 'SELECT COUNT(DISTINCT student_class) FROM t_student'

sql6 = 'SELECT student_class,AVG(student_age) FROM t_student GROUP BY (student_class) HAVING AVG(student_age)>=20'

sql7 = "select ename,deptno,sal from emp where deptno=(select deptno from dept where loc='NEW YORK')"

ret1 = moz_sql_parser.parse(sql1)

ret2 = moz_sql_parser.parse(sql2)

ret3 = moz_sql_parser.parse(sql3)

ret4 = moz_sql_parser.parse(sql4)

ret5 = moz_sql_parser.parse(sql5)

ret6 = moz_sql_parser.parse(sql6)

ret7 = moz_sql_parser.parse(sql7)

print(ret1)
print(ret2)
print(ret3)
print(ret4)
print(ret5)
print(ret6)
print(ret7)


print(Segment.split_word(sql1))
print(Segment.split_word(sql2))
print(Segment.split_word(sql3))
print(Segment.split_word(sql4))
print(Segment.split_word(sql5))
print(Segment.split_word(sql6))


def isaNumberic(string: str):
    if string.isdecimal():
        return True
    try:
        float(string)
        return True
    except:
        return False


def segment_origin_sql(sql: str):
    segment_span = sql.split()
    ret = []
    for span in segment_span:
        if isaNumberic(span) or span.isalpha():
            ret.append(span)


def handleList(ret: list, key: str, data: list):
    pass
