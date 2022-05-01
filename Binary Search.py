import csv


def bisearch(lst, elm, start, stop):
    if start > stop:
        return False
    else:
        mid = (start + stop) // 2
        if elm == lst[mid]:
            return mid
        elif lst[mid] > elm:
            return bisearch(lst, elm, mid + 1, stop)
        else:
            return bisearch(lst, elm, start, mid - 1)


csv_file = csv.reader(open("foreign_names.csv", "r"))
lst = [csv_file[0], csv_file[1], csv_file[3], csv_file[4]]
# with open('foreign_names.csv', 'r') as csvfile:
#     lst = csv.reader(csvfile)
    # for row in reader:
    #     print(row['id'], row['name'], row['gender'], row['origin'])
elm = 'Phrixus'

bisearch(lst, elm, 0, len(lst))
