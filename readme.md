# 🎬 Movie Ticket Booking System - FastAPI Backend

A complete real-world FastAPI backend application for movie ticket booking, built as part of the Feb Internship 2026 Final Project.

## 🚀 Features

- **GET APIs** - Home route, list movies, get by ID, summary
- **POST APIs** with Pydantic validation - Add movies, cart management
- **Helper Functions** - find_movie(), calculate_total(), filter_logic()
- **CRUD Operations** - Create, Read, Update, Delete movies and cart items
- **Multi-Step Workflow** - Cart → Order → Check-in → Check-out
- **Advanced APIs** - Search, Sorting, Pagination, Combined Browse

## 📋 20 API Endpoints

| Q# | Method | Endpoint | Description |
|----|--------|----------|-------------|
| Q1 | GET | `/` | Home route |
| Q2 | GET | `/movies` | List all movies |
| Q3 | GET | `/movies/summary` | Movies summary & count |
| Q4 | GET | `/movies/{movie_id}` | Get movie by ID |
| Q5 | POST | `/movies` | Add new movie |
| Q6 | POST | `/cart` | Add to cart |
| Q7 | GET | `/cart/{user_id}` | View cart |
| Q8 | GET | `/movies/search/keyword` | Search by keyword |
| Q9 | GET | `/movies/filter/advanced` | Filter movies |
| Q10 | GET | `/movies/{movie_id}/revenue` | Revenue estimate |
| Q11 | PUT | `/movies/{movie_id}` | Update movie |
| Q12 | DELETE | `/movies/{movie_id}` | Delete movie |
| Q13 | DELETE | `/cart/{user_id}/{movie_id}` | Remove from cart |
| Q14 | PUT | `/cart/{user_id}/{movie_id}` | Update cart quantity |
| Q15 | POST | `/orders` | Place order |
| Q16 | POST | `/orders/checkin` | Check-in |
| Q17 | POST | `/orders/checkout` | Check-out |
| Q18 | GET | `/orders/{user_id}/history` | Order history |
| Q19 | GET | `/movies/browse/sorted` | Sorted + Pagination |
| Q20 | GET | `/movies/browse/combined` | Combined browse |

## 🛠 Setup & Run

```bash
pip install -r requirements.txt
python main.py