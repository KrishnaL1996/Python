#Left rotate
#method 1
a1 = [1,2,3,4,5,6,7]
d=2
l=len(a1)
x=a1[d:l]+a1[0:d]
print(x)


#method 2 using function
def lrot(arr,l):
    d=int(input("Enter the step to rotate:"))
    l=len(arr)
    return  arr[d:l]+arr[0:d]
arr=[1,2,3,4,5,6,7]
ans=lrot(arr,l)
print("left rotate:",ans)

