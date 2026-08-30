class EquipmentDomain:
    def __init__(self, id=None, provider_id=None, space_id=None, name=None, model_name=None,
                 equipment_type=None, compatibility=None, condition='good', description=None,
                 price_per_hour=0, is_available=True, created_at=None, updated_at=None):
        self.id = id
        self.provider_id = provider_id
        self.space_id = space_id
        self.name = name
        self.model_name = model_name
        self.equipment_type = equipment_type
        self.compatibility = compatibility
        self.condition = condition
        self.description = description
        self.price_per_hour = price_per_hour
        self.is_available = is_available
        self.created_at = created_at
        self.updated_at = updated_at
