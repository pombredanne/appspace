from appspace.state import AppSpaceKey, appifies


class ATestClass(AppSpaceKey):

    def __init__(): #@NoSelf
        pass

    def footrain(one): #@NoSelf
        pass

    def rootrain(two): #@NoSelf
        pass

    def bahrain(three): #@NoSelf
        pass


class TestClass(object):

    appifies(ATestClass)

    def __init__(self):
        self.number = 1

    def footrain(self, one):
        return self.number + one

    def rootrain(self, two):
        return self.number + two

    def bahrain(self, three):
        return self.number + three


testclass = TestClass()