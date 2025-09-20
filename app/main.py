list = [1, 2, 3]
squared_list = [el * 2 for el in list]

for idx, l in enumerate(list):
    new_l = l * 3
    print(f"L {l} L*3 {new_l}")

print(squared_list)
