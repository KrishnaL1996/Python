#method 3:
sum = lambda n : 1 if n==1 else n**2 + sum(n-1)
sum(500) # max length support upto 3 digit
