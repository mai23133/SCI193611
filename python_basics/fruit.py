fruitPrices = {'apples': 2.00, 'oranges': 1.50, 'pears': 1.75}

def buyFruit(fruit, numPounds):
    if fruit not in fruitPrices:
        print("Sorry we don't have %s" % (fruit))
        return None  
    else:
        cost = fruitPrices[fruit] * numPounds
        print("That'll be %.2f please" % (cost))
        return cost  

# Main Function
if __name__ == '__main__':

    total_apples = buyFruit('apples', 2.4) 
    if total_apples is not None:
        print("total = %.2f" % total_apples)
        
    print("-" * 30)
    total_coconuts = buyFruit('coconuts', 2)
    if total_coconuts is not None:
        print("total = %.2f" % total_coconuts)
    else:
        print("total = Cannot calculate (Item not found)")