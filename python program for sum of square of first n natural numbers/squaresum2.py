#Method 2: 
def squaresum1(n):
    return (n*(n+1)*(2*n+1))/6
n=500000 # max length support upto 5 digit
print(squaresum1(n)) 


#method 3
def squaresum3(n):
   return int((n*(n+1)*(2*n+1))/6)
n=50000000000 
print(squaresum3(n))

