
def _versiontuple(v): # eg. 1.5.10 
    return tuple(map(int, (v.split("."))))
  
def main():
    old = "0.0.9"
    new = "0.0.10"

    print(_versiontuple(new) >= _versiontuple(old)) # True
    
if __name__ == "__main__":    
    main()
