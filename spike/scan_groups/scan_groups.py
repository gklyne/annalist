def scan_groups(prefix, group_list, field_name, field_name_postfix, data_dict):
    """
    return (stop, result)
    where:
      'stop'   is True if there are no more possible results to try.
      'result' is the final result to return if `more` is false.
    """
    stop_all   = True
    if group_list == []:
        try_field = prefix + field_name
        if try_field in data_dict:
            try_postfix = try_field + "__" + field_name_postfix
            return (try_postfix in data_dict, try_postfix)
    else:
        group_head = group_list[0]
        group_tail = group_list[1:]
        index      = 0
        while True:
            next_prefix = "%s%s__%d__"%(prefix, group_head, index)
            (stop, result) = scan_groups(next_prefix, group_tail, field_name, field_name_postfix, data_dict)
            if stop:
                if result:
                    return (True, result)
                else:
                    break
            stop_all = False
            index   += 1
    return (stop_all, None)

if __name__ == "__main__":
    data_dict = (
        { "f1":                     "f1"
        , "f2":                     "f1"
        , "f2__post":               "yes"
        , "g1__0__f3":              "f3"
        , "g1__1__f3":              "f3"
        , "g2__0__f4":              "f4"
        , "g2__1__f4":              "f4"
        , "g2__1__f4__post":        "f4"
        , "g3__0__g4__0__f5":       "f5"
        , "g3__0__g4__1__f5":       "f5"
        , "g3__1__g4__0__f5":       "f5"
        , "g3__1__g4__1__f5":       "f5"
        , "g5__0__g6__0__f6":       "f6"
        , "g5__0__g6__1__f6":       "f6"
        , "g5__0__g6__2__f6":       "f6"
        , "g5__1__g6__0__f6":       "f6"
        , "g5__1__g6__1__f6":       "f6"
        , "g5__2__g6__0__f6":       "f6"
        , "g5__2__g6__1__f6":       "f6"
        , "g5__2__g6__1__f6__post": "f6"       
        , "g5__2__g6__2__f6":       "f6"
        , "g5__3__g6__0__f6":       "f6"
        , "g5__3__g6__1__f6":       "f6"
        , "g5__3__g6__2__f6":       "f6"
        })
    s1, r1 = scan_groups("", [], "f1", "post", data_dict)
    assert s1 == False
    assert r1 == "f1__post"
    s2, r2 = scan_groups("", [], "f2", "post", data_dict)
    assert s2 == True
    assert r2 == "f2__post"
    s3, r3 = scan_groups("", ["g1"], "f3", "post", data_dict)
    assert s3 == False
    assert r3 == None
    s4, r4 = scan_groups("", ["g2"], "f4", "post", data_dict)
    assert s4 == True
    assert r4 == "g2__1__f4__post"
    s5, r5 = scan_groups("", ["g3", "g4"], "f5", "post", data_dict)
    assert s5 == False
    assert r5 == None
    s6, r6 = scan_groups("", ["g5", "g6"], "f6", "post", data_dict)
    assert s6 == True
    assert r6 == "g5__2__g6__1__f6__post"
    s7, r7 = scan_groups("", ["g7"], "f7", "post", data_dict)
    assert s7 == True
    assert r7 == None
    print "All tests pass."

