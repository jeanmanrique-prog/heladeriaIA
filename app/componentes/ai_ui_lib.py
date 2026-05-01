import streamlit as st
import base64
from pathlib import Path

def _is_dark_color(value: str) -> bool:
    color = (value or "").strip().lower()
    if color in {"", "#fff", "#ffffff", "white"}:
        return False
    return False

def get_ai_call_html(
    api_url, 
    saved_sid, 
    is_fresh, 
    avatar_src, 
    urban_src, 
    user_src="👤",
    accent_color="#FF4B7D", 
    bg_color="#F7F7F7", 
    text_color="#222222",
    card_bg="#ffffff",
    border_color="#FF4B7D"
):
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');

  * {{ 
    box-sizing: border-box; 
    margin: 0; 
    padding: 0; 
    font-family: 'Outfit', sans-serif; 
  }}

  html, body {{
    height: 100%;
    width: 100%;
    overflow: hidden;
    background-color: {bg_color};
    color: {text_color};
  }}
  
  .app-layout {{
    display: flex;
    width: 100vw;
    height: 100vh;
    padding: 20px;
    gap: 30px;
    background-color: {bg_color};
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }}
  
  /* ── Columna Izquierda: Conversación en Vivo ── */
  .transcription-panel {{
    width: 400px;
    height: 620px;
    display: flex;
    flex-direction: column;
    background: transparent;
    overflow: hidden;
  }}
  
  .panel-header {{
    margin-bottom: 15px;
  }}
  
  .panel-title-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }}
  
  .panel-icon {{
    color: #A855F7;
    font-size: 1.4rem;
  }}
  
  .panel-title {{
    font-weight: 800;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #333;
  }}
  
  .panel-subtitle {{
    color: #666;
    font-size: 0.85rem;
  }}

  .chat-wrapper {{
    flex: 1;
    background: #FFFFFF;
    border-radius: 35px;
    box-shadow: 0 25px 80px rgba(0,0,0,0.04);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid rgba(0,0,0,0.05);
    position: relative;
    height: 100%;
  }}

  .hist {{
    flex: 1;
    overflow-y: auto;
    padding: 25px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    scrollbar-width: thin;
    scrollbar-color: {accent_color}22 transparent;
  }}

  .hist::-webkit-scrollbar {{ width: 6px; }}
  .hist::-webkit-scrollbar-thumb {{ background: {accent_color}22; border-radius: 10px; }}

  .empty-state {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    padding: 30px;
    color: #888;
  }}
  
  .empty-icon {{
    font-size: 3rem;
    margin-bottom: 15px;
    opacity: 0.5;
    background: linear-gradient(135deg, #FF4B7D, #A855F7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  
  .empty-title {{
    font-weight: 700;
    font-size: 1.2rem;
    color: #333;
    margin-bottom: 8px;
  }}
  
  .empty-text {{
    font-size: 0.9rem;
    max-width: 280px;
    line-height: 1.4;
  }}

  .msg-row {{
    display: flex;
    gap: 12px;
    max-width: 85%;
    animation: slideIn 0.3s ease-out;
  }}
  
  @keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  .msg-avatar {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
  }}
  .msg-avatar img {{ width: 100%; height: 100%; object-fit: cover; }}

  .msg-content {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .msg-meta {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .msg-name {{
    font-weight: 800;
    font-size: 0.85rem;
  }}

  .msg-time {{
    font-size: 0.7rem;
    color: #999;
  }}

  .msg-bubble {{
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 0.9rem;
    line-height: 1.4;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02);
  }}

  .msg-row.ia .msg-bubble {{ background: #FFE4EC; color: #222; border-top-left-radius: 4px; }}
  .msg-row.usr .msg-bubble {{ background: #F1F1F1; color: #222; border-top-right-radius: 4px; }}
  .msg-row.ia .msg-name {{ color: {accent_color}; }}

  .chat-footer {{
    padding: 15px;
    background: #FAFAFA;
    border-top: 1px solid #EEE;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #999;
    font-size: 0.8rem;
    font-weight: 600;
  }}

  .live-indicator {{
    margin: 10px 25px;
    padding: 10px 15px;
    background: #FFF;
    border-radius: 10px;
    font-style: italic;
    color: #888;
    font-size: 0.8rem;
    border-left: 4px solid {accent_color};
    display: flex;
    align-items: center;
  }}

  /* ── Columna Derecha: Panel de Llamada ── */
  .call-panel {{
    width: 400px;
    height: 620px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }}
  
  .call-card {{
    width: 100%;
    height: 100%;
    background: #FFFFFF;
    border-radius: 35px;
    padding: 35px 30px;
    text-align: center;
    box-shadow: 0 25px 80px rgba(255, 75, 125, 0.1);
    border: 1px solid rgba(255, 75, 125, 0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }}

  .call-badge {{
    background: {accent_color};
    color: white;
    padding: 6px 20px;
    border-radius: 50px;
    font-weight: 900;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 25px;
  }}

  .call-title {{
    font-weight: 900;
    font-size: 1.6rem;
    color: #222;
    margin-bottom: 5px;
  }}

  .call-subtitle {{
    color: {accent_color};
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 30px;
    opacity: 0.8;
  }}

  .viz-row {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    width: 100%;
    margin-bottom: 25px;
  }}
  .viz-bars {{ display: flex; gap: 5px; align-items: center; height: 40px; }}
  .v-bar {{ width: 4px; height: 4px; background: {accent_color}55; border-radius: 2px; transition: height 0.1s; }}

  .main-avatar-wrap {{
    width: 150px;
    height: 150px;
    border-radius: 50%;
    border: 6px solid #FFE4EC;
    padding: 10px;
    position: relative;
  }}
  
  .main-avatar {{
    width: 100%; height: 100%; border-radius: 50%;
    background: white; overflow: hidden; display: flex;
    align-items: center; justify-content: center;
    border: 1px solid #EEE;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  }}
  .main-avatar img {{ width: 100%; height: 100%; object-fit: contain; }}
  .main-avatar.speaking {{ animation: pulseAvatar 1.5s infinite; }}
  
  @keyframes pulseAvatar {{
    0% {{ box-shadow: 0 0 0 0px rgba(255, 75, 125, 0.3); }}
    100% {{ box-shadow: 0 0 0 30px rgba(255, 75, 125, 0); }}
  }}

  .timer {{
    font-size: 2.3rem;
    font-weight: 900;
    color: #222;
    margin: 25px 0 10px 0;
    letter-spacing: 2px;
    font-family: 'Courier New', Courier, monospace;
  }}

  .status-row {{
    display: flex; align-items: center; gap: 8px;
    color: #888; font-weight: 600; font-size: 0.9rem; margin-bottom: 35px;
  }}
  .status-dot {{ width: 10px; height: 10px; border-radius: 50%; background: #DDD; }}
  .status-dot.active {{ background: {accent_color}; box-shadow: 0 0 10px {accent_color}AA; }}

  .controls-row {{ display: flex; align-items: center; justify-content: center; gap: 30px; }}
  .btn-sec {{
    width: 55px; height: 55px; border-radius: 50%; background: #F3F3F3; border: none;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; color: {accent_color}; transition: all 0.2s;
  }}
  .btn-sec:hover {{ background: #FFE4EC; transform: translateY(-3px); }}
  .btn-main {{
    width: 80px; height: 80px; border-radius: 50%; background: {accent_color}; border: none;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 2.1rem; color: white; box-shadow: 0 15px 40px rgba(255, 75, 125, 0.35);
  }}
  .btn-main:hover {{ transform: scale(1.05) translateY(-4px); }}
  
  .btn-label {{ font-size: 0.75rem; font-weight: 800; color: #888; text-transform: uppercase; margin-top: 10px; }}
  .control-group {{ display: flex; flex-direction: column; align-items: center; }}
  .error-box {{ margin-top: 20px; padding: 12px; background: #FFF0F0; color: #D32F2F; border-radius: 12px; font-size: 0.85rem; display: none; }}
</style>
</head>
<body>
<div class="app-layout">
  <div class="transcription-panel">
    <div class="panel-header">
      <div class="panel-title-row">
        <span class="panel-icon">💬</span>
        <h2 class="panel-title">Conversación en vivo</h2>
      </div>
      <p class="panel-subtitle">Aquí puedes ver la conversación en tiempo real con Urban.</p>
    </div>
    <div class="chat-wrapper">
      <div class="hist" id="histEl">
        <div class="empty-state" id="emptyState">
          <div class="empty-icon">💬</div>
          <h3 class="empty-title">La conversación aparecerá aquí</h3>
          <p class="empty-text">Inicia la llamada para comenzar a hablar con Urban</p>
        </div>
      </div>
      <div class="live-indicator" id="liveEl" style="display:none;"></div>
      <div class="chat-footer">🚫 Solo puedes ver la conversación. La escritura está deshabilitada.</div>
    </div>
  </div>
  <div class="call-panel">
    <div class="call-card">
      <div class="call-badge">📞 EN LLAMADA</div>
      <h1 class="call-title">Hablando con Urban</h1>
      <p class="call-subtitle">Gelatería Urbana Colombia</p>
      <div class="viz-row">
        <div class="viz-bars" id="viz_L">
          {"".join(f'<div class="v-bar" id="vb_l_{i}"></div>' for i in range(10))}
        </div>
        <div class="main-avatar-wrap">
          <div class="main-avatar" id="avCircle">
             {"<img src='" + avatar_src + "'>" if avatar_src.startswith("data:") else "🍦"}
          </div>
        </div>
        <div class="viz-bars" id="viz_R">
          {"".join(f'<div class="v-bar" id="vb_r_{i}"></div>' for i in range(10))}
        </div>
      </div>
      <div class="timer" id="callTimer">00:00</div>
      <div class="status-row">
        <div class="status-dot" id="statusDot"></div>
        <span id="statusTxt">Desconectado</span>
      </div>
      <div class="controls-row">
        <div class="control-group">
          <button class="btn-sec">🔇</button>
          <span class="btn-label">Mudo</span>
        </div>
        <div class="control-group">
          <button class="btn-main" id="btnStart" onclick="startCall()">📞</button>
          <button class="btn-main" id="btnEnd" onclick="endCall()" style="display:none; background:#FF1744;">📞</button>
          <span class="btn-label" id="mainBtnLabel">Iniciar</span>
        </div>
        <div class="control-group">
          <button class="btn-sec">🔊</button>
          <span class="btn-label">Altavoz</span>
        </div>
      </div>
      <div class="error-box" id="errEl"></div>
    </div>
  </div>
</div>

<script>
const API_URL = "{api_url}";
const SILENCE_MS = 700;
const SPEECH_THR = 55;
const SILENCE_THR = 30;
const MIN_SPEECH_MS = 300;
const CHUNK_INTERVAL = 80;

let sessionId = "{saved_sid}";
let stream = null;
let audioCtx = null;
let analyser = null;
let mediaRecorder = null;
let audioChunks = [];
let isRunning = false;
let isSpeaking = false;
let isProcessing = false;
let isAiSpeaking = false;
let silenceTimer = null;
let speechStartTs = 0;
let currentSrc = null;
let vadTimer = null;
let freshStart = {"true" if is_fresh else "false"};
let callTimerInterval = null;
let callSeconds = 0;

const iaAvatarUrl = "{avatar_src}";
const usrAvatarUrl = "{user_src}";

const histEl = document.getElementById('histEl');
const emptyEl = document.getElementById('emptyState');
const liveEl = document.getElementById('liveEl');
const statusTxt = document.getElementById('statusTxt');
const statusDot = document.getElementById('statusDot');
const avCircle = document.getElementById('avCircle');
const errEl = document.getElementById('errEl');

function setStatus(txt, isActive=false) {{
  statusTxt.textContent = txt;
  statusDot.className = 'status-dot' + (isActive ? ' active' : '');
}}

function updateTimer() {{
    callSeconds++;
    const m = String(Math.floor(callSeconds / 60)).padStart(2, '0');
    const s = String(callSeconds % 60).padStart(2, '0');
    document.getElementById('callTimer').textContent = m + ':' + s;
}}

function addMsg(role, text) {{
  if (emptyEl) emptyEl.style.display = 'none';
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }});
  const row = document.createElement('div');
  row.className = 'msg-row ' + (role === 'ia' ? 'ia' : 'usr');
  const imgUrl = (role === 'ia' ? iaAvatarUrl : usrAvatarUrl);
  const name = (role === 'ia' ? 'Urban IA' : 'Tú');
  let avatarHtml = '';
  if (imgUrl.startsWith('data:')) {{
    avatarHtml = `<img src="${{imgUrl}}">`;
  }} else {{
    avatarHtml = `<div style="display:flex;justify-content:center;align-items:center;height:100%;font-size:1.2rem;background:#EEE;">${{imgUrl}}</div>`;
  }}
  row.innerHTML = `
    <div class="msg-avatar">${{avatarHtml}}</div>
    <div class="msg-content">
      <div class="msg-meta">
        <span class="msg-name">${{name}}</span>
        <span class="msg-time">${{timeStr}}</span>
      </div>
      <div class="msg-bubble">${{text}}</div>
    </div>
  `;
  histEl.appendChild(row);
  histEl.scrollTop = histEl.scrollHeight;
}}

function animBars(energy) {{
  for (let i = 0; i < 10; i++) {{
    const bL = document.getElementById('vb_l_' + i);
    const bR = document.getElementById('vb_r_' + i);
    let h;
    if (isAiSpeaking) {{
      h = 8 + Math.abs(Math.sin((Date.now() / 150) + i * 0.5)) * 25;
    }} else if (isSpeaking) {{
      h = Math.min(35, energy * 0.6 + Math.random() * 5);
    }} else {{
      h = 4;
    }}
    if (bL) bL.style.height = h + 'px';
    if (bR) bR.style.height = h + 'px';
  }}
}}

async function playB64Audio(b64) {{
  if (!b64 || !audioCtx) return;
  stopCurrentAudio();
  try {{
    const bin = atob(b64);
    const buf = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    const decoded = await audioCtx.decodeAudioData(buf.buffer.slice(0));
    const src = audioCtx.createBufferSource();
    src.buffer = decoded;
    src.connect(audioCtx.destination);
    currentSrc = src;
    isAiSpeaking = true;
    avCircle.classList.add('speaking');
    setStatus('Urban respondiendo...', true);
    src.onended = () => {{
      isAiSpeaking = false;
      currentSrc = null;
      avCircle.classList.remove('speaking');
      if (isRunning) setStatus('Conectado', true);
    }};
    src.start(0);
  }} catch(e) {{ console.error('Playback Error:', e); }}
}}

function stopCurrentAudio() {{
  if (currentSrc) {{
    try {{ currentSrc.stop(); }} catch(e) {{}}
    currentSrc = null;
    isAiSpeaking = false;
    avCircle.classList.remove('speaking');
  }}
}}

async function stopAndSend() {{
  if (!mediaRecorder || mediaRecorder.state !== 'recording') return;
  isProcessing = true;
  setStatus('Procesando...', true);
  await new Promise(r => {{ mediaRecorder.onstop = r; mediaRecorder.stop(); }});
  const blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
  audioChunks = [];
  const speechDur = Date.now() - speechStartTs;
  if (blob.size < 800 || speechDur < MIN_SPEECH_MS) {{
    isProcessing = false;
    if (isRunning) setStatus('Conectado', true);
    return;
  }}
  liveEl.style.display = 'block';
  liveEl.textContent = '⚡ Enviando audio...';
  try {{
    const fd = new FormData();
    fd.append('session_id', sessionId || '');
    fd.append('reset', 'false');
    fd.append('force_reply', 'true');
    fd.append('mime_type', 'audio/webm');
    fd.append('audio_chunk', blob, 'audio.webm');
    const resp = await fetch(API_URL + '/voz-stream', {{ method:'POST', body:fd }});
    const data = await resp.json();
    sessionId = data.session_id || sessionId;
    const ai = (data.assistant_text || '').trim();
    const b64 = data.assistant_audio_b64 || '';
    const trans = (data.transcript_live || '').trim();
    if (trans) {{
      liveEl.textContent = '🎤 ' + trans;
      liveEl.dataset.last = trans;
    }}
    if (ai) {{
      addMsg('usr', liveEl.dataset.last || '...');
      addMsg('ia', ai);
      liveEl.style.display = 'none';
      liveEl.dataset.last = '';
    }}
    if (b64) await playB64Audio(b64);
    else if (isRunning) setStatus('Conectado', true);
  }} catch(e) {{ console.error('API Error:', e); setStatus('Error de conexión', false); }}
  finally {{ isProcessing = false; isSpeaking = false; }}
}}

function startRecording() {{
  if (mediaRecorder && mediaRecorder.state === 'recording') return;
  audioChunks = [];
  mediaRecorder = new MediaRecorder(stream, {{ mimeType: 'audio/webm' }});
  mediaRecorder.ondataavailable = e => {{ if (e.data.size > 0) audioChunks.push(e.data); }};
  mediaRecorder.start(100);
}}

function startVADLoop() {{
  const freqData = new Uint8Array(analyser.frequencyBinCount);
  vadTimer = setInterval(() => {{
    if (!isRunning) return;
    analyser.getByteFrequencyData(freqData);
    let energy = 0;
    for(let i=0; i<freqData.length; i++) energy += freqData[i];
    energy /= freqData.length;
    animBars(energy);
    if (isProcessing) return;
    if (energy > SPEECH_THR) {{
      if (isAiSpeaking) stopCurrentAudio();
      if (!isSpeaking) {{
        isSpeaking = true;
        speechStartTs = Date.now();
        startRecording();
        setStatus('Escuchando...', true);
      }}
      clearTimeout(silenceTimer);
      silenceTimer = setTimeout(() => {{
        if (isSpeaking && !isProcessing) {{
          isSpeaking = false;
          stopAndSend();
        }}
      }}, SILENCE_MS);
    }}
  }}, CHUNK_INTERVAL);
}}

async function startCall() {{
  document.getElementById('btnStart').style.display = 'none';
  document.getElementById('btnEnd').style.display = 'flex';
  document.getElementById('mainBtnLabel').textContent = 'Finalizar';
  callSeconds = 0;
  callTimerInterval = setInterval(updateTimer, 1000);
  try {{
    stream = await navigator.mediaDevices.getUserMedia({{ audio:true }});
    audioCtx = new AudioContext();
    const src = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    src.connect(analyser);
    isRunning = true;
    setStatus('Conectando...', true);
    const fd = new FormData();
    fd.append('reset', 'true');
    fd.append('session_id', sessionId || '');
    const resp = await fetch(API_URL + '/voz-stream', {{ method:'POST', body:fd }});
    const data = await resp.json();
    sessionId = data.session_id || '';
    if (data.assistant_text) addMsg('ia', data.assistant_text);
    if (data.assistant_audio_b64) await playB64Audio(data.assistant_audio_b64);
    startVADLoop();
    if (!isAiSpeaking) setStatus('Conectado', true);
  }} catch(e) {{
    errEl.style.display = 'block';
    errEl.textContent = 'Permite el micrófono para hablar.';
    endCall();
  }}
}}

function endCall() {{
  isRunning = false;
  clearInterval(vadTimer);
  clearInterval(callTimerInterval);
  stopCurrentAudio();
  if (stream) stream.getTracks().forEach(t => t.stop());
  setStatus('Desconectado', false);
  document.getElementById('btnEnd').style.display = 'none';
  document.getElementById('btnStart').style.display = 'flex';
  document.getElementById('mainBtnLabel').textContent = 'Iniciar';
  
  // Reiniciar panel de conversación
  if (histEl) {{
    histEl.innerHTML = ''; 
    if (emptyEl) {{
      emptyEl.style.display = 'flex';
      histEl.appendChild(emptyEl);
    }}
  }}
  if (liveEl) {{
    liveEl.style.display = 'none';
    liveEl.textContent = '';
    liveEl.dataset.last = '';
  }}
}}
</script>
</body>
</html>
"""
    return html_content
