import factory

from app.db.models import User

from ..faker import faker


class UserFactory(factory.Factory):
    class Meta:
        model = User

    full_name = factory.LazyAttribute(lambda _: f"{faker.unique.first_name()} {faker.unique.last_name()}")
    username = factory.LazyAttribute(lambda _: faker.unique.user_name())
    email = factory.LazyAttribute(
        lambda self: f"{self.full_name.lower().replace(' ', '.')}{faker.unique.random_int()}@testmail.com"
    )
