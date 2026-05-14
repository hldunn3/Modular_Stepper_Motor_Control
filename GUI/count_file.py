# table = """
# 32768,33571,34374,35175,35974,36770,37562,38350,
# 39132,39908,40678,41440,42194,42939,43675,44400,
# 45115,45818,46509,47188,47854,48506,49144,49767,
# 50375,50967,51542,52100,52641,53163,53667,54152,
# 54617,55063,55488,55892,56276,56638,56978,57296,
# 57592,57865,58115,58342,58546,58726,58882,59014,
# 59122,59206,59265,59299,59309,59293,59252,59186,
# 59094,58978,58836,58669,58476,58259,58017,57749,
# 57457,57140,56799,56433,56044,55630,55194,54734,
# 54251,53746,53218,52669,52098,51506,50893,50260,
# 49607,48934,48242,47531,46802,46055,45291,44510,
# 43713,42900,42072,41230,40373,39503,38620,37725,
# 36819,35902,34975,34038,33092,32138,31176,30208,
# 29233,28253,27268,26279,25287,24292,23295,22297,
# 21299,20300,19302,18306,17312,16321,15334,14351,
# 13373,12401,11436,10478,9530,8591,7663,6746,
# 5842,4951,4074,3212,2366,1537,726,0,
# 726,1537,2366,3212,4074,4951,5842,6746,
# 7663,8591,9530,10478,11436,12401,13373,14351,
# 15334,16321,17312,18306,19302,20300,21299,22297,
# 23295,24292,25287,26279,27268,28253,29233,30208,
# 31176,32138,33092,34038,34975,35902,36819,37725,
# 38620,39503,40373,41230,42072,42900,43713,44510,
# 45291,46055,46802,47531,48242,48934,49607,50260,
# 50893,51506,52098,52669,53218,53746,54251,54734,
# 55194,55630,56044,56433,56799,57140,57457,57749,
# 58017,58259,58476,58669,58836,58978,59094,59186,
# 59252,59293,59309,59299,59265,59206,59122,59014,
# 58882,58726,58546,58342,58115,57865,57592,57296,
# 56978,56638,56276,55892,55488,55063,54617,54152,
# 53667,53163,52641,52100,51542,50967,50375,49767,
# 49144,48506,47854,47188,46509,45818,45115,44400,
# 43675,42939,42194,41440,40678,39908,39132,38350,
# 37562,36770,35974,35175,34374,33571
# """

# values = [int(v.strip()) for v in table.split(",") if v.strip()]
# print("Number of entries:", len(values))

#####################################################

import math
import matplotlib.pyplot as plt


def generate_sine_table(entries=64, bits=16):
    max_value = (2 ** bits) - 1
    midpoint = max_value / 2

    table = []

    for i in range(entries):
        angle = 2 * math.pi * i / entries
        value = int((math.sin(angle) + 1) * midpoint)
        table.append(value)

    return table

def generate_trapazoid_table(entries=800, bits=16):
    bit_number = (2 ** bits) - 1
    max_value = int(bit_number * 1.5)
    midpoint = max_value / 2

    table = []
    time =[]

    for i in range(entries):
        angle = 2 * math.pi * i / entries

        value = int((math.sin(angle) + 1) * midpoint)
        table.append(value)
        time.append(i)
    
    for n in table:
        if n >= bit_number:
            n == bit_number
            

    plt.plot(time, table)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Simple Plot')

    plt.show()
    print(time)
    return table, time

def print_c_table(table, name="sineTable"):
    print(f"const uint16_t {name}[{len(table)}] = {{")

    for i, v in enumerate(table):
        if i % 8 == 0:
            print("    ", end="")

        end = ", " if i < len(table) - 1 else ""
        print(f"{v:5d}{end}", end="")

        if i % 8 == 7:
            print()

    print("\n};")


if __name__ == "__main__":

    ENTRIES = 800
    BITS = 16

    table,time = generate_trapazoid_table(ENTRIES, BITS)

    print(table)
    print(time)
    # table = generate_sine_table(ENTRIES, BITS)

    # print(f"Generated {len(table)} values ({BITS}-bit)\n")
    # print_c_table(table)