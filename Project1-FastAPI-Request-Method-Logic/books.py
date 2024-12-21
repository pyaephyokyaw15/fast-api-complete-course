from fastapi import FastAPI

BOOKS = [
    {"id": 1, "title": "Harry Potter", "author": "J.K. Rowling", "category": "fantasy"},
    {"id": 2, "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "category": "fantasy"},
    {"id": 3, "title": "The Alchemist", "author": "Paulo Coelho", "category": "adventure"},
    {"id": 4, "title": "The Da Vinci Code", "author": "Dan Brown", "category": "mystery"},
    {"id": 5, "title": "The Little Prince", "author": "Antoine de Saint-Exupéry", "category": "fantasy"},
]


app = FastAPI()

# GET: Return all books
# @app.get("/books")
# async def read_all_books() -> list[dict]:
#     """Return all books"""
#     return BOOKS


# GET: Path parameters
@app.get("/books/{book_id}")
async def read_book(book_id: int) -> dict:
    """Return a book by its ID"""
    return next((book for book in BOOKS if book["id"] == book_id), {})


# GET: Query parameters
@app.get("/books")
async def read_books_by_query(category: str) -> list[dict]:
    """Return books by category"""
    print("book[category]:", category)
    print("query case:", category.casefold())
    return [book for book in BOOKS if book["category"].casefold() == category.casefold()]


# POST: Create a new book
@app.post("/books")
async def create_book(book: dict) -> dict:
    """Create a new book"""
    BOOKS.append(book)
    return book


# PUT: Update a book
@app.put("/books/{book_id}")
async def update_book(book_id: int, book: dict) -> dict:
    """Update a book by its ID"""
    for i, b in enumerate(BOOKS):
        if b["id"] == book_id:
            BOOKS[i] = book
            return book
    return {}


# DELETE: Delete a book
@app.delete("/books/{book_id}")
async def delete_book(book_id: int) -> dict:
    """Delete a book by its ID"""
    for i, b in enumerate(BOOKS):
        if b["id"] == book_id:
            return BOOKS.pop(i)
    return {}
