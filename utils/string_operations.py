def truncate(string, length=20, suffix='...'):
    if len(string) <= length:
        return string
    else:
        return f"{' '.join(string[:length+1].split(' ')[0:-1])}{suffix}"
