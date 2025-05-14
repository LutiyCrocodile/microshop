import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy.engine import Result
from core.models import db_helper, User, Profile, Post
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


async def main():
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


if __name__ == "__main__":
    asyncio.run(main())
