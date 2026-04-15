import random
import string

length = int(input("Enter password length: "))

letters = string.ascii_letters
digits = string.digits
symbols = string.punctuation

password = [
    random.choice(letters),
    random.choice(digits),
    random.choice(symbols)
]

for i in range(length - 3):
    password.append(random.choice(letters + digits + symbols))

random.shuffle(password)

print("Generated Password:", "".join(password))