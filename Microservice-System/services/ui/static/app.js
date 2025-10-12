let state = {
  currentRoom: null,
  lastSeen: 0,
  heartbeatTimer: null,
  pollTimer: null
};

window.addEventListener('load', async () => {
  await refreshRooms();
  // Auto-select General Chat room if it exists
  await autoSelectGeneralChat();
});

async function logout(){
  await post('/api/logout', {});
  location.href = '/';
}

async function refreshRooms(){
  const res = await get('/api/room/list');
  const box = el('rooms');
  box.innerHTML = '';
  (res.rooms || []).forEach(r => {
    const div = document.createElement('div');
    div.className = 'item' + (state.currentRoom === r.room_id ? ' active' : '');
    div.textContent = `${r.name} (${r.room_id})`;
    div.onclick = () => selectRoom(r.room_id, r.name);
    box.appendChild(div);
  });
}

async function createRoom(){
  const room_id = val('newRoomId').trim();
  const name = val('newRoomName').trim();
  
  // Validate both room ID and name are provided
  if(!room_id) {
    banner('Please enter a room ID', false);
    return;
  }
  if(!name) {
    banner('Please enter a room name', false);
    return;
  }
  
  try {
    await post('/api/room/create', {room_id, name});
    await joinRoom(room_id);
    await refreshRooms();
    selectRoom(room_id, name);
    set('newRoomId',''); set('newRoomName','');
    banner('Room created successfully!', true);
  } catch(error) {
    banner('Failed to create room: ' + error.message, false);
  }
}

async function joinNew(){
  const room_id = val('newRoomId').trim();
  if(!room_id) return;
  await joinRoom(room_id);
  await refreshRooms();
  selectRoom(room_id, room_id);
  set('newRoomId','');
}

async function joinRoom(room_id){
  await post('/api/room/join', {room_id});
}

async function selectRoom(room_id, name){
  state.currentRoom = room_id;
  state.lastSeen = 0;
  el('roomTitle').textContent = `Room: ${name} (${room_id})`;
  el('messages').innerHTML = '';
  // kick presence & polling
  startHeartbeat();
  // Load all messages first, then start polling
  await loadMessages();
  startPolling();
  // refresh room list highlighting
  refreshRooms();
}

function startHeartbeat(){
  if(state.heartbeatTimer) clearInterval(state.heartbeatTimer);
  state.heartbeatTimer = setInterval(()=>{
    const displayName = document.cookie.split(';').find(c => c.trim().startsWith('sms_display_name='));
    const name = displayName ? decodeURIComponent(displayName.split('=')[1]) : '';
    post('/api/presence/heartbeat', {room_id: state.currentRoom, display_name: name});
  }, 5000);
  // send one immediately
  const displayName = document.cookie.split(';').find(c => c.trim().startsWith('sms_display_name='));
  const name = displayName ? decodeURIComponent(displayName.split('=')[1]) : '';
  post('/api/presence/heartbeat', {room_id: state.currentRoom, display_name: name}).catch(()=>{});
}

function startPolling(){
  if(state.pollTimer) clearInterval(state.pollTimer);
  state.pollTimer = setInterval(loadMessages, 1000);
  loadMessages(); // prime
}


async function loadMessages(){
  if(!state.currentRoom) return;

  const fromOffset = state.lastSeen === 0 ? 0 : state.lastSeen + 1;
  const res = await get(`/api/message/list?room_id=${encodeURIComponent(state.currentRoom)}&from_offset=${fromOffset}&limit=200`);
  const msgs = res.messages || [];
  const list = el('messages');
  msgs.forEach(m => {
    // Use display_name from API response, fallback to user_id
    const sender = m.display_name || m.user_id;
    const div = document.createElement('div');
    div.className = 'msg';
    div.innerHTML = `<b>${escapeHtml(sender)}</b>: ${escapeHtml(m.text)}`;
    list.appendChild(div);
    state.lastSeen = Math.max(state.lastSeen, m.offset);
  });
  if(msgs.length > 0) list.scrollTop = list.scrollHeight;
}

function banner(msg, ok=true){
  let b = document.getElementById("banner");
  if(!b){
    b = document.createElement("div");
    b.id = "banner";
    b.style.cssText = "position:fixed;top:8px;left:50%;transform:translateX(-50%);padding:8px 12px;border-radius:8px;color:#fff;z-index:9999";
    document.body.appendChild(b);
  }
  b.style.background = ok ? "#16a34a" : "#dc2626";
  b.textContent = msg;
  setTimeout(()=>{ b.textContent = ""; }, 2500);
}

async function saveName(){
  const n = val('newDisplayName').trim();
  try{
    await post('/api/profile/setname', {display_name: n});
    banner("Name saved");
    // hard refresh header text
    location.reload();
  }catch(e){
    console.error(e);
    banner("Failed to save name", false);
  }
}

async function send(){
  const t = val('text').trim();
  if(!state.currentRoom){
    banner("Select or join a room first", false);
    return;
  }
  if(!t){
    banner("Type a message", false);
    return;
  }
  try{
    await post('/api/message/append', {room_id: state.currentRoom, text: t});
    set('text','');
    // next poll will pick it up; optionally force a quick fetch:
    // loadMessages();
  }catch(e){
    console.error(e);
    banner("Failed to send message", false);
  }
}

function val(id){ return document.getElementById(id).value; }
function set(id,v){ document.getElementById(id).value = v; }
function el(id){ return document.getElementById(id); }
function escapeHtml(s){ return s.replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m])); }

async function post(url, body){
  const r = await fetch(url, {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(body)});
  if(!r.ok) throw new Error(await r.text());
  return await r.json();
}
async function get(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error(await r.text());
  return await r.json();
}

async function autoSelectGeneralChat(){
  const res = await get('/api/room/list');
  const generalRoom = (res.rooms || []).find(r => r.room_id === 'general');
  if (generalRoom) {
    await selectRoom('general', 'General Chat');
  }
}
