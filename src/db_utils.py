from pynamodb.models import Model
from pynamodb.exceptions import DoesNotExist


def get_item(sol: int, model: Model) -> Model | None:
    try:
        return model.get(sol)
    except DoesNotExist:
        return None
