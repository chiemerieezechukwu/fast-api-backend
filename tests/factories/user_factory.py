import factory

from app.db.models import User

from ..faker import faker


class UserFactory(factory.Factory):
    class Meta:
        model = User

    full_name = factory.LazyAttribute(lambda _: f"{faker.unique.first_name()} {faker.unique.last_name()}")
    email = factory.LazyAttribute(lambda _: faker.unique.email())
    username = factory.LazyAttribute(lambda _: faker.unique.user_name())
    bio = factory.LazyAttribute(lambda _: faker.sentence(nb_words=10))
