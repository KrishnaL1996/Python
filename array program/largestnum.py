#method 1

n= int(input("enter the number of element: "))
arr=[]

for i in range(1,n+1):
    b=int(input("Enter the element: "))
    arr.append(b)
arr.sort()
print("Largest element is:",arr[-1])


#method 2
c=[12,15,174,146,15]
c.sort()
print("Largest element is:",c[-1])
