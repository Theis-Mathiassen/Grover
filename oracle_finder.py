import random


def number_to_binary_array(number, array_size):
  """
  Converts a number into a fixed-size array (list) of binary integers.

  Args:
    number: The integer to convert.
    array_size: The desired size of the output binary array.

  Returns:
    A list of integers (0s and 1s) representing the binary number,
    padded with leading zeros to fit the array_size.
    Returns an error message string if the binary representation exceeds array_size.
  """
  if not isinstance(number, int) or not isinstance(array_size, int):
    return "Error: Both number and array_size must be integers."
  if number < 0:
    return "Error: Number must be non-negative for this conversion."
  if array_size <= 0:
    return "Error: array_size must be a positive integer."

  # 1. Convert to binary string and 2. remove "0b" prefix
  binary_string = bin(number)[2:]

  # Check if the binary representation is too large for the array_size
  if len(binary_string) > array_size:
    return f"Error: Binary representation of {number} ({binary_string}) exceeds array_size of {array_size}."

  # 3. Pad with leading zeros
  padded_binary_string = binary_string.zfill(array_size)

  # 4. Convert each character to an integer and 5. store in a list
  binary_array = [int(bit) for bit in padded_binary_string]

  return binary_array

def do (func, data, i0, i1, i2):
    if func == n:
        data[i2] = func(data[i0])
    else:
        data[i2] = func(data[i0], data[i1])


# not
def n (x):
    return 1 if x == 0 else 0
# and
def a (x1, x2):
    return x1 * x2
# or
def o (x1, x2):
    return min(x1 + x2, 1)
# xor
def x (x1, x2):
    return 0 if x1+x2 == 2 else x1+x2





def oracle (input, confs, size):
    for i in range(num_iter):
        current_conf = confs[i]
        operation_type = current_conf[0]
        param_1 = current_conf[1]
        param_2 = current_conf[2]
        param_3 = current_conf[3]
        if operation_type == 0:
            do(n, input, param_1, param_2, param_3)
        elif operation_type == 1:
            do(a, input, param_1, param_2, param_3)
        elif operation_type == 2:
            do(o, input, param_1, param_2, param_3)
        elif operation_type == 3:
            do(x, input, param_1, param_2, param_3)
        else:
            print(f"Unknown operation type: {operation_type}")
        









found_config = False
lowest_hits = 256
for i in range(1):
    if found_config == False:
        bits = [0,0,0,0,0,0,0,0]
        size = 8

        num_iter = 16
        #confs = [[random.randint(0, 3)] + [random.randint(0, 7) for _ in range(3)] for _ in range(num_iter)]
        confs =[[2,4,0,7],[2,5,6,0],[3,7,1,1],[3,7,4,4],[3,4,1,3],[3,4,2,4],[1,3,1,3],[1,4,2,1],[1,3,0,5],[2,6,1,6],[0,5,0,4],[0,5,2,5],[2,6,0,2],[0,0,6,3],[1,7,4,4],[1,5,6,3]]
        print(confs)

        hits = 0
        for i in range(pow(2,8)):
            bits = number_to_binary_array(i,8)
            #print(bits)
            oracle(bits, confs, 8)
            if (bits[0] == 0 and bits[1] == 0 and bits[2] == 0):
                hits += 1
            #print(bits)
            #input()
        if hits < lowest_hits:
            lowest_hits = hits

        if hits < 16 and hits > 1:
           found_config = True

        
    else:
        print(confs)
        print(hits)
        break

print(lowest_hits)




