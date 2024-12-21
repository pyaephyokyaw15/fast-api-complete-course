from typing import Optional, Annotated
from fastapi import FastAPI, Query, Path, HTTPException, status
from pydantic import BaseModel, Field


BOOKS = []

app = FastAPI()


class Book(BaseModel):
    # id: Optional[int] = None
    id: Optional[int] = Field(description="ID is not required for POST requests", default=None)
    title: str = Field(min_length=3)  # https://fastapi.tiangolo.com/tutorial/body-fields/
    author: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    rating: int = Field(ge=1, le=5)


class BookRequest(BaseModel):
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    rating: int = Field(ge=1, le=5)

    # https://fastapi.tiangolo.com/tutorial/schema-extra-example/#extra-json-schema-data-in-pydantic-models
    model_config = {
        "json_schema_extra": {
            "examples": [

                {
                    "title": "The Great Gatsby",
                    "author": "F. Scott Fitzgerald",
                    "description": "A novel set in the Jazz Age that tells the story of Jay Gatsby's unrequited love "
                                   "for Daisy Buchanan.",
                    "rating": 5
                },
            ]
        }
    }


class FilterParams(BaseModel):
    # https://fastapi.tiangolo.com/tutorial/query-param-models/#query-parameters-with-a-pydantic-model
    rating: Optional[int] = Field(5, gt=0, le=5)
    author: Optional[str] = None


# GET: Return books with query filter
@app.get("/books", response_model=list[Book])
# https://fastapi.tiangolo.com/tutorial/query-param-models/#query-parameters-with-a-pydantic-model
async def read_all_books(filter_query: Annotated[FilterParams, Query()]) -> list[Book]:
    """Return all books with optional filters"""
    filtered_books = BOOKS
    if filter_query.rating:
        filtered_books = [book for book in filtered_books if book.rating == filter_query.rating]
    if filter_query.author:
        filtered_books = [book for book in filtered_books if book.author.casefold() == filter_query.author.casefold()]
    return filtered_books


# GET: get a book by its ID
@app.get("/books/{book_id}", response_model=Book | dict)
async def read_book(book_id: Annotated[int, Path(gt=0)]):
    # https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/#order-the-parameters-as-you-need
    """Return a book by its ID"""
    # return next((book for book in BOOKS if book.id == book_id), {})
    for book in BOOKS:
        if book.id == book_id:
            return book
    # https://fastapi.tiangolo.com/tutorial/handling-errors/
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not found")


# POST: Create a new book
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
# https://fastapi.tiangolo.com/tutorial/response-model/#response_model-parameter
# https://fastapi.tiangolo.com/tutorial/extra-models/#multiple-models
# https://fastapi.tiangolo.com/tutorial/response-status-code/#shortcut-to-remember-the-names
async def create_book(book: BookRequest):
    """Create a new book"""
    new_book = Book(**book.model_dump(), id=generate_next_book_id())
    BOOKS.append(new_book)
    return new_book


# PUT: Update a book by its ID
@app.put("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_id: Annotated[int, Path(gt=0)], book: BookRequest):
    """Update a book by its ID"""
    for i, b in enumerate(BOOKS):
        if b.id == book_id:
            BOOKS[i] = Book(**book.model_dump(), id=book_id)
            # return BOOKS[i]
            return
    # return {}
    # https://fastapi.tiangolo.com/tutorial/handling-errors/
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not found")


# DELETE: Delete a book by its ID
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: Annotated[int, Path(gt=0)]):
    """Delete a book by its ID"""
    for i, b in enumerate(BOOKS):
        if b.id == book_id:
            # return BOOKS.pop(i)
            return
    # return {}
    # https://fastapi.tiangolo.com/tutorial/handling-errors/
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not found")


def generate_next_book_id() -> int:
    return 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
