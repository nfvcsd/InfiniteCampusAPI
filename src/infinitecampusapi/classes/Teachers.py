class Teachers:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_teachers(self):
        r = self.api_call("teachers")
        return r

    def get_teacher(self, pid):
        r = self.api_call(f"teachers/{pid}")
        return r

    def get_teacher_ids(self):
        data = []
        r = self.get_teachers()
        for user in r["users"]:
            sourcedid = user["sourcedId"]
            name = f"{user['givenName']} {user['familyName']}"
            if sourcedid[0] == "t":
                sourcedid = f"{sourcedid[1:]}"
            sourcedid = int(sourcedid)
            data.append({"name": name, "ID": f"{sourcedid:04}"})
        return data

    def get_class_teacher(self, sourcedId):
        r = self.api_call(f"classes/{sourcedId}/teachers")
        return r["users"][0]
