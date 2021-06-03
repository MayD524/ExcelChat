import string
import math
import time

def expand_string(string_to_expand, lenght):
    return (string_to_expand *  (int(lenght/len(string_to_expand)) + 1))[:lenght]


def EHash(string:str, salt_string:str) -> str:
    hash_string = "" ## the output string
    
    if len(salt_string) != len(string):
        salt_string = expand_string(salt_string, len(string))
        
    for i in range(len(string)):
        string_char = ord(string[i])
        salt_char = ord(salt_string[i])
        temp = (string_char * salt_char)# // len(string)
        
        if (temp % 10) %  2 != 0:
            temp = temp // len(string)
            temp = temp << 2
        else:
            temp = temp >> 2
        hash_string += chr(temp)
    
    return hash_string