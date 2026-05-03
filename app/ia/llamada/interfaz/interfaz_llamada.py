"""
app/ia/llamada/interfaz/interfaz_llamada.py
──────────────────────────────────────────
Interfaz de usuario para la llamada en tiempo real. 
Centraliza la generación de HTML, JS y la integración con Streamlit.
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path
from utilidades.gestor_sesion import GestorSesion
from ia.llamada.estilos.estilos_llamada import obtener_estilos_llamada

def obtener_cuerpo_llamada(avatar_src):
    """Retorna el cuerpo HTML para la interfaz de llamada."""
    barras_izq = "".join(f'<div class="v-bar" id="vb_l_{i}"></div>' for i in range(10))
    barras_der = "".join(f'<div class="v-bar" id="vb_r_{i}"></div>' for i in range(10))
    
    avatar_html = f"<img src='{avatar_src}'>" if avatar_src.startswith("data:") else "🍦"

    return f"""
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
          {barras_izq}
        </div>
        <div class="main-avatar-wrap">
          <div class="main-avatar" id="avCircle">
             {avatar_html}
          </div>
        </div>
        <div class="viz-bars" id="viz_R">
          {barras_der}
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
"""

def obtener_script_llamada(url_api, sid_guardado, es_nuevo, avatar_src, user_src):
    """Retorna el bloque de JavaScript para la lógica de la llamada."""
    return f"""
<script>
const API_URL = "{url_api}";
const SILENCE_MS = 700;
const SPEECH_THR = 40;
const SILENCE_THR = 30;
const MIN_SPEECH_MS = 300;
const CHUNK_INTERVAL = 80;

let sessionId = "{sid_guardado}";
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
let freshStart = {"true" if es_nuevo else "false"};
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

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    try {{
      const resp = await fetch(API_URL + '/voz-stream', {{ 
        method:'POST', 
        body:fd,
        signal: controller.signal
      }});
      clearTimeout(timeoutId);
      const data = await resp.json();
      sessionId = data.session_id || '';
      if (data.assistant_text) addMsg('ia', data.assistant_text);
      if (data.assistant_audio_b64) await playB64Audio(data.assistant_audio_b64);
      startVADLoop();
      if (!isAiSpeaking) setStatus('Conectado', true);
    }} catch(fe) {{
      clearTimeout(timeoutId);
      console.error('Error de conexión:', fe);
      setStatus('Error de conexión. Reintenta.', false);
      setTimeout(endCall, 2000);
    }}
  }} catch(e) {{
    console.error('Error de micrófono:', e);
    errEl.style.display = 'block';
    errEl.textContent = 'Permite el micrófono para hablar.';
    endCall();
  }}
}}

function endCall() {{
  isRunning = false;
  sessionId = '';
  clearInterval(vadTimer);
  clearInterval(callTimerInterval);
  callSeconds = 0;
  document.getElementById('callTimer').textContent = '00:00';
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
"""

def generar_interfaz_llamada(
    url_api, 
    sid_guardado, 
    es_nuevo, 
    avatar_src, 
    urban_src, 
    user_src="👤",
    color_acento="#FF4B7D", 
    color_fondo="#F7F7F7", 
    color_texto="#222222",
    color_tarjeta="#ffffff",
    color_borde="#FF4B7D"
):
    """Genera el HTML completo para la interfaz de llamada inmersiva."""
    css = obtener_estilos_llamada(color_acento, color_fondo, color_texto, color_tarjeta)
    cuerpo = obtener_cuerpo_llamada(avatar_src)
    js = obtener_script_llamada(url_api, sid_guardado, es_nuevo, avatar_src, user_src)
    
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    {css}
</head>
<body>
    {cuerpo}
    {js}
</body>
</html>
"""

def render_realtime_call(theme: dict):
    """Renderiza la interfaz de llamada con soporte completo de colores del tema."""
    GestorSesion.inicializar_modo("call")
    
    # Colores del tema
    accent = theme.get("ACCENT", "#ff1493")
    bg = theme.get("BG", "#ffffff")
    text = theme.get("TEXT", "#1a1a1a")
    card = theme.get("BG2", "#ffffff")
    border = theme.get("ACCENT", "#ff1493")

    # Cargar recursos visuales
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    images_dir = root_dir / "imagenes"
    
    def get_b64(path):
        if path.exists():
            with open(path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        return None

    avatar_src = get_b64(images_dir / "perfil_ia.png") or "🍦"
    urban_name = "urban_admin.png" if st.session_state.role == "admin" else "urban_comiendo.png"
    urban_src = get_b64(images_dir / urban_name) or get_b64(images_dir / "urban_comiendo.png") or ""
    user_src = get_b64(images_dir / "perfil_cliente.png") or "👤"

    saved_sid = st.session_state.get("_voz_session_id") or ""
    is_fresh = not st.session_state.get("call_greeted", False)
    
    if is_fresh:
        st.session_state["call_greeted"] = True
        st.session_state["_voz_session_id"] = ""
        saved_sid = ""

    # Inyectar CSS global de la página
    st.markdown("""
        <style>
            .main .block-container {
                max-width: 100vw !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                padding-top: 1rem !important;
            }
            iframe {
                border-radius: 25px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.05);
            }
        </style>
    """, unsafe_allow_html=True)

    html_code = generar_interfaz_llamada(
        url_api="http://127.0.0.1:8000",
        sid_guardado=saved_sid,
        es_nuevo=is_fresh,
        avatar_src=avatar_src,
        urban_src=urban_src,
        user_src=user_src,
        color_acento="#FF4B7D",
        color_fondo="#F7F7F7",
        color_texto="#222222",
        color_tarjeta="#FFFFFF",
        color_borde="#FF4B7D"
    )
    
    components.html(html_code, height=750, scrolling=False)
