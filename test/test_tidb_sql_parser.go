package main

import _ "github.com/pingcap/tidb/types/parser_driver"

import (
	"fmt"

	"github.com/pingcap/parser"
	"github.com/pingcap/parser/ast"
)

type visitor struct{}

func (v *visitor) Enter(in ast.Node) (out ast.Node, skipChildren bool) {
	fmt.Println(in.Text())
	fmt.Printf("%T\n", in)
	return in, false
}

func (v *visitor) Leave(in ast.Node) (out ast.Node, ok bool) {
	return in, true
}

func main() {

	sql := "SELECT emp_no, first_name, last_name " +
		"FROM employees " +
		"where last_name='Aamodt' and gender='F' and birth_date > '1960-01-01'"

	sqlParser := parser.New()
	stmtNodes, _, err := sqlParser.Parse(sql, "", "")
	if err != nil {
		fmt.Printf("parse error:\n%v\n%s", err, sql)
		return
	}
	for _, stmtNode := range stmtNodes {
		v := visitor{}
		stmtNode.Accept(&v)
	}
}
