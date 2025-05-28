package main

import "testing"

func TestOracleNegZero(t *testing.T) {
	var conf = [][]int{{0, 0, 0, 0}}
	var want = 0x1
	result := Oracle(0x0, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleNegOne(t *testing.T) {
	var conf = [][]int{{0, 0, 0, 0}}
	var want = 0x0
	result := Oracle(0x1, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}

func TestOracleAndZero(t *testing.T) {
	var conf = [][]int{{1, 0, 1, 2}}
	var want = 0b00100000
	result := Oracle(0b00100000, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleAndOne(t *testing.T) {
	var conf = [][]int{{1, 0, 1, 2}}
	var want = 0b00100001
	result := Oracle(0b00100001, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleAndTwo(t *testing.T) {
	var conf = [][]int{{1, 0, 1, 2}}
	var want = 0b00100010
	result := Oracle(0b00100010, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleAndThree(t *testing.T) {
	var conf = [][]int{{1, 0, 1, 2}}
	var want = 0b00100111
	result := Oracle(0b00100011, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}

func TestOracleOrZero(t *testing.T) {
	var conf = [][]int{{2, 0, 1, 2}}
	var want = 0b00100000
	result := Oracle(0b00100000, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleOrOne(t *testing.T) {
	var conf = [][]int{{2, 0, 1, 2}}
	var want = 0b00100101
	result := Oracle(0b00100001, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleOrTwo(t *testing.T) {
	var conf = [][]int{{2, 0, 1, 2}}
	var want = 0b00100110
	result := Oracle(0b00100010, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleOrThree(t *testing.T) {
	var conf = [][]int{{2, 0, 1, 2}}
	var want = 0b00100111
	result := Oracle(0b00100011, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}

func TestOracleXorZero(t *testing.T) {
	var conf = [][]int{{3, 0, 1, 2}}
	var want = 0b00100000
	result := Oracle(0b00100000, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleXorOne(t *testing.T) {
	var conf = [][]int{{3, 0, 1, 2}}
	var want = 0b00100101
	result := Oracle(0b00100001, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleXorTwo(t *testing.T) {
	var conf = [][]int{{3, 0, 1, 2}}
	var want = 0b00100110
	result := Oracle(0b00100010, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
func TestOracleXorThree(t *testing.T) {
	var conf = [][]int{{3, 0, 1, 2}}
	var want = 0b00100011
	result := Oracle(0b00100011, conf)
	if want != int(result) {
		t.Errorf(`Expected: %d, but got: %d.`, want, result)
	}
}
