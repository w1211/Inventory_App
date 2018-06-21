class UserManager():

    def get_user(self, user):
        if user == 'MRRH':
            return user
        return None

    def verify_pass(self,user,password):
        if user == "MRRH" and password == "biomed":
            return True
        return False