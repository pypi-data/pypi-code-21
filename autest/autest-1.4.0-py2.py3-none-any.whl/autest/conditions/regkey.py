
import autest.api as api
import autest.common.reg as reg

def HasRegKey(self, root, keys, msg):
    return self.Condition(lambda: reg.has_regkey(root, keys), msg, True)

# def RegistryKeyEqual(self,key,value):
# pass

api.ExtendCondition(HasRegKey)
