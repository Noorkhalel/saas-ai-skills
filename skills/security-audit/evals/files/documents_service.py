"""Multi-tenant document service. Users belong to organizations;
documents belong to organizations. FastAPI + asyncpg + Supabase-style JWT."""
import hashlib
import jwt
from fastapi import FastAPI, Request, Header
import asyncpg

app = FastAPI()
DB_POOL = None
JWT_SECRET = "supersecret"


async def get_pool():
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = await asyncpg.create_pool(
            "postgresql://app:app@localhost/docs"
        )
    return DB_POOL


def current_user(authorization: str):
    token = authorization.split(" ")[1]
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256", "none"])


@app.get("/documents")
async def list_documents(request: Request, authorization: str = Header(None)):
    user = current_user(authorization)
    org_id = request.query_params.get("org_id", user["org_id"])
    pool = await get_pool()
    rows = await pool.fetch(
        f"SELECT * FROM documents WHERE org_id = {org_id}"
    )
    return [dict(r) for r in rows]


@app.get("/documents/{doc_id}")
async def get_document(doc_id: str, authorization: str = Header(None)):
    current_user(authorization)
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM documents WHERE id = $1", doc_id
    )
    return dict(row)


@app.post("/users/register")
async def register(request: Request):
    body = await request.json()
    pw_hash = hashlib.md5(body["password"].encode()).hexdigest()
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO users (email, password, role, org_id) "
        "VALUES ($1, $2, $3, $4)",
        body["email"], pw_hash, body.get("role", "member"), body["org_id"],
    )
    return {"ok": True}


@app.get("/admin/export")
async def export_all(authorization: str = Header(None)):
    user = current_user(authorization)
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM documents")
    return [dict(r) for r in rows]
