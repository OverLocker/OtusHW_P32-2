import asyncio
from fastapi import FastAPI, HTTPException
from sqlalchemy.future import select
from models import User, Post, Base, engine, Session
from aiohttp import ClientTimeout, ClientSession
from jsonplaceholder_requests import fetch_users_data, fetch_posts_data, compile_posts_data

app = FastAPI()


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session = ClientSession(timeout=ClientTimeout(total=5.0))
    users_data, posts_data = await asyncio.gather(
        fetch_users_data(session),
        fetch_posts_data(session)
    )

    users, ids = users_data
    posts = await compile_posts_data(posts_data, ids)

    await session.close()

    async with Session() as session:
        async with session.begin():
            session.add_all(users)
            session.add_all(posts)

        await session.commit()


@app.on_event("startup")
async def startup_event():
    await async_main()


@app.get("/users")
async def get_users():
    async with Session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users


@app.get("/posts")
async def get_posts():
    async with Session() as session:
        result = await session.execute(select(Post))
        posts = result.scalars().all()
        return posts


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with Session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user


@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    async with Session() as session:
        result = await session.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        return post


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)