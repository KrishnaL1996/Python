n = int(input("Please enter a number: "))
 
num_str = str(n)
num_len = len(num_str)
 
sum_of_digits = 0
for d in num_str:
    sum_of_digits += int(d) ** num_len # power operation
 
if n == sum_of_digits:
    print("{} is an Armstrong number of order {}".format(n,num_len))
else:
    print("{} is NOT an Armstrong number".format(n))
