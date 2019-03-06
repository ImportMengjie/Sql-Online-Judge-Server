
CREATE TABLE `sql_online_judge`.`course_fk` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `teacher` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `teacher_idx` (`teacher` ASC) VISIBLE,
  CONSTRAINT `teacher`
    FOREIGN KEY (`teacher`)
    REFERENCES `sql_online_judge`.`teacher` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
