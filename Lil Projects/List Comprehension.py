#List Comprehension + Unpacking



emails = ["spider.man@gmail.com","yagoz.ayran@gmail.com","Idonlikeblacks@gmail.com","Faded_x123@gmail.com"]

usernames = []
for email in emails:
    a = email.split("@")[0]
    usernames.append(a)

#print(usernames)




#Unpacking


product_info = ["Wireless Mouse","Electronics","Black","Battery included",15.99,"In Stock"]


product_name,*_,price,availability = product_info

print(f" {product_name} costs ${price} and is {availability}")