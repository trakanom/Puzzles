input = "label"
#convert from string to char array
#from chars to int
#xor with int 13
midpoint = [ord(x) ^ 13 for x in input]
#convert back to string
output = [chr(x) for x in midpoint]
output = "".join(output)
print(output)
