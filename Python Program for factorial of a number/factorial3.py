def factorial(k):
    if (k==0 or k == 1):
        return 1
    else:
         f = k*factorial(k-1)
         print("factorial of {} is {}".format(k,f))
    return f

k=input("enter the number: ")
factorial(int(k))
