def find_duplicates(items):
    # Inefficient O(n^2) duplicate check, and no input validation
    # use set for better performance and to avoid duplicates in the result
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if i != j and items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates


def load_config(path):
    # Security issue: eval() on file contents
    with open(path, "r") as f:
        contents = f.read()
    return eval(contents)