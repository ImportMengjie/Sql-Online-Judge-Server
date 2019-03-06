package main1

import (
	"log"

	"github.com/xwb1989/sqlparser"
)

func main() {
	sql := "select * from table where table.a='123'"
	sql = "SELECT * FROM t WHERE a = 'abc'"
	stmt, err := sqlparser.Parse(sql)
	if err != nil {
		log.Println(err)
	}
	switch stmt := stmt.(type) {
	case *sqlparser.Select:
		log.Println(stmt.SelectExprs)
	}

}
