#SHOPPING LIST

your_cart = []
foods = {"Apple": 3.17, "Banana":4.00, "Cherry":2.50,"Tomato":2.15,"Cucumber":2.16,"Eggplant":4.15,"Hamburger":3.50,"Fries": 2.45 ,"Soda": 5.00 }
price = 0

print("----------------------Welcome To the Python Shopping Centre------------------------------")
for food,p in foods.items():
    print(f"{food} : {p}")

def print_cart():
    print(" ")
    print(your_cart)
    print(f"Total Price: {price}$")




def Add_Cart():
    global price
    c = input("Enter the name of the item you want to add q to quit: ")
    while True:
        if c in foods.keys():
            your_cart.append(c)
            price += foods.get(c)

            print(your_cart)
        elif c.lower() == "q":
            break

        else:
            print("Enter something existed in the foods list")
        c = input("Enter the name of the item you want to add : ")


def Remove_Cart():
    global price
    print(your_cart)
    b = input("Enter the name of the item you want to remove q to quit :  ")
    while b in your_cart:
        if b.lower() == "q":
            break
        else:
            your_cart.remove(b)
            price = price - foods.get(b)
        print(your_cart)
        b = input("Enter the name of the item you want to remove q to quit :  ")


def main():

    while True:
        print(" \n")
        print("Please enter a number")
        print("1. Add cart")
        print("2 Remove cart")
        print("3 Display cart")
        print("4 Exit")
        a = int(input("Enter your choice: "))
        if a == 1:
            Add_Cart()

        elif a == 2:
            Remove_Cart()
        elif a == 3:
            print_cart()
        elif a == 4:
            print("Exiting...")
            break
        else:
            print("Please enter a valid choice")

if __name__ == "__main__":
    main()

