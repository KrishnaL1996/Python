#method 1
def array1(arr,n1):
    mul=1
    for i in arr:
        mul*=i
    return mul%n1    
arr=[100, 10, 5, 25, 35, 14 ]
m=int(input("Enter the number divide by number:"))
print("Remainder of array multiplication divided by", m ,":",array1(arr,m))


#method 2 
def findremainder(arr, l, n): 
    mul = 1
  
    # find the individual remainder and multiple with mul. 
    for i in range(l):  
        mul = (mul * (arr[i] % n))  
        #print("array element",i,arr[i]," remainder of individual element is",arr[i] % n,":","mul",mul)
        print("array element{:>2} : {:<3}, remainder of individual element is {:<2} and multiplication result is {}".format(i,arr[i],arr[i] % n,mul))
    return mul % n 
  
# Driven code 
arr = [ 100, 10, 5, 25, 14, 35 ] 
l = len(arr) 
n = 11
  
# print the remainder of after multiple all the numbers 
print( "array remainder is",findremainder(arr, l, n)) 
