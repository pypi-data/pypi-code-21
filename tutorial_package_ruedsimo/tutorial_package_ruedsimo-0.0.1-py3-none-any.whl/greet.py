def say_hello(who):
    print(greeting(who))
    
def greeting(who):
    return "hi %s" % who

def main():
    import sys
    say_hello(sys.argv[1])

if __name__=="__main__":
    main()
    
