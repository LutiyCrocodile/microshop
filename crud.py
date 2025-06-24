import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy.engine import Result
from urllib3.poolmanager import key_fn_by_scheme

from core.models import (
    db_helper,
    User,
    Profile,
    Post,
    Order,
    Product,
    OrderProductAssociation,
)
from sqlalchemy.orm import joinedload, selectinload


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("user", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)
    # user: User | None = await session.scalar(stmt)
    user: User | None = result.scalar_one_or_none()
    print("found user", username, user)
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profiles(
    session: AsyncSession,
):
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = await session.scalars(stmt)
    for user in users:
        print(user)
        print(user.profile.first_name)


async def create_posts(
    session: AsyncSession,
    user_id: int,
    *post_titles: str,
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in post_titles]
    session.add_all(posts)
    await session.commit()
    print(posts)
    return posts


async def get_users_with_post(
    session: AsyncSession,
):
    stmt = (
        select(User)
        .options(
            selectinload(User.posts),
        )
        .order_by(User.id)
    )
    users = await session.scalars(stmt)

    for user in users:
        print("*" * 20)
        print(user)
        for post in user.posts:
            print("--", post)


async def get_posts_with_authors(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)

    for post in posts:
        print("post", post)
        print("author", post.user)


async def get_users_with_post_and_profiles(
    session: AsyncSession,
):
    stmt = (
        select(User)
        .options(
            joinedload(User.profile),
            selectinload(User.posts),
        )
        .order_by(User.id)
    )
    users = await session.scalars(stmt)

    for user in users:
        print("*" * 20)
        print(user, user.profile and user.profile.first_name)
        for post in user.posts:
            print("--", post)


async def get_profiles_with_user_and_user_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .join(Profile.user)
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
        .where(User.username == "Max")
        .order_by(Profile.id)
    )

    profiles = await session.scalars(stmt)

    for profile in profiles:
        print(profile.first_name, profile.user)
        print(profile.user.posts)


async def create_order(session: AsyncSession, promocode: str | None = None) -> Order:
    order = Order(promocode=promocode)
    session.add(order)
    await session.commit()
    return order


async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    price: int,
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
    )
    session.add(product)
    await session.commit()
    return product


async def create_products_and_products(session: AsyncSession):
    order_one = await create_order(session)
    order_promo = await create_order(session, promocode="promo")

    mouse = await create_product(
        session,
        "mouse",
        "Grate mouse",
        2000,
    )
    keyboard = await create_product(
        session,
        "keyboard",
        "Grate keyboard",
        5000,
    )
    display = await create_product(
        session,
        "display",
        "Office display",
        10000,
    )
    order_one = await session.scalar(
        select(Order)
        .where(Order.id == order_one.id)
        .options(
            selectinload(Order.products),
        ),
        options=(selectinload(Order.products),),
    )
    order_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_promo.id)
        .options(
            selectinload(Order.products),
        ),
        options=(selectinload(Order.products),),
    )
    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    # order_promo.products.append(keyboard)
    # order_promo.products.append(display)
    order_promo.products = [keyboard, display]
    await session.commit()


async def get_orders_with_products(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
    orders = await get_orders_with_products(session)
    for order in orders:
        print(order.id, order.promocode, order.created_at, "products: ")
        for product in order.products:
            print("-", product.id, product.name, product.price)


async def get_orders_with_products_assoc(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            )
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_with_assoc(session: AsyncSession):
    orders = await get_orders_with_products_assoc(session)

    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for (
            order_product_details
        ) in order.products_details:  # type: OrderProductAssociation
            print(
                "-",
                order_product_details.product.name,
                order_product_details.product.price,
                "qty:",
                order_product_details.quantity,
            )


async def main_relations(session: AsyncSession):
    async with db_helper.session_factory() as session:
        # # await create_user(session=session, username="john")
        # await create_user(session=session, username="Bob")
        # # await create_user(session=session, username="Max")
        # user_john = await get_user_by_username(session=session, username="john")
        # user_Max = await get_user_by_username(session=session, username="Max")
        # await create_user_profile(
        #     session=session,
        #     user_id=user_john.id,
        #     first_name="john",
        # )
        # await create_user_profile(
        #     session=session,
        #     user_id=user_Max.id,
        #     first_name="Max",
        #     last_name="Trosh",
        # )
        # await show_users_with_profiles(session=session)
        # await create_posts(
        #     session,
        #     user_Max.id,
        #     "SQLA 2.0",
        #     "SQLA Joins",
        #     "FastPI",
        # )
        # await create_posts(
        #     session,
        #     user_john.id,
        #     "Pyqt5",
        #     "Pyqt6",
        # )
        # await create_posts(
        #     session,
        #     user_john.id,
        #     "Pyqt5",
        #     "Pyqt6",
        # )
        # await get_users_with_post(session=session)
        # await get_posts_with_authors(session=session)
        # await get_users_with_post_and_profiles(session=session)
        await get_profiles_with_user_and_user_with_posts(session=session)


async def demo_m2m(session: AsyncSession):
    await create_products_and_products(session)
    # await demo_get_orders_with_products_through_secondary(session)
    await demo_get_orders_with_products_with_assoc(session)


async def main():
    async with db_helper.session_factory() as session:
        await demo_m2m(session)
        # await main_relations(session)


if __name__ == "__main__":
    asyncio.run(main())
