print("\nSIMPLE CALCULATOR")

a = float(input("Enter the 1st number: "))
b = float(input("Enter the 2nd number: "))
o = input("Enter the operator: ")

if o == "+":
    c = a + b
    print(f"Result: {a} + {b} = {c}\n")
elif o == "*":
    c = a * b
    print(f"Result: {a} * {b} = {c}\n")
elif o == "-":
    c = a - b
    print(f"Result: {a} - {b} = {c}\n")
elif o == "/":
    c = a / b
    print(f"Result: {a} / {b} = {c}\n")
else:
    print(f"{o} is not a valid operator")
