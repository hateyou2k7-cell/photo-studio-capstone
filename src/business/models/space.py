class Space:
    def __init__(self, id, provider_id, name, space_type, description=None, address=None,
                 max_capacity=None, dimensions=None, art_style=None, lighting=None,
                 ventilation=None, acoustics=None, amenities=None, operating_hours=None,
                 base_price_per_hour=0, status=True, created_at=None, updated_at=None):
        self.id = id
        self.provider_id = provider_id
        self.name = name
        self.space_type = space_type
        self.description = description
        self.address = address
        self.max_capacity = max_capacity
        self.dimensions = dimensions
        self.art_style = art_style
        self.lighting = lighting
        self.ventilation = ventilation
        self.acoustics = acoustics
        self.amenities = amenities
        self.operating_hours = operating_hours
        self.base_price_per_hour = base_price_per_hour
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at