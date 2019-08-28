from bs4 import Tag

def getChildren(child, object):
    if isinstance(child, Tag):
        for item in child.children:
            getChildren(item, object)
            if item.next_sibling is None:
                return
    try:
        text = child.text
    except:
        text = ''
    if text:
        field = object.update({len(object) + 1: child.text})
    else:
        field = str(child).strip(' \n')
    if field:
        object.update({len(object) + 1: field})
