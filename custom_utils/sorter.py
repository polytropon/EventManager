from collections import OrderedDict
import datetime

def sortList(entries,key,key_order=[]):
    '''Order list according to a single criterium, optionally according to a custom order of the values of this criterium

    Parameters:
    entries (iterable): Items to be sorted

    key: Attribute by which to sort

    key_order (list): Optional argument with values of key in the order in which they should appear
    '''
    ## If no key order provided, create set of unique values
    if not key_order:
        key_order = sorted(set([getattr(entry,key) for entry in entries if getattr(entry,key)]))

    has_key = sorted([entry for entry in entries if getattr(entry,key)],
        key=lambda o:getattr(o,key))
    list_of_lists = []

    for ordered_key in key_order:
        matching_entries = [entry for entry in has_key if getattr(entry,key) == ordered_key]
        list_of_lists.append(matching_entries)

    ## Entries that have a sortable value, but are not in sublist (only triggered if key order passed as arg does not include all actual values)
    not_in_custom_list = sorted([entry for entry in has_key if getattr(entry,key) and getattr(entry,key) not in key_order],
    key=lambda o:getattr(o,key))

    if not_in_custom_list:
        list_of_lists.append(not_in_custom_list)

    ## If object has a null value saved to this key, add to last list
    not_key = [entry for entry in entries if not getattr(entry,key)]
    if not_key:
        list_of_lists.append(not_key)

    return(list_of_lists)

from custom_utils.sorter import *
from crm.models import *

def multisort(entries,criteria):
    '''Order list according to multiple criteria, each of which may be ordered in an arbitrary order
    provided in criteria.

    Parameters:
    entries (iterable): List to be sorted

    criteria (OrderedDict): Has format (attribute_to_sort_by:(first_value,second_value)), first items in dict are the top sorting criteria

    Returns:
    list: Sorted list
    '''
    if type(criteria) in (OrderedDict,dict):
        criteria_dict = criteria
    elif type(criteria) in (list,tuple,set):
        criteria_dict = {x:None for x in criteria}
    elif type(criteria) == str:
        criteria_dict = {criteria:None}
    else:
        raise ValueError(f"Multisort criteria has wrong type: {type(criteria)}")

    criteria_list = list(criteria_dict.keys())
    multilevel_list = []
    for key,key_order in criteria_dict.items():
        if multilevel_list == []:

            multilevel_list = sortList(entries,key,key_order=key_order)
        else:
            new_multilevel_list = []
            for sorted_sublist in multilevel_list:
                sublists = sortList(sorted_sublist,key,key_order=key_order)
                new_multilevel_list.extend(sublists)
            multilevel_list = new_multilevel_list

    flat_list = []
    [flat_list.extend(sublist) for sublist in multilevel_list]
    return(flat_list)

# from collections import OrderedDict
# criteria_dict = OrderedDict([('Status', False), ('Übernachtung', False)])
# entries = FormEntry.objects.filter(Veranstaltung=24)

#from custom_utils.sorter import *
#sorted = recursiveSort(entries,criteria_dict)
