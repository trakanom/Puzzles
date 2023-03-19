import base64
input = "72bca9b68fc16ac7beeb8f849dca1d8a783e8acf9679bf9269f7bf"
decoded = bytes.fromhex(input)
encoded = base64.b64encode(decoded)
print(encoded)