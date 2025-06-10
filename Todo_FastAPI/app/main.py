from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
# from api.router.todo import todo_router

app = FastAPI()     # Created an instance. Here, instance is app.
# app.include_router(todo_router)

# Function name can be anything, it may be same, may be diff. Actually it doesn't matter.
# What actually matter is to maintain the decorum and it's good if the coder give diff names for diff funcs. 
# ("/") -> called as 'path' in Fastapi.
# @app -> called path operation decorator.
@app.get("/")
def index():
    return {"status": "blog is ruuning"}


@app.get("/blog")       # this is called the decorator.
def index(limit: int = 10, published: bool = True, sort: Optional[str]=None):
    # only get 10 published blog
    if published:
        return {"data": f"{limit} published blogs from the database"}
    else:
        return {"data": f"{limit} blogs from the database"}


@app.get('/blog/unpublished')
def unpublished():
    return {'data': 'all unpublished blogs'}

@app.get('/blog/{blog_id}')
def show(blog_id: int):
    # fetch blog with blog_id
    return {'data': blog_id}


@app.get('/blog/{blog_id}/comments')
def comments(blog_id, limit: int=10):
    return {'data': limit}


class Blog(BaseModel):
    title: str
    body: str
    published: Optional[bool]




@app.post('/blog')
def create_blog(request: Blog):
    # return request
    return {'data': "Blog is created with title as {blog.title}"}

