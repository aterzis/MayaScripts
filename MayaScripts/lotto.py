import random

numbers = list()
for i in range(46):
    numbers.append(i)
    
numbers.pop(0)
random.shuffle(numbers)

print numbers[0:6]
print numbers[6:12]
print numbers[12:18]
print numbers[18:24]
print numbers[24:30]
print numbers[30:36]
print numbers[36:42]
print numbers[42:]

'''
1st run
'''
#[12, 43, 44, 27, 7, 1]
#[32, 40, 26, 15, 10, 34]
#[14, 23, 18, 28, 2, 29]
#[16, 8, 35, 38, 30, 37]
#[11, 33, 4, 6, 3, 45]
#[9, 17, 31, 39, 21, 42]
#[19, 24, 36, 5, 41, 20]
#[22, 13, 25]

'''
2nd run
'''
#[25, 21, 6, 9, 14, 34]
#[31, 28, 26, 23, 24, 27]
#[36, 38, 15, 43, 4, 10]
#[30, 7, 41, 12, 29, 16]
#[5, 33, 18, 35, 40, 32]
#[22, 37, 39, 19, 13, 3]
#[44, 42, 17, 2, 8, 45]
#[1, 11, 20]

'''
Add the last 2 games together for final random game
then you have 16 games for saturday lotto = $10.60 game
'''