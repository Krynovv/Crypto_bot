


def custom_filter(some_list):
   sum = 0
   some_list = [7, 14, 28, 32, 32, 56]
   for i in some_list:
      if type(i) is int and i % 7 == 0:
         sum += i
   if sum <= 83:
      return True
   else:
      return False

print(custom_filter(some_list))