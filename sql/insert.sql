INSERT INTO `sql_online_judge`.`Admin`
(`name`,
`password`)
VALUES
("admin",
"123456");
SELECT * FROM sql_online_judge.Admin;


-- create table student( Sno int not null primary key, Sname char(10) not null, Ssex bit not null, Sage tinyint not null, Sdept char(20) not null)

-- create table course( Cno int not null primary key, Cname char(20)not null, Cpno int not null, Ccredit tinyint not null)

-- create table sc( Sno int not null, Cno int not null, Grade tinyint not null)