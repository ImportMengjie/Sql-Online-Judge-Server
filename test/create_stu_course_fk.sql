
CREATE TABLE `sql_online_judge`.`stu_course_fk` (
  `student` INT NOT NULL,
  `course` INT NOT NULL,
  `score` VARCHAR(20) NULL,
  `semester` VARCHAR(45) NULL,
  PRIMARY KEY (`student`, `course`),
  INDEX `course_idx` (`course` ASC) VISIBLE,
  CONSTRAINT `student`
    FOREIGN KEY (`student`)
    REFERENCES `sql_online_judge`.`student` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `course`
    FOREIGN KEY (`course`)
    REFERENCES `sql_online_judge`.`course_fk` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
