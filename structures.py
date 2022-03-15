#!/usr/bin/env python


class Base:
    def __init__(self, name, notes=None):
        self.name = name
        self.uid = None
        self.notes = None
    
    def _is_uid_set(self):
        return self.uid is not None


class MaterialBase(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cost = None
        self.costOffset = None
        self.tags = set()
    
    def add_tags(self, *args):
        self.tags = self.tags.union(set(args))

    def _is_cost_set(self):
        return self.cost is not None
    
    def set_cost(self, amount, offset=None):
        self.cost = float(amount)
        if offset:
            self.costOffset = float(offset)

    def reset_cost(self):
        self.cost = None
        self.costOffset = None


class Material(MaterialBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XORGroup(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = None
        self.members = set()


class Product(MaterialBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.materials = dict()
        self.xorGroups = dict()
        self.xorEnabledMaterials = set()
        self.version = None

    def add_materials(self, *mats):
        for m in mats:
            self.materials.update({m.uid: m})

    def remove_materials(self, *mats):
        for m in mats:
            if m.uid in self.materials.keys():
                del self.materials[m.uid]

    def enable_xor(self, material, xorGroupName):
        if xorGroupName not in self.xorGroups.keys():
            newXorGroup = XORGroup(xorGroupName)
            self.xorGroups.update({newXorGroup.name: newXorGroup})
        self.xorGroups[xorGroupName].members.add(material.uid)
        self.xorEnabledMaterials.add(material.uid)

    def disable_xor(self, *materials):
        for k, v in self.xorGroups:
            for m in materials:
                v.members.remove(m.uid)
        self.xorEnabledMaterials.remove(m.uid)

    def set_xor_active(self, material):
        if material.uid not in self.xorEnabledMaterials:
            raise IndexError(f'XOR is not enabled for {material.name}')
        for k, v in self.xorGroups.items():
            if material.uid in v.members:
                self.xorGroups[k].active = material.uid

    def material_is_active(self, material):
        return (material.uid in (group.active for group in self.xorGroups.values()))

    def _accumulate_material_costs(self):
        self.cost = self.costOffset if self.costOffset is not None else 0.0
        for muid, material in self.materials.items():
            if (muid in self.xorEnabledMaterials) and not self.material_is_active(material):
                pass
            elif material._is_cost_set():
                self.cost += material.cost
                if material.costOffset is not None:
                    self.cost += material.costOffset
            else:
                print(f'Cost not set for {material.name}; skipping')
    
    def get_cost(self):
        self._accumulate_material_costs()
        return self.cost


class ProductSet(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.products = set()
        self.uidIndex = 0

    def _increment_uid_index(self):
        currentUid = self.uidIndex
        self.uidIndex += 1
        return currentUid

    def create_product(self, name):
        newProduct = Product(name)
        newProduct.uid = self._increment_uid_index()
        self.products.add(newProduct)
        return newProduct
    
    def duplicate_product(self, product):
        newProduct = self.create_product(product.name)
        newProduct.notes = product.notes
        newProduct.cost = product.cost
        newProduct.costOffset = product.costOffset
        newProduct.tags = product.tags
        newProduct.materials = product.materials
        newProduct.xorGroups = product.xorGroups
        newProduct.xorEnabledMaterials = product.xorEnabledMaterials
        newProduct.version = product.version
        return newProduct
    
    def create_material(self, name):
        newMaterial = Material(name)
        newMaterial.uid = self._increment_uid_index()
        return newMaterial

    def duplicate_material(self, material):
        newMaterial = self.create_material(material.name)
        newMaterial.notes = material.notes
        newMaterial.cost = material.cost
        newMaterial.costOffset = material.costOffset
        newMaterial.tags = material.tags
        return newMaterial


