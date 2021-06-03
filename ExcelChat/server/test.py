import security

test_str = "hello world!"


string = security.EHash(test_str, "hello")

print(string)