 def fib(n):
        if n<0:
            print("Incorrect input")
         # First Fibonacci number is 0 
        elif n==1:
             return 0
        elif n==2:
            return 1
        else: return fib(n-1)+fib(n-2)
        
n= int(input("enter the number:"))       
print("fibonacii of",n,"is", fib(n))
