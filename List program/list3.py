def swapList3(list): 
      
    start, *middle, end = list
    list = [end, *middle, start] 
      
    return list
      
# Driver code 
newList = [12, 35, 9, 56, 24] 
  
print(swapList3(newList)) 
