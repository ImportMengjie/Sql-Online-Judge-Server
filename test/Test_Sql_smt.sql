# 单表查询
select id-1, 'sb' wo,name from student;

select * from student where gender like 'fe%';

select count(distinct student ) from stu_course_fk;

select course, count(distinct student) from stu_course_fk group by course ;

select course, count(distinct student) from stu_course_fk group by course having count(*)>1;

select * from stduent where id!=1;

select * from student join stu_course_fk on(stu_course_fk.student=student.id) join course_fk on(stu_course_fk.course=course_fk.id);

select * from student,stu_course_fk,course_fk where student.id = stu_course_fk.student and stu_course_fk.course=course_fk.id; 