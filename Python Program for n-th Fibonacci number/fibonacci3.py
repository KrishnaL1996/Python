fibonacci_cache = {}
def fib2(n):
  # if we have cached the value, then return it  
    if n in fibonacci_cache:
        return fibonacci_cache[n]
    #compute the Nth term
    if n<0:
        return False
    elif n==1:
        return 0
    elif n==2:
        return 1
    elif n>2:
        value = fib2(n-1)+fib2(n-2)
    #cache the value and return it
    fibonacci_cache[n]=value
    return value
for n in range(1,101):
    print(n, ":",fib2(n))
    
    
    
