import SocketServer
import re

NUMS = []

class User(object):
    def __init__(self, name, roles, domain):
        self.name = name
        self.roles = roles
        self.domain = domain

    def may(self, action, resource):
        global privileges
        permissions = []
        for role in self.roles:
            permissions += [p for p in privileges[role]
                            if action in p.actions
                            and type(resource) in p.resource_types]

        def all(bools):
            return reduce(lambda a, b: a and b, bools, True)

        for p in permissions:
            if all([c(self, resource) for c in p.constraints]):
                return True
        return False

USERS = {
    "alice": User("Alice Smith", ["admin"], None),
    "wworth": User("Some Wordsworth", ["domain-expert", "trainee"], "words"),
    "bool": User("James Bool", ["domain-expert"], "very-low-numbers"),
    "stein": User("Albert Stein", ["domain-expert"], "evens"),
    "etl-load": User(None, ["loader"], None),
    "etl-extract": User(None, ["reader"], None),
}

class Permission(object):
    def __init__(self, actions, resource_types, constraints):
        self.actions = actions
        self.resource_types = resource_types
        self.constraints = constraints

is_simple = lambda u, r: r <= 25

def is_in_domain(user, num):
    if "very-low-numbers" == user.domain:
        return num == 0 or num == 1
    if "odds" == user.domain:
        return num % 2 == 1
    if "evens" == user.domain:
        return num % 2 == 0
    return False

privileges = {
    "admin": [Permission(["reset"], [type([])], []),
              Permission(["put", "get"], [type(1)], [])],
    "expert": [Permission(["put", "get"], [type(1)], [])],
    "domain-expert": [Permission(["put"], [type(1)], [is_in_domain]),
                      Permission(["get"], [type(1)], [])],
    "trainee": [Permission(["get"], [type(1)], [is_simple])],
    "domain-trainee": [Permission(["get"], [type(1)],
                                  [is_simple, is_in_domain])],
    "loader": [Permission(["put"], [type(1)], [])],
    "reader": [Permission(["get"], [type(1)], [])],
}

def parsable(n):
    try:
        _ = int(n)
        return True
    except:
        return False

def find_user(path):
    for username in USERS:
        if re.search(username, path):
            return USERS[username]
    raise Exception("not authenticated!!!")

class NumberHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        global NUMS
        path = self.rfile.readline().strip()
        print "Recieved:", path
        requested_numbers = [int(n) for n in path.split('/') if parsable(n)]
        print "Requested Numbers:", requested_numbers
        try:
            requesting_user = find_user(path)
        except:
            self.wfile.write("put who you are in the path")
            print "didn't find a user"
            return

        # insert numbers they are allowed to insert
        insertable_numbers = [n for n in requested_numbers
                              if requesting_user.may("put", n)]
        NUMS += insertable_numbers
        NUMS = sorted(list(set(NUMS)))

        # reset the list if the user wants to and is allowed to
        if requesting_user.may("reset", NUMS):
            if re.search("RESET", path):
                NUMS = []

        # then return all then numbers they are allowed to see
        viewable_numbers = [n for n in NUMS if requesting_user.may("get", n)]
        self.wfile.write("The numbers are: {}".format(viewable_numbers))
        print "sent", viewable_numbers

if __name__ == "__main__":
    try:
        httpd = SocketServer.TCPServer(("", 8000), NumberHandler)
        print "listening on 8000"
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "SHUTTING DOWN!!!!!"
        httpd.shutdown()
