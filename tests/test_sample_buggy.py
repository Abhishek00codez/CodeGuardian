import target

def test_divide():
    assert target.divide(10, 2) == 5
    # The agent should see this test fails if not handled
    try:
        target.divide(10, 0)
    except ZeroDivisionError:
        pass
    else:
        assert False, "Should have raised ZeroDivisionError or handled it gracefully"

def test_process_list():
    assert target.process_list([1, 2, 3]) == [2, 4, 6]
