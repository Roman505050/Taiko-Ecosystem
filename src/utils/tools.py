

def int_to_decimal(qty, decimal):
    return int(qty * 10**decimal)

def decimal_to_int(qty, decimal):
    return float(qty / 10**decimal)

def get_decimal_places(value):
    """Повертає кількість десяткових знаків у числі."""
    str_value = str(value)
    if '.' in str_value:
        return len(str_value.split('.')[1])
    else:
        return 0