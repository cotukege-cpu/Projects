#Number Guessing Game
import random

number = random.randint(1, 100)
tries = 0
print("-----------------------WELCOME TO GUESS THE NUMBER GAME------------------------")
while True:
    guess= int(input("Guess the number! :  "))
    if guess == number:
        print("You guessed the number Right!")
        print(f"Total tries: {tries} ")
        break
    elif guess < number:
        print("Too low!")
        tries += 1
    elif guess > number:
        print("Too high!")
        tries += 1
    else:
        print("Enter a number between 1 and 100")

