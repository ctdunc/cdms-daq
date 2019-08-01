import re
import ast 
def redis_to_dict(st):
    """
    Convienence Method to return Dict from Redis input
    """
    try:
        st = st.decode("utf-8")
    except AttributeError:
        pass
    dict_string = re.search('({.+})', st)
    if dict_string:
        return ast.literal_eval(dict_string.group(0))
    else:
        return {}

