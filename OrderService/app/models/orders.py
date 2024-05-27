from datetime import datetime

from beanie import Document

from app.core.enums import OrderStatuses


class Order(Document):
    rental_date_start: datetime
    rental_date_end: datetime
    total_cost: float
    status: OrderStatuses
    customer_id: int
    car_ids: list[int]
    created_at: datetime = datetime.now()

    @property
    def rental_time(self) -> int:
        time_difference = self.rental_date_end - self.rental_date_start
        rental_time_hours = time_difference.total_seconds() / 3600
        return int(rental_time_hours)
