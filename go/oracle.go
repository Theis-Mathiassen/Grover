package main

import (
	"fmt"
	"math"
	"math/rand"
	"strconv"
	"strings"
	"time"
)

const verboseDebugMode = false

// formatIntSlice2D takes a 2D integer slice and returns a string
// formatted as {{val,val,...},{val,val,...}}.
func formatIntSlice2D(data [][]int) string {
	var sb strings.Builder

	sb.WriteString("[") // Start of the outer structure

	for i, innerSlice := range data {
		sb.WriteString("[") // Start of an inner slice

		for j, val := range innerSlice {
			sb.WriteString(strconv.Itoa(val)) // Convert int to string and append
			if j < len(innerSlice)-1 {
				sb.WriteString(",") // Add comma if not the last element in innerSlice
			}
		}
		sb.WriteString("]") // End of an inner slice

		if i < len(data)-1 {
			sb.WriteString(",") // Add comma if not the last innerSlice
		}
	}

	sb.WriteString("]") // End of the outer structure
	return sb.String()
}

// Good configs:
// 8: [[3 1 1 6] [1 3 0 7] [2 3 7 6] [0 2 4 2] [3 0 6 0] [0 4 5 5] [3 7 5 3] [0 7 2 6] [3 2 4 7] [2 7 1 7] [2 3 4 5] [3 1 3 4] [3 2 1 6] [1 5 3 2] [0 3 2 0] [3 1 4 6]]
// 4: [[2 2 4 7] [1 4 4 1] [1 6 5 4] [3 6 3 7] [1 4 7 5] [2 0 2 5] [0 2 6 6] [2 2 1 6] [0 1 4 7] [2 3 7 2] [0 7 3 1] [1 2 4 6] [2 4 4 1] [2 4 7 2] [2 0 0 7] [0 1 6 7]]
// 4: [[2,4,6,3],[2,1,3,3],[2,2,3,6],[1,2,5,3]]
// 4: no_change: [[0,2,3,1],[0,5,7,2],[2,3,2,5],[2,5,6,5],[3,1,6,6],[2,7,4,7]]
// 4: no_change, output 5: [[0,3,5,0],[2,6,5,1],[2,2,0,0],[2,7,1,5],[0,7,5,7],[2,5,0,3]]

// Only AND and NOT gates
// 4: [[1,3,1,2],[1,4,5,4],[1,4,2,3],[0,3,3,5]]

func main() {
	rand.New(rand.NewSource(time.Now().UnixNano()))

	var found_config = false
	var lowest_hits = 256
	var num_iter = 4
	var confs = make([][]int, num_iter)
	var hits = 0
	for range 400000 {
		if !found_config {
			hits = 0
			//var no_change = true
			for i := range confs {
				confs[i] = []int{rand.Intn(2), rand.Intn(8), rand.Intn(8), rand.Intn(8)}
			}
			//confs = [][]int{{0, 3, 5, 0}, {2, 6, 5, 1}, {2, 2, 0, 0}, {2, 7, 1, 5}, {0, 7, 5, 7}, {2, 5, 0, 3}}

			for i := range int(math.Pow(2, 8)) {
				//for range 1 {
				//fmt.Println("Hello, World!")
				//var input = uint8(0b00001100)
				var input = uint8(i)
				if verboseDebugMode {
					fmt.Println("Configurations: ", confs)
					fmt.Printf("Input: %.8b\n", input)
				}
				var output = Oracle(input, confs, 5)
				if verboseDebugMode {
					fmt.Printf("Output: %.8b\n", output)
				}
				if output&0b11100000 == 0 {
					if verboseDebugMode {
						fmt.Println("Hit!")
					}
					hits++
				}
				if input == output {
					//no_change = false
				}
			}
			if hits < lowest_hits {
				lowest_hits = hits
			}
			if hits < 8 && hits > 1 { //&& no_change {
				found_config = true
			}
		} else {
			fmt.Println("Configurations: ", formatIntSlice2D(confs))
			fmt.Println("Hits: ", hits)
			break
		}
	}
	fmt.Println("Lowest hits: ", lowest_hits)
}

func Oracle(input uint8, confs [][]int, outSize int) uint8 {
	var output = input
	for i := range confs {

		var current_conf = confs[i]
		//fmt.Println("Conf: ", current_conf)
		//fmt.Printf("input: %.8b\n", input)
		var operationType = current_conf[0]
		var param1 = current_conf[1]
		var param2 = current_conf[2]
		var param3 = current_conf[3]
		var val1 = (output >> param1) & 0x1
		var val2 = (output >> param2) & 0x1

		switch operationType {
		case 0:
			// doOperation('n', input, param1, param2, param3)
			// Get current bit value at param1
			var curValue uint8 = (output >> param1) & 0x1

			// Flip the value (0 becomes 1, 1 becomes 0)
			var flippedValue uint8 = curValue ^ 1

			if flippedValue == 1 {
				output = output | (1 << param3)
			} else {
				output = output & ^(1 << param3)
			}
		case 1:
			// doOperation('a', input, param1, param2, param3)

			var andVal = val1 & val2

			if andVal == 1 {
				output = output | (1 << param3)
			} else {
				output = output & ^(1 << param3)
			}

		case 2:
			// doOperation('o', input, param1, param2, param3)
			// doOperation('a', input, param1, param2, param3)

			var orVal = val1 | val2

			if orVal == 1 {
				output = output | (1 << param3)
			} else {
				output = output & ^(1 << param3)
			}
		case 3:
			// doOperation('x', input, param1, param2, param3)

			var xorVal = val1 ^ val2

			if xorVal == 1 {
				output = output | (1 << param3)
			} else {
				output = output & ^(1 << param3)
			}
		default:
			fmt.Printf("Unknown operation type: %d\n", operationType)
		}
		//fmt.Printf("output: %.8b\n", output)

	}

	//fmt.Printf("%.8b", 0b10000000>>7)

	// Xor to limit to output size
	/*for i := range 8 - outSize {
		var val1 = (output >> (8 - (i + 1))) & 0x1
		var val2 = (output >> (8 - (i + 2))) & 0x1

		var xorVal = val1 ^ val2

		if xorVal == 1 {
			output = output | (1 << (8 - (i + 2)))
		} else {
			output = output & ^(1 << (8 - (i + 2)))
		}
		//fmt.Printf("Before: %.8b\n", output)
		output = output & ^(0x1 << (8 - (i + 1)))
		//fmt.Printf("After: %.8b\n", output)
	}*/

	return output
}
