from fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("CineBot")

@mcp.tool()
def check_showtimes(movie_title: str) -> str:
    """Check available showtimes for a movie."""
    fake_showtimes = {
        "interstellar": "7:00 PM and 10:15 PM",
        "dune part two": "9:30 PM",
    }
    return fake_showtimes.get(movie_title.lower(), "No showtimes found.")

@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def cancel_booking(booking_id: str) -> str:
    """Cancel an existing booking. Irreversible."""
    return f"Booking {booking_id} cancelled."

@mcp.tool()
def get_seat_map(movie_title: str) -> dict:
    """Get the seat map for a movie -- returns structured data, not just text."""
    return {"movie": movie_title, "available_rows": ["A", "B", "C"], "sold_out_rows": ["D"]}

if __name__ == "__main__":
    mcp.run()
