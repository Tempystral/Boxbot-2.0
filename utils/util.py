def commaList(l:list) -> str:
    text = ""
    if len(l) < 1:
        return text
    if len(l) == 1:
        text = l[0]
    elif len(l) == 2:
        text = f"{l[0]} and {l[1]}"
    else:
        text = f'{", ".join(l[:-1])}, and {l[-1]}'
    return text.replace("_", " ")