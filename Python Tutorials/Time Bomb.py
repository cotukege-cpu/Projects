import time


def TimeBombFalse():
    t = 10  # in seconds

    for i in range(t, 0, -1):
        seconds = i % 60
        minutes = int(i / 60) % 60
        hours = int(i / 3600)
        print(f"{hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
    print("Boom")


def TimeBombTrue():
    print("BOMB DISARMED SUCCESSFULLY")


print("[----------------------------SECURITY SYSTEM-------------------------------]")

Password = 3524
attempts = 3

while attempts > 0:
    a = int(input(f"Enter The Password (attempts : {attempts})  "))
    if a != Password:
        print("Wrong")
        attempts -= 1
        if attempts == 0:
            TimeBombFalse()
    else:
        TimeBombTrue()
        break


