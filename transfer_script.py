import pickle

class ah_item:
    def __init__(self,name,tier,category,reforge,metadata=set(),enchantments={}):
        self.name = name
        self.metadata = metadata
        self.tier = tier
        self.category = category
        self.reforge = reforge
        self.enchantments = enchantments
    def __repr__(self):
        if self.reforge:
            return self.reforge + ' ' + self.name
        else:
            return self.name
    def __str__(self):
        if self.reforge:
            return self.reforge + ' ' + self.name
        else:
            return self.name
    def __eq__(self,obj):
        if type(obj) != ah_item:
            return False
        if obj.name != self.name:
            return False
        elif obj.metadata != self.metadata:
            return False
        elif obj.reforge != self.reforge:
            return False
        elif obj.enchantments != self.enchantments:
            return False
        elif obj.tier != self.tier:
            return False
        return True
    def __ne__(self,obj):
        return not self.__eq__(obj)
    def __hash__(self):
        return hash(hash(''.join(self.metadata))+hash(self.reforge)+hash(self.name))

with open('bazaar_data.dat','rb') as F:
    data = pickle.load(F)

for item in data.items():
    with open('bazaar_data/'+item[0]+'.dat','wb') as F:
        pickle.dump({item[0]:item[1]},F)
