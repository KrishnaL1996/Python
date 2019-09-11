def is_prime_v3(n): 
    #return TRUE if 'n' is a prime number. FALSE otherwise
    if n==1:
        return False
    # if it's even and not 2, then it's not prime
    if n==2:
        return True
    if n>2 and n%2==0:
        return False
    
    max_divisor= math.floor(math.sqrt(n))
    for d in range(3, 1+ max_divisor,2):
         if n%d ==0:
            return False
    return True
    #==== test function

t0=time.time()
for n in range(1,100000):
    is_prime_v3(n)
t1=time.time()
print("Time required: ",t1-t0)         
