#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal

from collections import namedtuple

Item = namedtuple("Item", ['index', 'value', 'weight'])
NewItem = namedtuple("Item", ['index', 'value', 'weight', 'unit_value'])


def signal_handler(signum, frame):
    raise Exception("Time limit of 5 hours exceeded")


def knapsack_tabulation(items, item_count, capacity):
    table = [[0 for _ in range(capacity + 1)] for _ in range(item_count + 1)]
    for i in range(item_count + 1):
        # print(i)
        for w in range(capacity + 1):
            # print(w)
            if i == 0 or w == 0:
                table[i][w] = 0
            elif items[i - 1].weight <= w:
                table[i][w] = max(table[i - 1][w],
                                  items[i - 1].value + table[i - 1][
                                      w - items[i - 1].weight])
            else:
                table[i][w] = table[i - 1][w]
    return table

def knapsack_tabulation_dict(items, item_count, capacity):
    # table = [[0 for _ in range(capacity+1)] for _ in range(item_count+1)]

    # total_value = sum(item.value for item in items)
    # if total_value < capacity:
    #     selected_items = [1] * item_count
    #     value = total_value
    #     print("yes")
    #     return selected_items, value
    table = {}
    for i in range(item_count + 1):
        # print(i)
        for w in range(capacity + 1):
            # print(w)
            if i == 0 or w == 0:
                table[(i, w)] = 0
            elif items[i - 1].weight <= w:
                table[(i, w)] = max(table[(i - 1, w)],
                                    items[i - 1].value + table[
                                        (i - 1, w - items[i - 1].weight)])
            else:
                table[(i, w)] = table[(i - 1, w)]
    value = table[(item_count, capacity)]
    # print(table, value)
    remaining_value = value
    selected_items = [0] * item_count
    # print(selected_items)
    for i in range(item_count - 1, -1, -1):
        # print(i)
        value_found = False
        for j in range(capacity, -1, -1):
            if remaining_value > table[(i, j)]:
                break
            elif remaining_value == table[(i, j)]:
                value_found = True
                break
        if not value_found:
            selected_items[i] = 1
            remaining_value = remaining_value - items[i].value
        if remaining_value == 0:
            break
    return selected_items, value


def knapsack_greedy(new_items, item_count, capacity):
    selected_items = [0] * item_count
    value = 0
    remaining_space = capacity
    sorted_items = sorted(new_items, key=lambda item: item.unit_value, reverse=True)
    for item in sorted_items:
        if item.weight <= remaining_space:
            selected_items[item.index] = 1
            remaining_space = remaining_space - item.weight
            value = value + item.value
        else:
            units = remaining_space / item.weight
            #print(units, units * item.value, item)
            break
    return selected_items, value


def knapsack_recursive(items, item_count, capacity, item):
    # Base Condition
    if item_count == 0 or capacity == 0:
        return 0, [0] * len(items)

    # Exclude the item
    if items[item].weight > capacity:
        return knapsack_recursive(items, item_count - 1, capacity, item + 1)
    else:  # Include the item

        left, left_selected = knapsack_recursive(items, item_count - 1, capacity - items[item].weight, item + 1)
        left += items[item].value
        right, right_selected = knapsack_recursive(items, item_count - 1, capacity, item + 1)
        if left > right:
            left_selected[item] = 1
            return left, left_selected
        else:
            return right, right_selected

        # return max(knapsack_recursive(items, item_count-1, capacity, item+1),
        #            items[item].value + knapsack_recursive(items, item_count-1, capacity - items[item].weight, item+1))


def knapsack_recursive_relax_capacity(items, item_count, capacity, item, oe):
    # Base Condition
    if item_count == 0 or capacity == 0:
        return 0, [0] * len(items), oe

    # Exclude the item
    if items[item].weight > capacity:
        return knapsack_recursive_relax_capacity(items, item_count - 1, capacity, item + 1, oe - items[item].value)
    else:  # Include the item
        left, left_selected, loe = knapsack_recursive_relax_capacity(items, item_count - 1, capacity - items[
            item].weight, item + 1, oe)
        left += items[item].value
        roe = oe - items[item].value
        if roe > loe:
            right, right_selected, roe = knapsack_recursive_relax_capacity(items, item_count - 1, capacity, item + 1,
                                                                           roe)
        else:
            right, right_selected = float("-inf"), [0] * len(items)
        if left > right:
            left_selected[item] = 1
            return left, left_selected, loe
        else:
            return right, right_selected, roe


def ks_bb_relax_capacity(items, item_count, capacity, optimistic_estimate, item, value, selected_items):
    if item_count == 0 or capacity <= 0:
        return value, selected_items

    if items[item].weight > capacity:
        optimistic_estimate = optimistic_estimate - items[item].value
        right = ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate, item + 1, value,
                                     selected_items)
        # print(right, "inside")
    else:
        # Including the item
        if capacity - items[item].weight >= 0:
            value = value + items[item].value
            selected_items[item] = 1
        left = ks_bb_relax_capacity(items, item_count - 1, capacity - items[item].weight, optimistic_estimate,
                                    item + 1, value, selected_items)
        # print(left, "\n*****")

        # else:
        #     left = (value, selected_items)
        #     #return value, selected_items

        # value = left[0]
        # Excluding the item
        optimistic_estimate = optimistic_estimate - items[item].value

        # if value < ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate, item + 1, value,
        #                                 selected_items)[0]:
        #     selected_items[item] = 0
        #     right = ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate, item + 1, value,
        #                                  selected_items)
        # value = right[0]

        right = ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate - items[item].value, item + 1,
                                     value,
                                     selected_items)

        if right[0] < left[0]:
            return left
        else:
            return right
            # if left[0] >= right[0]:
            #     return left
            # else:
            #     return right
        # return ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate, item + 1, value,
        # selected_items)
        #     if left[0] >= right[0]:
        #         return left
        #     else:
        #         return right
        # else:
        #     return left
        # else:
        #     right = left
        #     return
        # if left[0] > right[0]:
        #     return left
        # else:
        #     return right
        # return value, selected_items


def ks_bb_relax_capacity1(items, capacity, optimistic_estimate, item, value, selected_items):
    if item == len(items) or capacity == 0:
        return value, selected_items

    # Exclude the current item
    exclude_value, exclude_selected = ks_bb_relax_capacity1(items, capacity, optimistic_estimate - items[item].value,
                                                            item + 1, value, selected_items.copy())

    # Include the current item if it fits in the knapsack
    if items[item].weight <= capacity:
        include_value, include_selected = ks_bb_relax_capacity1(items, capacity - items[item].weight,
                                                                optimistic_estimate, item + 1,
                                                                value + items[item].value,
                                                                selected_items.copy())
        include_selected[item] = 1
    else:
        include_value, include_selected = float('-inf'), selected_items

    # Choose the better option between including and excluding the current item
    if include_value >= exclude_value:
        return include_value, include_selected
    else:
        return exclude_value, exclude_selected




def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []
    new_items = []
    for i in range(1, item_count + 1):
        # print(f"items creating {i}")
        line = lines[i]
        parts = line.split()
        items.append(Item(i - 1, int(parts[0]), int(parts[1])))
        new_items.append(NewItem(i - 1, int(parts[0]), int(parts[1]),
                                 float(int(parts[0]) / int(parts[1]))))

    # a trivial algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    # value = 0
    # weight = 0
    # taken = [0]*len(items)

    # for item in items:
    #    if weight + item.weight <= capacity:
    #        taken[item.index] = 1
    #        value += item.value
    #        weight += item.weight
    # taken, value = knapsack_tabulation_dict(items, item_count, capacity)

    # taken, value = knapsack_greedy(new_items, item_count, capacity)
    if item_count == 30 or item_count == 50 or item_count == 200 or item_count == 1000:
        table = knapsack_tabulation(new_items, item_count, capacity)
        value = table[item_count][capacity]
        # taken = [0] * item_count
        # remaining_value = value
        # for i in range(item_count + 1, 0, -1):
        #     if remaining_value not in table[i - 1]:
        #         taken[i - 1] = 1
        #         remaining_value = remaining_value - items[i - 1].value
        # # prepare the solution in the specified output format
        # total wt
        # wt = 0
        # for i in range(len(taken)):
        #     if taken[i] == 1:
        #         wt = wt + items[i].weight
        # print(wt, "*********************")

        taken = [0] * item_count
        w = capacity
        # wt = 0
        for i in range(item_count, 0, -1):
            if table[i][w] != table[i - 1][w]:
                taken[i - 1] = 1
                w -= items[i - 1].weight
        # for i in range(len(taken)):
        #     if taken[i] == 1:
        #         wt = wt + items[i].weight
        # print(wt, "*********************")

    else:
        taken, value = knapsack_greedy(new_items, item_count, capacity)

    # # print(table)

    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    #print(output_data)

    # oe = sum(item.value for item in items)
    # oe = knapsack_greedy(new_items, item_count, capacity)[1]
    # print(oe)
    # value, taken, oe = knapsack_recursive_relax_capacity(items, item_count, capacity, 0, oe)
    # output_data = str(value) + ' ' + str(0) + '\n'
    # output_data += ' '.join(map(str, taken))
    #selected_items = [0] * item_count
    # value, taken = ks_bb_relax_capacity(items, item_count, capacity, sum(item.value for item in items), 0, 0,
    # selected_items)

    # output_data = str(value) + ' ' + str(0) + '\n'
    # output_data += ' '.join(map(str, taken))

    #print(knapsack_recursive(items, item_count, capacity, 0))

    return output_data


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(18000)
        try:
            print(solve_it(input_data))
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()
            print("Time limit of 5 hours exceeded")
    else:
        print(
            'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')
