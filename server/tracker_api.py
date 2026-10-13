"""Tracker endpoints, and the single tick rule shared by the app and Claude Code:
no passing verification record, no tick."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server import tracker as tr
from server.paths import Paths
from server.verifications import VerificationLog, verify_kind

RECENT = 6


class CheckRefused(Exception):
    pass


def check_item(paths: Paths, item_id: str, checked: bool = True) -> tr.Tracker:
    """Tick or untick one item under the tracker lock. Unticking is always
    allowed; ticking needs an unlocked week and a passing verification."""
    log = VerificationLog(paths.verifications)
    with tr.locked(paths.tracker_lock):
        t = tr.load(paths.tracker)
        try:
            item = t.item(item_id)
        except KeyError:
            raise KeyError(f"no item {item_id} in the tracker") from None
        if checked and not item.checked:
            if not t.item_unlocked(item_id):
                week = t.week_of(item_id)
                where = f"week {week.n}" if week else "the completion section"
                raise CheckRefused(f"{item_id}: {where} is locked until the previous week is complete")
            if not log.has_pass(item_id):
                raise CheckRefused(f"{item_id}: no passing record in progress/verifications.jsonl")
        if item.checked != checked:
            t.set_checked(item_id, checked)
            tr.write_atomic(paths.tracker, t.serialize())
    return t


def item_json(i: tr.Item, verified: set[str]) -> dict:
    return {"id": i.id, "text": i.text, "checked": i.checked, "verified": i.id in verified,
            "verify": verify_kind(i.text)}


def tracker_json(t: tr.Tracker, log: VerificationLog) -> dict:
    records = log.read()
    verified = {r.item for r in records if r.passed}
    current = t.current()
    return {
        "weeks": [{
            "n": w.n,
            "title": w.title,
            "focus": w.focus,
            "pitfalls": w.pitfalls,
            "unlocked": t.week_unlocked(w.n),
            "done": sum(i.checked for i in w.items),
            "total": len(w.items),
            "tasks": [{
                "id": task.id,
                "title": task.title,
                "kind": task.kind,
                "items": [item_json(i, verified) for i in task.items],
            } for task in w.tasks],
        } for w in t.weeks],
        "completion": {
            "unlocked": t.completion_unlocked(),
            "items": [item_json(i, verified) for i in t.completion],
        },
        "current": None if current is None else {
            "week": current[0].n if current[0] else None,
            "task": current[1].id if current[1] else None,
            "task_title": current[1].title if current[1] else "Completion",
            "item": item_json(current[2], verified),
        },
        "recent": [r.model_dump() for r in reversed(records[-RECENT:])],
    }


class CheckRequest(BaseModel):
    item: str
    checked: bool = True


def router(paths: Paths) -> APIRouter:
    r = APIRouter(prefix="/api/tracker")
    log = VerificationLog(paths.verifications)

    def parse_error(e: tr.TrackerError) -> JSONResponse:
        return JSONResponse({"detail": str(e), "line": e.line_no}, status_code=422)

    @r.get("")
    def get_tracker():
        try:
            return tracker_json(tr.load(paths.tracker), log)
        except tr.TrackerError as e:
            return parse_error(e)

    @r.post("/check")
    def post_check(body: CheckRequest):
        try:
            t = check_item(paths, body.item, body.checked)
        except tr.TrackerError as e:
            return parse_error(e)
        except KeyError as e:
            raise HTTPException(404, e.args[0]) from None
        except CheckRefused as e:
            raise HTTPException(409, str(e)) from None
        return tracker_json(t, log)

    return r
