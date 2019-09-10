def factorial(k):
    if k ==1:
        return 1
    else:
        return k * factorial(k-1)
k=input("enter the number: ")
f = factorial(int(k))
print("factorial of ",k ,"is",f)
