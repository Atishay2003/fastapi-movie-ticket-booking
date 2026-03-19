from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="Movie Ticket Booking System",
    description="A complete FastAPI backend for movie ticket booking - Feb Internship 2026 Final Project",
    version="1.0.0"
)

# ============================================================
# DATABASE (In-Memory)
# ============================================================

movies_db = [
    {
        "id": 1,
        "title": "Inception",
        "genre": "Sci-Fi",
        "director": "Christopher Nolan",
        "release_year": 2010,
        "rating": 8.8,
        "duration_minutes": 148,
        "language": "English",
        "available_seats": 120,
        "ticket_price": 250.0
    },
    {
        "id": 2,
        "title": "The Dark Knight",
        "genre": "Action",
        "director": "Christopher Nolan",
        "release_year": 2008,
        "rating": 9.0,
        "duration_minutes": 152,
        "language": "English",
        "available_seats": 100,
        "ticket_price": 300.0
    },
    {
        "id": 3,
        "title": "Interstellar",
        "genre": "Sci-Fi",
        "director": "Christopher Nolan",
        "release_year": 2014,
        "rating": 8.6,
        "duration_minutes": 169,
        "language": "English",
        "available_seats": 80,
        "ticket_price": 350.0
    },
    {
        "id": 4,
        "title": "Parasite",
        "genre": "Thriller",
        "director": "Bong Joon-ho",
        "release_year": 2019,
        "rating": 8.5,
        "duration_minutes": 132,
        "language": "Korean",
        "available_seats": 60,
        "ticket_price": 200.0
    },
    {
        "id": 5,
        "title": "The Shawshank Redemption",
        "genre": "Drama",
        "director": "Frank Darabont",
        "release_year": 1994,
        "rating": 9.3,
        "duration_minutes": 142,
        "language": "English",
        "available_seats": 50,
        "ticket_price": 280.0
    },
    {
        "id": 6,
        "title": "Pulp Fiction",
        "genre": "Crime",
        "director": "Quentin Tarantino",
        "release_year": 1994,
        "rating": 8.9,
        "duration_minutes": 154,
        "language": "English",
        "available_seats": 70,
        "ticket_price": 220.0
    },
    {
        "id": 7,
        "title": "RRR",
        "genre": "Action",
        "director": "S.S. Rajamouli",
        "release_year": 2022,
        "rating": 8.0,
        "duration_minutes": 187,
        "language": "Telugu",
        "available_seats": 150,
        "ticket_price": 180.0
    },
    {
        "id": 8,
        "title": "Spirited Away",
        "genre": "Animation",
        "director": "Hayao Miyazaki",
        "release_year": 2001,
        "rating": 8.6,
        "duration_minutes": 125,
        "language": "Japanese",
        "available_seats": 90,
        "ticket_price": 200.0
    },
    {
        "id": 9,
        "title": "Avengers: Endgame",
        "genre": "Action",
        "director": "Anthony Russo",
        "release_year": 2019,
        "rating": 8.4,
        "duration_minutes": 181,
        "language": "English",
        "available_seats": 200,
        "ticket_price": 400.0
    },
    {
        "id": 10,
        "title": "The Godfather",
        "genre": "Crime",
        "director": "Francis Ford Coppola",
        "release_year": 1972,
        "rating": 9.2,
        "duration_minutes": 175,
        "language": "English",
        "available_seats": 40,
        "ticket_price": 320.0
    }
]

# Cart: user_id -> list of cart items
cart_db = {}

# Orders: order_id -> order details
orders_db = {}

# Delivery/Tickets: order_id -> delivery status
delivery_db = {}

# Counters
order_counter = 1
cart_item_counter = 1


# ============================================================
# PYDANTIC MODELS
# ============================================================

class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Movie title")
    genre: str = Field(..., min_length=1, max_length=50, description="Movie genre")
    director: str = Field(..., min_length=1, max_length=100, description="Director name")
    release_year: int = Field(..., ge=1900, le=2030, description="Release year")
    rating: float = Field(..., ge=0.0, le=10.0, description="Movie rating out of 10")
    duration_minutes: int = Field(..., ge=1, le=600, description="Duration in minutes")
    language: str = Field(..., min_length=1, max_length=50, description="Language")
    available_seats: int = Field(..., ge=0, description="Number of available seats")
    ticket_price: float = Field(..., gt=0, description="Ticket price")


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    director: Optional[str] = Field(None, min_length=1, max_length=100)
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    language: Optional[str] = Field(None, min_length=1, max_length=50)
    available_seats: Optional[int] = Field(None, ge=0)
    ticket_price: Optional[float] = Field(None, gt=0)


class CartItem(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    movie_id: int = Field(..., ge=1, description="Movie ID")
    quantity: int = Field(..., ge=1, le=10, description="Number of tickets (1-10)")


class OrderCreate(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")


class CheckInRequest(BaseModel):
    order_id: int = Field(..., ge=1, description="Order ID")


class CheckOutRequest(BaseModel):
    order_id: int = Field(..., ge=1, description="Order ID")
    feedback: Optional[str] = Field(None, max_length=500, description="Optional feedback")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Rating 1-5")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_movie_by_id(movie_id: int):
    """Find a movie by its ID"""
    for movie in movies_db:
        if movie["id"] == movie_id:
            return movie
    return None


def find_movie_index(movie_id: int):
    """Find index of a movie by its ID"""
    for index, movie in enumerate(movies_db):
        if movie["id"] == movie_id:
            return index
    return -1


def calculate_cart_total(user_id: str):
    """Calculate total price for a user's cart"""
    if user_id not in cart_db or len(cart_db[user_id]) == 0:
        return 0.0
    total = 0.0
    for item in cart_db[user_id]:
        movie = find_movie_by_id(item["movie_id"])
        if movie:
            total += movie["ticket_price"] * item["quantity"]
    return total


def get_next_movie_id():
    """Generate next movie ID"""
    if not movies_db:
        return 1
    return max(m["id"] for m in movies_db) + 1


def filter_movies(movies, genre=None, language=None, min_rating=None, max_price=None):
    """Filter movies based on criteria"""
    results = movies.copy()
    if genre is not None:
        results = [m for m in results if m["genre"].lower() == genre.lower()]
    if language is not None:
        results = [m for m in results if m["language"].lower() == language.lower()]
    if min_rating is not None:
        results = [m for m in results if m["rating"] >= min_rating]
    if max_price is not None:
        results = [m for m in results if m["ticket_price"] <= max_price]
    return results


# ============================================================
# DAY 1: GET APIs
# ============================================================

# Q1 — Home Route
@app.get("/", tags=["Day 1 - GET APIs"])
def home():
    """Q1: Home route - Welcome message"""
    return {
        "message": "Welcome to Movie Ticket Booking System!",
        "project": "FastAPI Movie Ticket Booking",
        "developer": "Your Name",
        "version": "1.0.0",
        "docs": "Visit /docs for Swagger UI"
    }


# Q2 — Get All Movies
@app.get("/movies", tags=["Day 1 - GET APIs"])
def get_all_movies():
    """Q2: List all movies available in the system"""
    return {
        "status": "success",
        "total_movies": len(movies_db),
        "movies": movies_db
    }


# Q3 — Movies Summary/Count
@app.get("/movies/summary", tags=["Day 1 - GET APIs"])
def get_movies_summary():
    """Q3: Get summary and count of all movies"""
    genres = {}
    languages = {}
    total_seats = 0
    total_revenue_potential = 0.0

    for movie in movies_db:
        genres[movie["genre"]] = genres.get(movie["genre"], 0) + 1
        languages[movie["language"]] = languages.get(movie["language"], 0) + 1
        total_seats += movie["available_seats"]
        total_revenue_potential += movie["available_seats"] * movie["ticket_price"]

    avg_rating = sum(m["rating"] for m in movies_db) / len(movies_db) if movies_db else 0
    avg_price = sum(m["ticket_price"] for m in movies_db) / len(movies_db) if movies_db else 0

    return {
        "status": "success",
        "total_movies": len(movies_db),
        "genres_breakdown": genres,
        "languages_breakdown": languages,
        "total_available_seats": total_seats,
        "average_rating": round(avg_rating, 2),
        "average_ticket_price": round(avg_price, 2),
        "total_revenue_potential": round(total_revenue_potential, 2)
    }


# Q4 — Get Movie by ID
@app.get("/movies/{movie_id}", tags=["Day 1 - GET APIs"])
def get_movie_by_id(movie_id: int):
    """Q4: Get a specific movie by its ID"""
    movie = find_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return {
        "status": "success",
        "movie": movie
    }


# ============================================================
# DAY 2: POST + PYDANTIC VALIDATION
# ============================================================

# Q5 — Add New Movie (POST with Pydantic Validation)
@app.post("/movies", status_code=201, tags=["Day 2 - POST + Pydantic"])
def add_movie(movie: MovieCreate):
    """Q5: Add a new movie with Pydantic validation"""
    # Check for duplicate title
    for existing in movies_db:
        if existing["title"].lower() == movie.title.lower():
            raise HTTPException(status_code=400, detail=f"Movie '{movie.title}' already exists")

    new_movie = {
        "id": get_next_movie_id(),
        "title": movie.title,
        "genre": movie.genre,
        "director": movie.director,
        "release_year": movie.release_year,
        "rating": movie.rating,
        "duration_minutes": movie.duration_minutes,
        "language": movie.language,
        "available_seats": movie.available_seats,
        "ticket_price": movie.ticket_price
    }
    movies_db.append(new_movie)
    return {
        "status": "success",
        "message": f"Movie '{movie.title}' added successfully",
        "movie": new_movie
    }


# Q6 — Add to Cart (POST with validation)
@app.post("/cart", status_code=201, tags=["Day 2 - POST + Pydantic"])
def add_to_cart(cart_item: CartItem):
    """Q6: Add movie tickets to user's cart with validation"""
    global cart_item_counter

    movie = find_movie_by_id(cart_item.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {cart_item.movie_id} not found")

    if cart_item.quantity > movie["available_seats"]:
        raise HTTPException(
            status_code=400,
            detail=f"Only {movie['available_seats']} seats available for '{movie['title']}'"
        )

    if cart_item.user_id not in cart_db:
        cart_db[cart_item.user_id] = []

    # Check if movie already in cart for this user
    for item in cart_db[cart_item.user_id]:
        if item["movie_id"] == cart_item.movie_id:
            item["quantity"] += cart_item.quantity
            item["subtotal"] = item["quantity"] * movie["ticket_price"]
            return {
                "status": "success",
                "message": f"Updated quantity for '{movie['title']}' in cart",
                "cart_item": item,
                "cart_total": calculate_cart_total(cart_item.user_id)
            }

    new_cart_item = {
        "cart_item_id": cart_item_counter,
        "user_id": cart_item.user_id,
        "movie_id": cart_item.movie_id,
        "movie_title": movie["title"],
        "quantity": cart_item.quantity,
        "ticket_price": movie["ticket_price"],
        "subtotal": movie["ticket_price"] * cart_item.quantity
    }
    cart_item_counter += 1
    cart_db[cart_item.user_id].append(new_cart_item)

    return {
        "status": "success",
        "message": f"Added {cart_item.quantity} ticket(s) for '{movie['title']}' to cart",
        "cart_item": new_cart_item,
        "cart_total": calculate_cart_total(cart_item.user_id)
    }


# Q7 — View Cart
@app.get("/cart/{user_id}", tags=["Day 2 - POST + Pydantic"])
def view_cart(user_id: str):
    """Q7: View user's cart contents"""
    if user_id not in cart_db or len(cart_db[user_id]) == 0:
        raise HTTPException(status_code=404, detail=f"Cart is empty for user '{user_id}'")

    return {
        "status": "success",
        "user_id": user_id,
        "cart_items": cart_db[user_id],
        "total_items": sum(item["quantity"] for item in cart_db[user_id]),
        "cart_total": calculate_cart_total(user_id)
    }


# ============================================================
# DAY 3: HELPER FUNCTIONS + QUERY PARAMETERS
# ============================================================

# Q8 — Search Movies by Keyword
@app.get("/movies/search/keyword", tags=["Day 3 - Helper Functions"])
def search_movies_by_keyword(
    keyword: str = Query(..., min_length=1, description="Search keyword for title or director")
):
    """Q8: Search movies by keyword in title or director name"""
    results = [
        m for m in movies_db
        if keyword.lower() in m["title"].lower() or keyword.lower() in m["director"].lower()
    ]

    if not results:
        raise HTTPException(status_code=404, detail=f"No movies found matching '{keyword}'")

    return {
        "status": "success",
        "keyword": keyword,
        "total_results": len(results),
        "movies": results
    }


# Q9 — Filter Movies by Genre, Language, Rating, Price
@app.get("/movies/filter/advanced", tags=["Day 3 - Helper Functions"])
def filter_movies_advanced(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    language: Optional[str] = Query(None, description="Filter by language"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="Minimum rating"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum ticket price")
):
    """Q9: Filter movies using helper function with multiple query parameters"""
    results = filter_movies(movies_db, genre, language, min_rating, max_price)

    if not results:
        raise HTTPException(status_code=404, detail="No movies found matching the given filters")

    return {
        "status": "success",
        "filters_applied": {
            "genre": genre,
            "language": language,
            "min_rating": min_rating,
            "max_price": max_price
        },
        "total_results": len(results),
        "movies": results
    }


# Q10 — Get Movie Revenue Estimate
@app.get("/movies/{movie_id}/revenue", tags=["Day 3 - Helper Functions"])
def get_movie_revenue(movie_id: int):
    """Q10: Calculate potential revenue for a movie using helper functions"""
    movie = find_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    potential_revenue = movie["available_seats"] * movie["ticket_price"]
    return {
        "status": "success",
        "movie_title": movie["title"],
        "ticket_price": movie["ticket_price"],
        "available_seats": movie["available_seats"],
        "potential_revenue": round(potential_revenue, 2)
    }


# ============================================================
# DAY 4: CRUD OPERATIONS
# ============================================================

# Q11 — Update Movie (PUT)
@app.put("/movies/{movie_id}", tags=["Day 4 - CRUD Operations"])
def update_movie(movie_id: int, movie_update: MovieUpdate):
    """Q11: Update an existing movie's details"""
    index = find_movie_index(movie_id)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    update_data = movie_update.dict(exclude_unset=True, exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for key, value in update_data.items():
        movies_db[index][key] = value

    return {
        "status": "success",
        "message": f"Movie with ID {movie_id} updated successfully",
        "updated_movie": movies_db[index]
    }


# Q12 — Delete Movie (DELETE)
@app.delete("/movies/{movie_id}", tags=["Day 4 - CRUD Operations"])
def delete_movie(movie_id: int):
    """Q12: Delete a movie from the system"""
    index = find_movie_index(movie_id)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    deleted_movie = movies_db.pop(index)
    return {
        "status": "success",
        "message": f"Movie '{deleted_movie['title']}' deleted successfully",
        "deleted_movie": deleted_movie
    }


# Q13 — Remove Item from Cart (DELETE)
@app.delete("/cart/{user_id}/{movie_id}", tags=["Day 4 - CRUD Operations"])
def remove_from_cart(user_id: str, movie_id: int):
    """Q13: Remove a specific movie from user's cart"""
    if user_id not in cart_db or len(cart_db[user_id]) == 0:
        raise HTTPException(status_code=404, detail=f"Cart not found for user '{user_id}'")

    for i, item in enumerate(cart_db[user_id]):
        if item["movie_id"] == movie_id:
            removed_item = cart_db[user_id].pop(i)
            return {
                "status": "success",
                "message": f"Removed '{removed_item['movie_title']}' from cart",
                "removed_item": removed_item,
                "cart_total": calculate_cart_total(user_id)
            }

    raise HTTPException(
        status_code=404,
        detail=f"Movie ID {movie_id} not found in cart for user '{user_id}'"
    )


# Q14 — Update Cart Item Quantity (PUT)
@app.put("/cart/{user_id}/{movie_id}", tags=["Day 4 - CRUD Operations"])
def update_cart_quantity(user_id: str, movie_id: int, quantity: int = Query(..., ge=1, le=10)):
    """Q14: Update ticket quantity for a movie in user's cart"""
    if user_id not in cart_db or len(cart_db[user_id]) == 0:
        raise HTTPException(status_code=404, detail=f"Cart not found for user '{user_id}'")

    movie = find_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    if quantity > movie["available_seats"]:
        raise HTTPException(
            status_code=400,
            detail=f"Only {movie['available_seats']} seats available"
        )

    for item in cart_db[user_id]:
        if item["movie_id"] == movie_id:
            item["quantity"] = quantity
            item["subtotal"] = quantity * movie["ticket_price"]
            return {
                "status": "success",
                "message": f"Updated quantity to {quantity} for '{movie['title']}'",
                "cart_item": item,
                "cart_total": calculate_cart_total(user_id)
            }

    raise HTTPException(
        status_code=404,
        detail=f"Movie ID {movie_id} not found in cart for user '{user_id}'"
    )


# ============================================================
# DAY 5: MULTI-STEP WORKFLOW (Cart → Order → Check-in → Check-out)
# ============================================================

# Q15 — Place Order from Cart (Cart → Order)
@app.post("/orders", status_code=201, tags=["Day 5 - Multi-Step Workflow"])
def place_order(order: OrderCreate):
    """Q15: Place an order from user's cart (Cart → Order)"""
    global order_counter

    if order.user_id not in cart_db or len(cart_db[order.user_id]) == 0:
        raise HTTPException(status_code=400, detail=f"Cart is empty for user '{order.user_id}'")

    cart_items = cart_db[order.user_id]
    total_amount = calculate_cart_total(order.user_id)

    # Check seat availability and reduce seats
    for item in cart_items:
        movie = find_movie_by_id(item["movie_id"])
        if not movie:
            raise HTTPException(status_code=404, detail=f"Movie ID {item['movie_id']} not found")
        if item["quantity"] > movie["available_seats"]:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough seats for '{movie['title']}'. Available: {movie['available_seats']}"
            )

    # Reduce available seats
    for item in cart_items:
        movie = find_movie_by_id(item["movie_id"])
        movie["available_seats"] -= item["quantity"]

    new_order = {
        "order_id": order_counter,
        "user_id": order.user_id,
        "items": cart_items.copy(),
        "total_amount": round(total_amount, 2),
        "status": "confirmed",
        "order_date": datetime.now().isoformat(),
        "checked_in": False,
        "checked_out": False
    }

    orders_db[order_counter] = new_order
    order_counter += 1

    # Clear cart
    cart_db[order.user_id] = []

    return {
        "status": "success",
        "message": "Order placed successfully!",
        "order": new_order
    }


# Q16 — Check-in (Order → Check-in)
@app.post("/orders/checkin", tags=["Day 5 - Multi-Step Workflow"])
def check_in(request: CheckInRequest):
    """Q16: Check-in for a booked order (Order → Check-in)"""
    if request.order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Order ID {request.order_id} not found")

    order = orders_db[request.order_id]

    if order["status"] == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot check-in for a cancelled order")

    if order["checked_in"]:
        raise HTTPException(status_code=400, detail="Already checked in for this order")

    order["checked_in"] = True
    order["status"] = "checked-in"
    order["checkin_time"] = datetime.now().isoformat()

    # Create delivery/ticket record
    delivery_db[request.order_id] = {
        "order_id": request.order_id,
        "user_id": order["user_id"],
        "ticket_status": "active",
        "checkin_time": order["checkin_time"],
        "checkout_time": None
    }

    return {
        "status": "success",
        "message": f"Successfully checked in for Order #{request.order_id}",
        "order": order,
        "ticket": delivery_db[request.order_id]
    }


# Q17 — Check-out (Check-in → Check-out)
@app.post("/orders/checkout", tags=["Day 5 - Multi-Step Workflow"])
def check_out(request: CheckOutRequest):
    """Q17: Check-out after movie (Check-in → Check-out)"""
    if request.order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Order ID {request.order_id} not found")

    order = orders_db[request.order_id]

    if not order["checked_in"]:
        raise HTTPException(status_code=400, detail="Must check-in before checking out")

    if order["checked_out"]:
        raise HTTPException(status_code=400, detail="Already checked out for this order")

    order["checked_out"] = True
    order["status"] = "completed"
    order["checkout_time"] = datetime.now().isoformat()
    order["feedback"] = request.feedback
    order["customer_rating"] = request.rating

    # Update delivery record
    if request.order_id in delivery_db:
        delivery_db[request.order_id]["ticket_status"] = "used"
        delivery_db[request.order_id]["checkout_time"] = order["checkout_time"]

    return {
        "status": "success",
        "message": f"Successfully checked out for Order #{request.order_id}. Thank you!",
        "order": order
    }


# Q18 — View Order History
@app.get("/orders/{user_id}/history", tags=["Day 5 - Multi-Step Workflow"])
def get_order_history(user_id: str):
    """Q18: View complete booking history for a user"""
    user_orders = [
        order for order in orders_db.values()
        if order["user_id"] == user_id
    ]

    if not user_orders:
        raise HTTPException(status_code=404, detail=f"No orders found for user '{user_id}'")

    total_spent = sum(o["total_amount"] for o in user_orders)

    return {
        "status": "success",
        "user_id": user_id,
        "total_orders": len(user_orders),
        "total_amount_spent": round(total_spent, 2),
        "orders": user_orders
    }


# ============================================================
# DAY 6: ADVANCED APIs (Search, Sort, Pagination, Combined Browse)
# ============================================================

# Q19 — Sorted Movies with Pagination
@app.get("/movies/browse/sorted", tags=["Day 6 - Advanced APIs"])
def get_sorted_movies(
    sort_by: str = Query("rating", description="Sort field: rating, ticket_price, release_year, title, duration_minutes"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(5, ge=1, le=20, description="Items per page")
):
    """Q19: Get sorted movies with pagination"""
    valid_sort_fields = ["rating", "ticket_price", "release_year", "title", "duration_minutes", "available_seats"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field. Valid options: {valid_sort_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'")

    reverse = order == "desc"
    sorted_movies = sorted(movies_db, key=lambda x: x[sort_by], reverse=reverse)

    # Pagination
    total_movies = len(sorted_movies)
    total_pages = (total_movies + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated = sorted_movies[start:end]

    return {
        "status": "success",
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "per_page": per_page,
        "total_movies": total_movies,
        "total_pages": total_pages,
        "movies": paginated
    }


# Q20 — Combined Browse Endpoint (Search + Filter + Sort + Pagination)
@app.get("/movies/browse/combined", tags=["Day 6 - Advanced APIs"])
def combined_browse(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    language: Optional[str] = Query(None, description="Filter by language"),
    min_rating: Optional[float] = Query(None, ge=0, le=10, description="Minimum rating"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price"),
    sort_by: str = Query("rating", description="Sort by: rating, ticket_price, release_year, title"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(5, ge=1, le=20, description="Results per page")
):
    """Q20: Combined browse with search + filter + sort + pagination"""
    # Step 1: Start with all movies
    results = movies_db.copy()

    # Step 2: Keyword search
    if keyword is not None:
        results = [
            m for m in results
            if keyword.lower() in m["title"].lower()
            or keyword.lower() in m["director"].lower()
            or keyword.lower() in m["genre"].lower()
        ]

    # Step 3: Apply filters using helper function
    results = filter_movies(results, genre, language, min_rating, max_price)

    # Step 4: Sort
    valid_sort_fields = ["rating", "ticket_price", "release_year", "title", "duration_minutes"]
    if sort_by not in valid_sort_fields:
        sort_by = "rating"

    reverse = order == "desc"
    results = sorted(results, key=lambda x: x[sort_by], reverse=reverse)

    # Step 5: Pagination
    total_results = len(results)
    total_pages = (total_results + per_page - 1) // per_page if total_results > 0 else 0
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    return {
        "status": "success",
        "filters_applied": {
            "keyword": keyword,
            "genre": genre,
            "language": language,
            "min_rating": min_rating,
            "max_price": max_price
        },
        "sorting": {
            "sort_by": sort_by,
            "order": order
        },
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_results": total_results,
            "total_pages": total_pages
        },
        "movies": paginated
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)