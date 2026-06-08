"""FastAPI dashboard — live experiment feed, lesson browser, stats, and reports."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse

from agent.config.settings import settings
from agent.monitoring.metrics import get_prometheus_metrics

app = FastAPI(
    title="Perpetual Scholar Agent",
    description="Autonomous research agent dashboard",
    version="0.1.0",
)

DB_PATH = str(settings.data_dir / "psa.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Render live experiment feed — last 20 experiments with status and reward."""
    conn = _get_db()
    try:
        rows = conn.execute(
            """SELECT e.id, e.technique_name, e.status, e.ops_per_sec,
                      e.baseline_ops_per_sec, e.reward, e.created_at, e.completed_at,
                      s.title AS source_title
               FROM experiments e
               LEFT JOIN seen_items s ON e.source_item_id = s.id
               ORDER BY e.created_at DESC
               LIMIT 20"""
        ).fetchall()

        rows_lessons = conn.execute(
            "SELECT COUNT(*) AS cnt FROM lessons"
        ).fetchone()

        rows_success = conn.execute(
            "SELECT COUNT(*) AS cnt FROM experiments WHERE status = 'success'"
        ).fetchone()

        rows_total = conn.execute(
            "SELECT COUNT(*) AS cnt FROM experiments"
        ).fetchone()

        rows_avg_reward = conn.execute(
            "SELECT AVG(reward) AS avg FROM lessons WHERE reward > 0"
        ).fetchone()

        total_lessons = rows_lessons["cnt"] if rows_lessons else 0
        total_success = rows_success["cnt"] if rows_success else 0
        total_experiments = rows_total["cnt"] if rows_total else 0
        avg_reward = rows_avg_reward["avg"] if rows_avg_reward and rows_avg_reward["avg"] else 0.0

        html_rows = ""
        for r in rows:
            status_color = {"success": "#22c55e", "failed": "#ef4444", "pending": "#f59e0b", "running": "#3b82f6"}.get(r["status"] or "pending", "#94a3b8")
            improvement = f"+{((r['ops_per_sec'] or 0) - (r['baseline_ops_per_sec'] or 0)) / (r['baseline_ops_per_sec'] or 1) * 100:.1f}%" if r["ops_per_sec"] and r["baseline_ops_per_sec"] else "—"
            html_rows += f"""<tr>
                <td>{r['id']}</td>
                <td>{(r['technique_name'] or '—')[:40]}</td>
                <td><span style="color:{status_color};font-weight:bold">{r['status']}</span></td>
                <td>{r['ops_per_sec'] or '—'}</td>
                <td>{improvement}</td>
                <td>{r['reward'] or '—'}</td>
                <td>{r['created_at'] or '—'}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html><head><title>Perpetual Scholar Agent</title>
<style>
body {{ font-family: -apple-system, system-ui, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
h1 {{ color: #38bdf8; }} h2 {{ color: #94a3b8; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
th {{ background: #1e293b; padding: 0.5rem 1rem; text-align: left; color: #94a3b8; }}
td {{ padding: 0.5rem 1rem; border-bottom: 1px solid #1e293b; }}
.stats {{ display: flex; gap: 2rem; margin: 1rem 0; }}
.stat {{ background: #1e293b; padding: 1rem 2rem; border-radius: 0.5rem; }}
.stat .value {{ font-size: 2rem; font-weight: bold; color: #38bdf8; }}
.stat .label {{ color: #94a3b8; font-size: 0.85rem; }}
nav a {{ color: #38bdf8; margin-right: 1rem; text-decoration: none; }}
nav a:hover {{ text-decoration: underline; }}
</style></head><body>
<h1>🔬 Perpetual Scholar Agent</h1>
<nav><a href="/">Experiments</a><a href="/lessons">Lessons</a><a href="/stats">Stats</a><a href="/metrics">Metrics</a><a href="/reports/latest">Latest Report</a></nav>
<div class="stats">
    <div class="stat"><div class="value">{total_lessons}</div><div class="label">Lessons Stored</div></div>
    <div class="stat"><div class="value">{total_experiments}</div><div class="label">Total Experiments</div></div>
    <div class="stat"><div class="value">{total_success}</div><div class="label">Successful</div></div>
    <div class="stat"><div class="value">{avg_reward:.3f}</div><div class="label">Avg Reward</div></div>
</div>
<h2>Recent Experiments</h2>
<table><tr><th>ID</th><th>Technique</th><th>Status</th><th>ops/s</th><th>Improvement</th><th>Reward</th><th>Time</th></tr>
{html_rows}</table></body></html>"""
    finally:
        conn.close()


@app.get("/lessons")
async def list_lessons(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
):
    """Paginated lesson browser with optional text search."""
    conn = _get_db()
    try:
        offset = (page - 1) * per_page
        where = ""
        params: list = []
        if search:
            where = "WHERE technique_name LIKE ? OR problem_desc LIKE ?"
            params = [f"%{search}%", f"%{search}%"]

        total = conn.execute(f"SELECT COUNT(*) FROM lessons {where}", params).fetchone()[0]

        rows = conn.execute(
            f"""SELECT id, technique_name, problem_desc, ops_per_sec, baseline_ops_per_sec,
                       improvement_pct, reward, source_url, source_title, created_at
                FROM lessons {where}
                ORDER BY reward DESC
                LIMIT ? OFFSET ?""",
            (*params, per_page, offset),
        ).fetchall()

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "lessons": [dict(r) for r in rows],
        }
    finally:
        conn.close()


@app.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: int):
    """Get full details of a single lesson including verified code."""
    conn = _get_db()
    try:
        row = conn.execute(
            """SELECT * FROM lessons WHERE id = ?""",
            (lesson_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        return dict(row)
    finally:
        conn.close()


@app.get("/stats")
async def get_stats():
    """Aggregate statistics: total experiments, success rate, avg reward, lessons stored."""
    conn = _get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        success = conn.execute("SELECT COUNT(*) FROM experiments WHERE status = 'success'").fetchone()[0]
        lessons = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
        avg_reward_row = conn.execute("SELECT AVG(reward) FROM lessons WHERE reward > 0").fetchone()
        avg_reward = avg_reward_row[0] if avg_reward_row and avg_reward_row[0] else 0.0

        top_lesson = conn.execute(
            "SELECT technique_name, reward, improvement_pct FROM lessons ORDER BY reward DESC LIMIT 1"
        ).fetchone()

        recent_24h = conn.execute(
            "SELECT COUNT(*) FROM experiments WHERE created_at >= datetime('now', '-1 day')"
        ).fetchone()[0]

        return {
            "total_experiments": total,
            "successful_experiments": success,
            "success_rate": success / total if total > 0 else 0.0,
            "lessons_stored": lessons,
            "avg_reward": round(avg_reward, 4),
            "top_lesson": dict(top_lesson) if top_lesson else None,
            "experiments_last_24h": recent_24h,
        }
    finally:
        conn.close()


@app.get("/reports/latest", response_class=PlainTextResponse)
async def latest_report():
    """Return the latest weekly digest Markdown report."""
    import glob
    reports_dir = settings.data_dir / "reports"
    if not reports_dir.exists():
        raise HTTPException(status_code=404, detail="No reports found")

    reports = sorted(reports_dir.glob("digest_*.md"), reverse=True)
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")

    return reports[0].read_text(encoding="utf-8")


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus-format metrics endpoint."""
    return get_prometheus_metrics()


def run_dashboard():
    """Start the FastAPI dashboard server."""
    import uvicorn
    uvicorn.run(
        "agent.dashboard:app",
        host=settings.fastapi_dashboard_host,
        port=settings.fastapi_dashboard_port,
        log_level=settings.log_level.lower(),
    )
