import time
import random

chars = "ABCDEFGHIJKLMNOPQWVZXY "


p = input("Enter your password: ")

guess = ""

while guess != p:
    guess = ""
    for i in range(len(p)):
        guess += random.choice(chars)
    print(guess)
    time.sleep(0.00000000000000000000000000000000001)

print(f"Password is {p}")