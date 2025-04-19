"""
создайте асинхронные функции для выполнения запросов к ресурсам (используйте aiohttp)
"""
from aiohttp import ClientSession
from copy import copy

from models import User, Post

USERS_DATA_URL = 'https://jsonplaceholder.typicode.com/users'
POSTS_DATA_URL = 'https://jsonplaceholder.typicode.com/posts'


async def fetch_json(session: ClientSession, url: str):
    async with session.get(url=url) as response:
        result = await response.json()
        return result


async def filter_data(model, data):
    field_names = {column.name for column in model.__table__.columns}
    return {key: value for key, value in data.items() if key in field_names}


async def fetch_users_data(session: ClientSession):
    users = await fetch_json(session, USERS_DATA_URL)
    filtered_users = [User(**await filter_data(User, user_data)) for user_data in users]
    users_ids = [user.id for user in filtered_users]
    return filtered_users, users_ids


async def fetch_posts_data(session: ClientSession):
    posts = await fetch_json(session, POSTS_DATA_URL)
    filtered_posts = [Post(**await filter_data(Post, post_data)) for post_data in posts]
    return filtered_posts


async def compile_posts_data(posts: list[Post], ids: list[str]):
    posts_data = copy(posts)
    i = 0
    while i < len(ids):
        for user_id in ids:
            for post in posts_data[i:i+10]:
                post.user_id = user_id
            i += 10
    return posts_data