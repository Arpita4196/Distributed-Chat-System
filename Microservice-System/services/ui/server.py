from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import os, time, jwt, grpc

# flat stubs (generated in the Dockerfile protoc step)
import gateway_pb2 as gp
import gateway_pb2_grpc as gpg
import auth_pb2 as ap
import room_pb2 as rp
import presence_pb2 as pp
import message_pb2 as mp

GATEWAY_ADDR = os.getenv("GATEWAY_ADDR", "gateway:50055")
COOKIE_NAME = "sms_token"
DISPLAY_NAME_COOKIE = "sms_display_name"

app = FastAPI(title="SMS UI (FastAPI)")
app.mount("/static", StaticFiles(directory="services/ui/static"), name="static")
templates = Jinja2Templates(directory="services/ui/templates")

def stub():
    ch = grpc.insecure_channel(GATEWAY_ADDR)
    return gpg.GatewayServiceStub(ch)

def parse_user_id(token: str) -> Optional[str]:
    try:
        data = jwt.decode(token, options={"verify_signature": False})
        return data.get("sub")
    except Exception:
        return None

def get_token(request: Request) -> Optional[str]:
    return request.cookies.get(COOKIE_NAME)

def require_auth(request: Request) -> str:
    tok = get_token(request)
    if not tok:
        raise HTTPException(401, "not authenticated")
    uid = parse_user_id(tok)
    if not uid:
        raise HTTPException(401, "bad token")
    return uid

# -------- Pages --------

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    # redirect to app if already logged in
    tok = get_token(request)
    if tok and parse_user_id(tok):
        return RedirectResponse("/app", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
def app_page(request: Request):
    uid = require_auth(request)
    
    # Try to get display name from auth service first, fallback to cookie
    display_name = request.cookies.get(DISPLAY_NAME_COOKIE, "")
    try:
        user = stub().GetUser(ap.UserId(user_id=uid))
        if user.display_name:
            display_name = user.display_name
    except Exception:
        # If we can't get from auth service, use cookie value
        pass
    
    return templates.TemplateResponse("app.html", {"request": request, "user_id": uid, "display_name": display_name})

@app.post("/api/profile/setname")
async def api_setname(payload: dict, response: Response, request: Request):
    require_auth(request)
    name = (payload.get("display_name") or "").strip()
    response.set_cookie(DISPLAY_NAME_COOKIE, name, samesite="Lax")
    return {"ok": True}

# -------- Auth API --------

@app.post("/api/register")
async def api_register(payload: dict, response: Response):
    email = payload.get("email"); pw = payload.get("password"); display_name = payload.get("display_name") or ""
    try:
        resp = stub().Register(ap.RegisterRequest(email=email, password=pw, display_name=display_name))
        response.set_cookie(COOKIE_NAME, resp.access_token, httponly=True, samesite="Lax")
        if display_name:
            response.set_cookie(DISPLAY_NAME_COOKIE, display_name, samesite="Lax")
        return {"ok": True}
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(400, "Email already registered. Please try logging in instead.")
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(400, "Invalid email or password format. Please check your input.")
        else:
            raise HTTPException(500, "Registration failed. Please try again.")
    except Exception as e:
        raise HTTPException(500, "Registration failed. Please try again.")

@app.post("/api/login")
async def api_login(payload: dict, response: Response):
    email = payload.get("email"); pw = payload.get("password")
    try:
        resp = stub().Login(ap.LoginRequest(email=email, password=pw))
        response.set_cookie(COOKIE_NAME, resp.access_token, httponly=True, samesite="Lax")
        
        # Get user info to retrieve display name
        try:
            # Parse JWT to get user_id
            import jwt
            token_data = jwt.decode(resp.access_token, options={"verify_signature": False})
            user_id = token_data.get('sub')
            if user_id:
                user = stub().GetUser(ap.UserId(user_id=user_id))
                if user.display_name:
                    response.set_cookie(DISPLAY_NAME_COOKIE, user.display_name, samesite="Lax")
        except Exception:
            # If we can't get display name, that's okay - user_id will be shown
            pass
            
        return {"ok": True}
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            raise HTTPException(401, "Invalid email or password. Please check your credentials or register first.")
        elif e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(401, "User not found. Please register first.")
        else:
            raise HTTPException(500, "Login failed. Please try again or register first.")
    except Exception as e:
        raise HTTPException(500, "Login failed. Please try again or register first.")

@app.post("/api/logout")
async def api_logout(request: Request, response: Response):
    tok = get_token(request)
    if tok:
        try:
            stub().Logout(ap.Token(access_token=tok))
        except Exception:
            pass
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}

# -------- Rooms & Presence --------

@app.post("/api/room/create")
async def api_create_room(request: Request, payload: dict):
    require_auth(request)
    rid = payload.get("room_id", "").strip()
    name = payload.get("name", "").strip()
    
    # Validate both room_id and name are provided
    if not rid:
        raise HTTPException(400, "Room ID is required")
    if not name:
        raise HTTPException(400, "Room name is required")
    
    ack = stub().CreateRoom(rp.CreateRoomReq(room_id=rid, name=name))
    if not ack.success:
        raise HTTPException(400, ack.error or "create failed")
    return {"ok": True}

@app.post("/api/room/join")
async def api_join(request: Request, payload: dict):
    tok = get_token(request); uid = parse_user_id(tok) if tok else None
    if not uid: raise HTTPException(401, "not authenticated")
    rid = payload.get("room_id")
    ack = stub().JoinRoom(rp.JoinLeaveReq(room_id=rid, user_id=uid))
    if not ack.success:
        raise HTTPException(400, ack.error or "join failed")
    return {"ok": True}

@app.get("/api/room/list")
async def api_list_rooms(request: Request):
    # naive: list all rooms and filter to ones where user is a member
    tok = get_token(request); uid = parse_user_id(tok) if tok else None
    if not uid: raise HTTPException(401, "not authenticated")

    rooms = [r for r in stub().ListRooms(rp.Empty())]
    result = []
    for r in rooms:
        members = [m.user_id for m in stub().ListMembers(rp.RoomId(room_id=r.room_id))]
        if uid in members:
            result.append({"room_id": r.room_id, "name": r.name})
    return {"rooms": result}

@app.get("/api/presence/roster")
async def api_roster(request: Request, room_id: str):
    require_auth(request)
    r = stub().Roster(pp.RoomId(room_id=room_id))
    return {"users": [{"user_id": u.user_id, "display_name": u.display_name} for u in r.users]}

@app.post("/api/presence/heartbeat")
async def api_heartbeat(request: Request, payload: dict):
    tok = get_token(request); uid = parse_user_id(tok) if tok else None
    if not uid: raise HTTPException(401, "not authenticated")
    rid = payload.get("room_id")
    # Get display name from payload first, then from cookies as fallback
    display_name = payload.get("display_name") or request.cookies.get(DISPLAY_NAME_COOKIE, "")
    stub().Heartbeat(pp.HeartbeatReq(room_id=rid, user_id=uid, display_name=display_name))
    return {"ok": True}

# -------- User Lookup --------

@app.get("/api/user/lookup")
async def api_user_lookup(request: Request, user_id: str):
    require_auth(request)
    # For now, we'll use the presence service to get display names
    # In a real system, you might want to store display names in the auth service
    try:
        # Try to get from presence service first
        roster_responses = []
        # Get all rooms the user might be in
        rooms_resp = await api_list_rooms(request)
        rooms = rooms_resp.get('rooms', [])
        
        for room in rooms:
            try:
                roster = stub().Roster(pp.RoomId(room_id=room['room_id']))
                for user in roster.users:
                    if user.user_id == user_id:
                        return {"user_id": user_id, "display_name": user.display_name}
            except:
                continue
        
        # If not found in presence, return user_id as fallback
        return {"user_id": user_id, "display_name": user_id}
    except Exception:
        return {"user_id": user_id, "display_name": user_id}

# -------- Messages --------

@app.post("/api/message/append")
async def api_append(request: Request, payload: dict):
    tok = get_token(request); uid = parse_user_id(tok) if tok else None
    if not uid: raise HTTPException(401, "not authenticated")
    rid = payload.get("room_id"); text = payload.get("text", "")
    idem = f"web-{int(time.time()*1000)}"
    resp = stub().Append(mp.AppendReq(room_id=rid, user_id=uid, text=text, idempotency_key=idem))
    if not resp.success: raise HTTPException(400, "append failed")
    return {"ok": True, "offset": resp.offset}

@app.get("/api/message/list")
async def api_list(request: Request, room_id: str, from_offset: int = 0, limit: int = 100):
    require_auth(request)
    msgs = [m for m in stub().List(mp.ListReq(room_id=room_id, from_offset=from_offset, limit=limit))]
    
    # Get display names from auth service for all unique user_ids
    user_ids = list(set(m.user_id for m in msgs))
    name_map = {}
    
    for user_id in user_ids:
        try:
            user = stub().GetUser(ap.UserId(user_id=user_id))
            name_map[user_id] = user.display_name or user_id
        except:
            name_map[user_id] = user_id
    
    out = []
    for m in msgs:
        display_name = name_map.get(m.user_id, m.user_id)
        out.append({
            "offset": m.offset, 
            "ts_ms": m.ts_ms, 
            "user_id": m.user_id, 
            "display_name": display_name,
            "text": m.text
        })
    
    return {"messages": out}
