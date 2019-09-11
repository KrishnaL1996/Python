def fib1(n):
    if n<0:
        return False
    elif n==1:
        return 0
    elif n==2:
        return 1
    else: return fib1(n-1)+fib1(n-2)
    
for n in range(1,35):
    print(n, ":",fib1(n))
