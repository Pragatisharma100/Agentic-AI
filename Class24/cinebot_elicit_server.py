from fastmcp import FastMCP, Context

mcp = FastMCP("CineBotElicit")

@mcp.tool()
async def cancel_booking_confirm(booking_id: str, ctx: Context) -> str:
    """Cancel a booking, but ask the caller to confirm first."""
    result = await ctx.elicit(
        f"Confirm cancellation of booking {booking_id}?",
        response_type=bool,
    )
    if result.action != "accept":
        return f"Cancellation of {booking_id} aborted ({result.action})."
    if not result.data:
        return f"Cancellation of {booking_id} aborted (user said no)."
    return f"Booking {booking_id}: cancelled."

if __name__ == "__main__":
    mcp.run()
