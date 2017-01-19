def addToDictList(dict_list, key, item):
    if(key in dict_list):
        dict_list[key].append(item)
    else:
        dict_list[key] = [item]
 
    return dict_list

def addToDictSet(dict_set, key, item):
    if(key in dict_set):
        dict_set[key] = dict_set[key].union(item)
    else:
        dict_set[key] = item

    return dict_set

def addItemToDictSet(dict_set, key, item):
    if(key not in dict_set):
        dict_set[key] = set()

    dict_set[key].add(item)

    return dict_set
