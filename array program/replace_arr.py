#
def rearr(m,a):

    for n in range(len(a)):
            if(a[n]==-1):
                a[n]=(a[n-1]+1)%m
            print("iteration ",n,a)
    return a[n]
a=[5,-1,7,-1,9,0]
m=int(input("Enter the integer: "))
rearr(m,a)
print("final array",a,"\n")

b=[5, -1, -1, 1, 2, 3]
n=m=int(input("Enter the integer: "))
rearr(n,b)
print("final array",b)
