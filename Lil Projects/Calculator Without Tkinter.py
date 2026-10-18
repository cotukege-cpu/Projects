def add(a,b):
    return a+b

def subtract(a,b):
    return a-b
def multiply(a,b):
    return a*b
def divide(a,b):
    if b == 0:
        raise ZeroDivisionError("Divide by zero")
    else:
        return a/b




def main():
    print("Welcome to Calculator")
    print("---------------------------------------------------------------------------")
    print("The EQUATIONS :  (+,-,/,*,*)")

    while True:
        start = input("press q to quit // o to go on :")
        if start.lower() == "q":
            print("quitting")
            break
        elif start.lower() == "o":
            a = int(input("Enter the first number: "))

            eq = input("Enter the equation: ")

            b = int(input("Enter the second number: "))

            answer = calculate(a,eq,b)
            if answer == int(answer):
                print(int(answer))


        else:
            raise("Wrong input, enter either o or q")




def calculate(a,eq,b):
    if eq == "+":
        return add(a,b)
    elif eq == "-":
        return subtract(a,b)
    elif eq == "*":
        return multiply(a,b)
    elif eq == "/":
        return divide(a,b)
    else:
        raise ValueError("Invalid equation")


if __name__ == "__main__":
    main()
