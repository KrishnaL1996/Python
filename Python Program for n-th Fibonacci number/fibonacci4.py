from functools import lru_cache  #Least Recently used Cache
@lru_cache(maxsize=1000) #default 128

def fib4(n):
    #check that the input is a positive integer
    if type(n)!= int:
        raise TypeError("n must be a positive int")
    if n<0:
        raise ValueError("n must be a positive int")
    
    #compute the Nth term
    if n==1:
        return 1
    elif n==2:
        return 1
    else: return fib4(n-1)+fib4(n-2)
for n in range(1,51):
    print(fib4(n))
   # print(fib4(n+1)/fib4(n)) #golden ratio
