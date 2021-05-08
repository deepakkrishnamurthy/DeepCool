from numpy import std, square, mean


def unsigned_to_signed(unsigned_array,N):
    signed = 0
    for i in range(N):
        signed = signed + int(unsigned_array[i])*(256**(N-1-i))
    signed = signed - (256**N)/2
    return signed

def split_int_2byte(number):
    # Most-significant-bit to Least-significant-bit
    return int(number) >> 8, int(number)%256

def split_signed_int_2byte(number):
    # Most-significant-bit to Least-significant-bit
    if abs(number) > 32767:
        number = np.sign(number)*32767

    if number!=abs(number):
        number=65536+number
    return int(number) >> 8, int(number)%256

def split_int_3byte(number):
    # Most-significant-bit to Least-significant-bit
    return int(number) >> 16, (int(number) >> 8)%256, int(number)%256 

def data2byte_to_signed_int(a,b):
    nb= a+256*b
    if nb>32767:
        nb=nb-65536
    return nb

def dataNbyte_to_int(unsigned_array, N):

    result = 0
    for i in range(N):
        result += int(unsigned_array[i])*(256**(N-1-i))

    return result