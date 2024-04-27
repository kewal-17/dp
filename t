def ks_bb_relax_capacity(items, item_count, capacity, optimistic_estimate, item, value, selected_items):
    if item_count == 0 or capacity <= 0:
        return value, selected_items

    if items[item].weight > capacity:
        optimistic_estimate = optimistic_estimate - items[item].value
        return ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate, item + 1, value,
                                    selected_items)
    else:

        if capacity - items[item].weight >= 0:
            value = value + items[item].value
            selected_items[item] = 1
        left = ks_bb_relax_capacity(items, item_count - 1, capacity - items[item].weight, optimistic_estimate,
                                    item + 1, value, selected_items)

        optimistic_estimate = optimistic_estimate - items[item].value

        if optimistic_estimate < left[0]:
            return left
        else:
            return ks_bb_relax_capacity(items, item_count - 1, capacity, optimistic_estimate, item + 1, value,
                                         selected_items)


