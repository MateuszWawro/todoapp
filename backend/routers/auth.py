from fastapi import APIRouter, HTTPException, Depends
from database import database
from security import hash_password, verify_password, create_token, generate_api_token, get_current_user
from models.schemas import RegisterIn, LoginIn

router = APIRouter()


@router.post("/register", status_code=201)
async def register(data: RegisterIn):
    if await database.fetch_one(
        "SELECT id FROM users WHERE email=:e OR username=:u",
        {"e": data.email, "u": data.username}
    ):
        raise HTTPException(400, "Użytkownik już istnieje")

    user_id = await database.fetch_val(
        "INSERT INTO users (username,email,password_hash,api_token) VALUES (:u,:e,:pw,:t) RETURNING id",
        {"u": data.username, "e": data.email,
         "pw": hash_password(data.password), "t": generate_api_token()}
    )
    row = await database.fetch_one(
        "SELECT id, username, email, api_token FROM users WHERE id=:id", {"id": user_id}
    )
    return {**dict(row), "token": create_token(user_id)}


@router.post("/login")
async def login(data: LoginIn):
    user = await database.fetch_one(
        "SELECT id, password_hash FROM users WHERE username=:u", {"u": data.username}
    )
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Nieprawidłowy login lub hasło")
    return {"token": create_token(user["id"])}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    row = await database.fetch_one(
        "SELECT id, username, email, api_token, created_at FROM users WHERE id=:id",
        {"id": user["id"]}
    )
    return dict(row)


@router.post("/regenerate-token")
async def regenerate_token(user=Depends(get_current_user)):
    t = generate_api_token()
    await database.execute(
        "UPDATE users SET api_token=:t WHERE id=:id", {"t": t, "id": user["id"]}
    )
    return {"api_token": t}
