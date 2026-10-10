from fastmcp import FastMCP
mcp = FastMCP("CineBot")

@mcp.tool()
def risky_lookup(booking_id: str) -> str:
    """Look up a booking -- fails if the ID format is wrong."""
    if not booking_id.startswith("BK"):
        raise ValueError(f"Invalid booking ID format: {booking_id!r}. Expected it to start with 'BK'.")
    return f"Booking {booking_id}: confirmed."

if __name__ == "__main__":
    mcp.run()
