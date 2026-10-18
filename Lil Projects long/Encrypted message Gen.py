#Message encrypting and decrypting
import string
import random


chars = " " + string.ascii_letters + string.punctuation + string.digits
chars = list(chars)
keys = chars.copy()

random.shuffle(keys)
#print(keys)


#Encrypting

text = input("Enter your message: ")
Encrypted = " "
for letter in text:
    index = chars.index(letter)
    Encrypted += keys[index]
print("----------------------------------")
print(f"Original message: {text}")
print(f"Encrypted message: {Encrypted}")



#Decrypting

plain_text = input("Enter your message: ")
Decrypted = " "
for letter in plain_text:
    index = keys.index(letter)
    Decrypted += chars[index]

print("----------------------------------")
print(f"Ciphered message: {plain_text}")
print(f"Decrypted message: {Decrypted}")
