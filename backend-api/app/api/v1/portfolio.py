"""Portfolio and Watchlist API endpoints."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.stock import (
    HoldingIn, HoldingOut, PortfolioResponse,
    WatchlistCreate, WatchlistItemIn, WatchlistOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["portfolio"])

# ---------------------------------------------------------------------------
# In-memory stores for POC (replace with DB in production)
# ---------------------------------------------------------------------------
_portfolios: dict[int, dict] = {}
_holdings_store: dict[int, list[dict]] = {}
_watchlists_store: dict[int, dict] = {}
_wl_items_store: dict[int, list[dict]] = {}
_id_counter = {"portfolio": 1, "holding": 1, "watchlist": 1, "wl_item": 1}


def _next_id(kind: str) -> int:
    val = _id_counter[kind]
    _id_counter[kind] += 1
    return val


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

@router.get("/api/portfolio/{user_id}", response_model=PortfolioResponse)
async def get_portfolio(user_id: str):
    """Get portfolio for a user."""
    # Find or create portfolio for user
    portfolio_id = None
    for pid, p in _portfolios.items():
        if p["user_id"] == user_id:
            portfolio_id = pid
            break

    if portfolio_id is None:
        portfolio_id = _next_id("portfolio")
        _portfolios[portfolio_id] = {"user_id": user_id, "name": "My Portfolio"}
        _holdings_store[portfolio_id] = []

    holdings_raw = _holdings_store.get(portfolio_id, [])

    total_invested = sum(h["quantity"] * h["avg_price"] for h in holdings_raw)
    holdings_out = []
    for h in holdings_raw:
        invested = h["quantity"] * h["avg_price"]
        holdings_out.append({
            "id": h["id"],
            "symbol": h["symbol"],
            "company_name": h.get("company_name", h["symbol"]),
            "exchange": h["exchange"],
            "quantity": h["quantity"],
            "avg_price": h["avg_price"],
            "current_price": None,
            "invested_value": invested,
            "current_value": None,
            "unrealized_pnl": None,
            "unrealized_pnl_pct": None,
        })

    return {
        "portfolio_id": portfolio_id,
        "total_invested": total_invested,
        "total_current_value": None,
        "total_unrealized_pnl": None,
        "total_unrealized_pnl_pct": None,
        "holdings": holdings_out,
    }


@router.post("/api/portfolio/{user_id}/holdings", status_code=201)
async def add_holding(user_id: str, holding: HoldingIn):
    """Add a stock holding to the user's portfolio."""
    portfolio_id = None
    for pid, p in _portfolios.items():
        if p["user_id"] == user_id:
            portfolio_id = pid
            break
    if portfolio_id is None:
        portfolio_id = _next_id("portfolio")
        _portfolios[portfolio_id] = {"user_id": user_id, "name": "My Portfolio"}
        _holdings_store[portfolio_id] = []

    holding_id = _next_id("holding")
    _holdings_store[portfolio_id].append({
        "id": holding_id,
        **holding.model_dump(),
    })
    return {"id": holding_id, "message": "Holding added successfully"}


@router.delete("/api/portfolio/{user_id}/holdings/{holding_id}", status_code=204)
async def remove_holding(user_id: str, holding_id: int):
    """Remove a holding from portfolio."""
    for pid, p in _portfolios.items():
        if p["user_id"] == user_id:
            holdings = _holdings_store.get(pid, [])
            _holdings_store[pid] = [h for h in holdings if h["id"] != holding_id]
            return
    raise HTTPException(status_code=404, detail="Portfolio not found")


# ---------------------------------------------------------------------------
# Watchlist
# ---------------------------------------------------------------------------

@router.get("/api/watchlists/{user_id}", response_model=list[WatchlistOut])
async def get_watchlists(user_id: str):
    """Get all watchlists for a user."""
    result = []
    for wid, w in _watchlists_store.items():
        if w["user_id"] == user_id:
            items = _wl_items_store.get(wid, [])
            result.append({"id": wid, "name": w["name"], "items": items})
    return result


@router.post("/api/watchlists/{user_id}", response_model=WatchlistOut, status_code=201)
async def create_watchlist(user_id: str, body: WatchlistCreate):
    """Create a new watchlist."""
    wid = _next_id("watchlist")
    _watchlists_store[wid] = {"user_id": user_id, "name": body.name}
    _wl_items_store[wid] = []
    return {"id": wid, "name": body.name, "items": []}


@router.post("/api/watchlists/{user_id}/{watchlist_id}/items", status_code=201)
async def add_to_watchlist(user_id: str, watchlist_id: int, item: WatchlistItemIn):
    """Add a stock to a watchlist."""
    w = _watchlists_store.get(watchlist_id)
    if not w or w["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    item_id = _next_id("wl_item")
    _wl_items_store[watchlist_id].append({"id": item_id, **item.model_dump()})
    return {"id": item_id, "message": "Stock added to watchlist"}


@router.delete("/api/watchlists/{user_id}/{watchlist_id}/items/{item_id}", status_code=204)
async def remove_from_watchlist(user_id: str, watchlist_id: int, item_id: int):
    """Remove a stock from a watchlist."""
    w = _watchlists_store.get(watchlist_id)
    if not w or w["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    _wl_items_store[watchlist_id] = [
        i for i in _wl_items_store.get(watchlist_id, []) if i["id"] != item_id
    ]


@router.delete("/api/watchlists/{user_id}/{watchlist_id}", status_code=204)
async def delete_watchlist(user_id: str, watchlist_id: int):
    """Delete an entire watchlist."""
    w = _watchlists_store.get(watchlist_id)
    if not w or w["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    _watchlists_store.pop(watchlist_id, None)
    _wl_items_store.pop(watchlist_id, None)
