import sqlparse
from moz_sql_parser import parse
import json


stm = 'Select * from  student where student.score>10 and student.name<>1 or (1==1 and 1==1) order by name'



query ="""
select id,fname,lname,address from res_users as r left join res_partner as p on p.id=r.partner_id where name = (select name from res_partner where id = 1) """

query1 = "select id from Student,SC where Student.Sno!=SC.Sno"
query2 = "select id from Student,SC where SC.Sno<>Student.Sno"


query_join1="select * from student join stu_course_fk on(stu_course_fk.student=student.id) join course_fk on(stu_course_fk.course=course_fk.id)"

query_join2="select * from student,stu_course_fk,course_fk where student.id = stu_course_fk.student and stu_course_fk.course=course_fk.id"

print(query1)
print(json.dumps(parse(query1),indent=2))
print(query2)
print(json.dumps(parse(query2),indent=2))

print(query_join1)
print(json.dumps(parse(query_join1),indent=2))

print(query_join2)
print(json.dumps(parse(query_join2),indent=2))