import argparse

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier
from mcp.types import ToolAnnotations

AUTH_TOKEN = "cinebot-secret-token"


class StaticTokenVerifier(TokenVerifier):
    """Accepts requests whose bearer token exactly matches AUTH_TOKEN."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if token == AUTH_TOKEN:
            return AccessToken(token=token, client_id="cinebot-client", scopes=[])
        return None


mcp = FastMCP("CineBot", auth=StaticTokenVerifier())

@mcp.tool()
def check_showtimes(movie_title: str) -> str:
    """Check available showtimes for a movie."""
    fake_showtimes = {
        "interstellar": "7:00 PM and 10:15 PM",
        "dune part two": "9:30 PM",
    }
    return fake_showtimes.get(movie_title.lower(), "No showtimes found.")

@mcp.tool(annotations=ToolAnnotations(destructiveHint=True,requiredAuthentication=True))
def cancel_booking(booking_id: str) -> str:
    """Cancel an existing booking. Irreversible."""
    return f"Booking {booking_id} cancelled."

@mcp.tool()
def get_seat_map(movie_title: str) -> dict:
    """Get the seat map for a movie -- returns structured data, not just text."""
    return {"movie": movie_title, "available_rows": ["A", "B", "C"], "sold_out_rows": ["D"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the authenticated HTTP server instead of the default stdio server.",
    )
    args = parser.parse_args()

    if args.http:
        mcp.run(transport="http", port=8000)
    else:
        mcp.run(transport="stdio", show_banner=False)
