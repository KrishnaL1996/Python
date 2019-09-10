def factorial(n):
    # single line to find factorial
    return 1 if (n == 1 or n == 0) else n * factorial(n - 1)

n = input("enter the number: ")
print("Factorial of", n , "is", factorial(int(n)))
