string = "2020"

try:
    if type(int(string)) is int:
        print(string)
except Exception as e:
    print(e)

string = "jsfaj-2020"

printer = string[string.rfind("-")+1:]

print(printer)
