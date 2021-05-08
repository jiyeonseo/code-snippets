def _replace(dict1: Dict, dict2: Dict):
    for k, val in dict2.items():
        if k in dict1:
            vv = dict1[k]
            if isinstance(vv, Dict):
                _replace(vv, val)
            else:
                if val:
                    dict1[k] = val
        else:
            if val:
                dict1[k] = val
 
def main():
    orig = {
      "foo" : "bar"
    }
    new = {
      "foo" : "bbar",
      "bar" : "foo"
    }

    print(_replace(orig, new) 
    # {
    #     "foo" : "bbar",
    #     "bar" : "foo"
    # }
    
if __name__ == "__main__":    
    main()
    
