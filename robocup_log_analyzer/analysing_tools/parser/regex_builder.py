import re
from string import Formatter
from functools import lru_cache

EXPANDABLE_CATEGORIES = {}
RAW_REGEX_CATEGORIES = {}

def EXPANDABLE(name, definition):
    global EXPANDABLE_CATEGORIES
    EXPANDABLE_CATEGORIES[name] = definition

def RAW_REGEX(name, definition):
    global RAW_REGEX_CATEGORIES
    RAW_REGEX_CATEGORIES[name] = definition

def expand(proto_regex,indent=""):
    def escape_prefix(prefix):
        """ escape " ", ")", and "(" """
        return re.sub(r"([ ()])",r"[\1]",prefix)
    final_regex = ""
    for prefix, name, category,_ in Formatter.parse(None, proto_regex):
        if prefix:
            prefix_regex = escape_prefix(prefix)
            final_regex += f'# literal "{prefix}"' + "\n"
            final_regex += "  " + escape_prefix(prefix) + "\n"
        if name:
            optional = False
            if "?" in category:
                if (
                    category.replace("?","") in EXPANDABLE_CATEGORIES
                    or category.replace("?","") in RAW_REGEX_CATEGORIES
                ):
                    category = category.replace("?","")
                    optional = True
            final_regex += f"# begin of{' optional' if optional else ''} {name} variable" + "\n"
            final_regex += f"  (?P<{name}>" + "\n"
            if category in EXPANDABLE_CATEGORIES:
                final_regex += f"    # {category}" + "\n"
                final_regex += expand(EXPANDABLE_CATEGORIES[category],
                                        indent+"    ") + "\n"
            elif category in RAW_REGEX_CATEGORIES:
                final_regex += f"    # raw {category}" + "\n"
                final_regex += "    "+RAW_REGEX_CATEGORIES[category] + "\n"
            else:
                final_regex += f"    # raw regex: {category}" + "\n"
                final_regex += "    "+category + "\n"
            final_regex += "  )"
            if optional:
                final_regex += "? # optional: may not exist"
            final_regex += "\n"
    final_regex = indent+final_regex.replace("\n","\n"+indent)
    return final_regex

@lru_cache(None)
def regex(category_name):
    if category_name in RAW_REGEX_CATEGORIES:
        return re.compile(RAW_REGEX_CATEGORIES[category_name])
    return re.compile(expand(EXPANDABLE_CATEGORIES[category_name]),flags=re.VERBOSE)

