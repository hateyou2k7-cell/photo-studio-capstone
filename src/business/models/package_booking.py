class PackageBookingDomain:
    def __init__(self, id=None, package_id=None, space_id=None, customer_id=None,
                 start_time=None, end_time=None, status='pending', total_price=0,
                 notes=None, created_at=None):
        self.id = id
        self.package_id = package_id
        self.space_id = space_id
        self.customer_id = customer_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.total_price = total_price
        self.notes = notes
        self.created_at = created_at
