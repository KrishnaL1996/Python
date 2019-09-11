def isarmstrong(value):
    l=len(value)
    temp=int(value)
    n=temp
    sum1=0
    while temp>0:
        r=temp%10
        sum1+=pow(r,l)
        temp//=10
    return sum1==n

x=input("Enter the number : ")

if isarmstrong(x):
    print(x,"is a armstrong number")
else:
    print(x,"is not a armstrong number")

    
