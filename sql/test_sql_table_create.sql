
create table student( Sno int not null primary key, Sname char(10)not null, Ssex bit not null, Sage tinyint not null, Sdept char(20) not null)

create table course( Cno int not null primary key, Cname char(20)not null, Cpno int not null, Ccredit tinyint not null)


create table sc( Sno int not null, Cno int not null, Grade tinyint not null foreign key(Sno)references student(Sno) foreign key(Cno)references course(Cno) )



{
	"session": "b65315063d8608fd8a34a282012d3ac9cd02a0ce",
	"name1":"student",
	"name2":"course",
	"sql1":"create table student( Sno int not null primary key, Sname char(10) not null, Ssex bit not null, Sage tinyint not null, Sdept char(20) not null)",
	"sql2":"create table course( Cno int not null primary key, Cname char(20)not null, Cpno int not null, Ccredit tinyint not null)",
	"name":"sc",
	"sql":"create table sc( Sno int not null, Cno int not null, Grade tinyint not null)"
}

insert into student values(1,"王二",0,18,"啊")

insert into course values(1,"math",0,18)

insert into sc values(1,1,59)