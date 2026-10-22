def divide(a, b):
    # Buggy: no zero division check
    return a / b

def process_list(lst):
    # Anti-pattern: using mutable default args (if we had them)
    # But here, let's just make it confusing
    res = []
    for i in range(len(lst)):
        res.append(lst[i] * 2)
    return res
