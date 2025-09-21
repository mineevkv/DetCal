def remove_zeros( input_string):
    """Remove trailing zeros from a string containing a decimal point"""
    if input_string is None:
        return
    
    input_string = str(input_string)
    if '.' in input_string:
        input_list = input_string.split('.')
        input_list[1] = input_list[1].rstrip('0')
        if input_list[1] == '':
            return input_list[0]
        input_string = '.'.join(input_list)
        
    return input_string

def str_to_bool(value):
    """Convert string to bool """
    if isinstance(value, str):
        value = value.lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False
    return bool(value)

def refresh_obj_view(object_name):
    object_name.style().unpolish(object_name)
    object_name.style().polish(object_name)