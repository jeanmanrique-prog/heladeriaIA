import streamlit as st
import base64
from pathlib import Path

def _is_dark_color(value: str) -> bool:
    color = (value or "").strip().lower()
    if color in {"", "#fff", "#ffffff", "white"}:
        return False

    if color.startswith("#"):
        hex_color = color[1:]
        if len(hex_color) == 3:
            hex_color = "".join(ch * 2 for ch in hex_color)
        if len(hex_color) == 6:
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return luminance < 0.62
            except ValueError:
                pass

    if color.startswith("rgb(") and color.endswith(")"):
        try:
            vals = [part.strip() for part in color[4:-1].split(",")]
            if len(vals) >= 3:
                r = int(float(vals[0]))
                g = int(float(vals[1]))
                b = int(float(vals[2]))
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return luminance < 0.62
        except ValueError:
            pass

    return color not in {"#fff", "#ffffff", "white"}

def get_ai_call_html(
    api_url, 
    saved_sid, 
    is_fresh, 
    avatar_src, 
    urban_src, 
    accent_color="#ff1493", 
    bg_color="#ffffff", 
    text_color="#1a1a1a",
    card_bg="#ffffff",
    border_color="#ff1493"
):
    # Determine if we should use dark or light styles for elements like history and live transcript
    is_dark = _is_dark_color(bg_color)
    hist_bg = "#1a0d1a" if is_dark else "#ffffff"
    live_bg = "#2a1a2a" if is_dark else "#ffffff"
    hist_text = "#f5e6ea" if is_dark else "#333333"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family:'Segoe UI',Tahoma,sans-serif;
    background:{bg_color};
    color:{text_color};
    padding: 0;
    margin: 0;
    user-select:none;
    overflow: hidden;
    display: flex;
    justify-content: center;
    background-color: transparent;
  }}
  .app-layout {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100vw;
    height: 100vh;
    background-color: {bg_color};
    margin: 0;
    padding: 0;
  }}
  /* Contenedor principal con scroll interno */
  .main-container {{
    width: 500px;
    height: 85vh;
    margin-left: 10%;
    overflow-y: auto;
    padding: 30px;
    background: {card_bg};
    border-radius: 30px;
    border: 3px solid {border_color};
    box-shadow: 0 0 30px rgba(255, 20, 147, 0.4); 
    scrollbar-width: thin;
    scrollbar-color: rgba(42, 26, 26, 0.3) transparent;
  }}
  /* Contenedor de imagen pegado al borde derecho */
  .image-container {{
    width: 35%;
    max-width: 600px;
    height: 100vh;
    background: {bg_color};
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    border-radius: 0;
    box-shadow: none;
    border: none;
  }}
  .image-container img {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
  }}
  .main-container::-webkit-scrollbar {{
    width: 8px;
  }}
  .main-container::-webkit-scrollbar-track {{
    background: transparent;
  }}
  .main-container::-webkit-scrollbar-thumb {{
    background-color: rgba(42, 26, 26, 0.3);
    border-radius: 10px;
  }}
  /* ── Avatar ── */
  .av-wrap {{ display:flex; justify-content:center; margin-bottom:10px; }}
  .av-circle {{
    width:100px; height:100px; border-radius:50%;
    border:3px solid {accent_color}; overflow:hidden; background:#fff;
    display:flex; justify-content:center; align-items:center;
    font-size:2.8rem; position:relative;
    box-shadow:0 6px 18px rgba(168,18,74,0.18);
    transition:box-shadow 0.3s;
  }}
  .av-circle img {{ width:100%; height:100%; object-fit:cover; }}
  .av-circle.ai-speaking {{
    box-shadow:0 0 0 6px rgba(168,18,74,0.25), 0 6px 18px rgba(168,18,74,0.18);
    animation:av-pulse 1s infinite;
  }}
  @keyframes av-pulse {{
    0%,100% {{ box-shadow:0 0 0 4px rgba(168,18,74,0.2); }}
    50%      {{ box-shadow:0 0 0 12px rgba(168,18,74,0.08); }}
  }}
  /* ── Título / Status ── */
  .call-header-pill {{
      background-color: #e91e63;
      color: #ffffff;
      padding: 8px 25px;
      border-radius: 50px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-weight: 800;
      font-size: 1rem;
      margin-bottom: 25px;
      box-shadow: 0 4px 10px rgba(233, 30, 99, 0.3);
  }}

  .call-title {{ color: #e91e63; font-size: 2.2rem; font-weight: 900; margin-bottom: 5px; text-align: center; }}
  .call-subtitle {{ color: #e91e63; font-size: 1.1rem; font-weight: bold; margin-bottom: 30px; text-align: center; }}
  
  .status-pill {{
      background-color: #ffffff;
      border: 1px solid #f8bbd0;
      border-radius: 50px;
      padding: 5px 15px;
      color: #2ecc71; /* Green color for 'escuchando' */
      font-size: 0.9rem;
      font-weight: bold;
      display: inline-block;
      margin-top: 15px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  }}

  .timer {{
      font-size: 1.8rem;
      font-weight: 900;
      color: #333;
      margin-top: 25px;
      text-align: center;
  }}

  /* ── Barras VAD ── */
  .viz {{ display:flex; justify-content:center; gap:5px; height:36px;
          align-items:center; margin-bottom:10px; margin-top: 20px; }}
  .vb  {{ width:6px; border-radius:3px; background:#e91e63; height:6px;
          transition:height 0.07s ease; }}

  /* ── Live transcript & Historial (Hidden to match mockup) ── */
  .live {{ display: none; }}
  .hist {{ display: none; }}

  /* ── Botones Circulares ── */
  .circle-btn-container {{
      display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 50px;
  }}
  .circle-btn {{
      width: 70px; height: 70px; border-radius: 50%;
      background-color: #ffffff; border: 1px solid #f0f0f0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; color: #333; font-size: 1.5rem;
      transition: all 0.2s;
  }}
  .circle-btn:hover {{ transform: scale(1.05); }}
  .circle-btn.start-call {{
      width: 90px; height: 90px; background-color: #e91e63; color: white; border: none; font-size: 2.2rem;
  }}
  .circle-btn.end-call {{
      width: 90px; height: 90px; background-color: #e91e63; color: white; border: none; font-size: 2.2rem;
  }}
  .circle-btn-label {{
      text-align: center; font-size: 0.85rem; color: #333; margin-top: 12px; font-weight: bold;
  }}

  /* ── Error permiso ── */
  .err {{ background:#ffeaea; border:1px solid #cc2222; border-radius:8px;
          padding:8px; font-size:0.78rem; color:#990000; text-align:center;
          margin-top:8px; display:none; }}
  /* ── Indicador micrófono ── */
  .mic-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%;
               background:#aaa; margin-right:6px; vertical-align:middle; }}
  .mic-dot.on  {{ background:#2ecc71; animation:dot-blink 1s infinite; }}
  .mic-dot.off {{ background:#e05070; }}
  .mic-dot.proc{{ background:#f0a020; animation:dot-blink 0.4s infinite; }}
  @keyframes dot-blink {{ 0%,100%{{opacity:1;}} 50%{{opacity:0.25;}} }}
</style>
</head>
<body>
<div class="app-layout">
<div class="main-container">

<div style="text-align:center;">
    <div class="call-header-pill">
        📞 LLAMADA EN CURSO
    </div>
</div>

<div class="call-title">Hablando con IA</div>
<div class="call-subtitle">Dulzura Callejera</div>

<div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
    <div class="viz" id="vizEl_left">
      {"".join(f'<div class="vb" id="vb_l_{i}"></div>' for i in range(5))}
    </div>

    <div class="av-wrap">
      <div class="av-circle" id="avCircle">
        {"<img src='" + avatar_src + "'>" if avatar_src.startswith("data:") else "🍦"}
      </div>
    </div>

    <div class="viz" id="vizEl_right">
      {"".join(f'<div class="vb" id="vb_r_{i}"></div>' for i in range(5))}
    </div>
</div>

<div class="timer" id="callTimer">00:00</div>

<div style="text-align:center;">
    <div class="status-pill" id="statusEl">
      <span class="mic-dot" id="micDot"></span><span id="statusTxt" style="color: #2ecc71;">IA escuchando...</span>
    </div>
</div>

<div class="live" id="liveEl"></div>
<div class="hist" id="histEl"></div>

<div class="circle-btn-container">
    <div>
        <button class="circle-btn">🔇</button>
        <div class="circle-btn-label">Silenciar</div>
    </div>
    <div>
        <button class="circle-btn start-call" id="btnStart" onclick="startCall()">📞</button>
        <button class="circle-btn end-call" id="btnEnd" onclick="endCall()" style="display:none;">📞</button>
        <div class="circle-btn-label" id="mainBtnLabel">Iniciar llamada</div>
    </div>
    <div>
        <button class="circle-btn">🔊</button>
        <div class="circle-btn-label">Altavoz</div>
    </div>
</div>
<div class="err" id="errEl"></div>

</div> <!-- end main-container -->

{f'<div class="image-container"><img src="{urban_src}"></div>' if urban_src else ''}

</div> <!-- end app-layout -->

<script>
// ═══════════════════════════════════════════════════
// CONFIGURACIÓN (espejo de voz_continua_pi.py)
// ═══════════════════════════════════════════════════
const API_URL        = "{api_url}";
const SILENCE_MS     = 700;    // ms de silencio para enviar (0.7s)
const SPEECH_THR     = 55;     // ALTO: umbral de energía para voz (ignorar voces lejanas)
const SILENCE_THR    = 30;     // ALTO: umbral de silencio
const MIN_SPEECH_MS  = 300;    // mínimo de habla para procesar
const CHUNK_INTERVAL = 80;     // ms del tick de VAD

// ═══════════════════════════════════════════════════
// ESTADO
// ═══════════════════════════════════════════════════
let sessionId       = "{saved_sid}";
let stream          = null;
let audioCtx        = null;
let analyser        = null;
let mediaRecorder   = null;
let audioChunks     = [];
let isRunning       = false;
let isSpeaking      = false;    // usuario hablando
let isProcessing    = false;    // esperando respuesta API
let isAiSpeaking    = false;    // IA reproduciendo audio
let silenceTimer    = null;
let speechStartTs   = 0;        // timestamp inicio de habla
let currentSrc      = null;     // AudioBufferSourceNode actual (para interrumpir)
let vadTimer        = null;
let freshStart      = {"true" if is_fresh else "false"};  // ¿llamada nueva?

let callTimerInterval = null;
let callSeconds       = 0;

function updateTimer() {{
    callSeconds++;
    const m = String(Math.floor(callSeconds / 60)).padStart(2, '0');
    const s = String(callSeconds % 60).padStart(2, '0');
    document.getElementById('callTimer').textContent = m + ':' + s;
}}

// ═══════════════════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════════════════
const avCircle = document.getElementById('avCircle');
const statusEl = document.getElementById('statusTxt');
const micDot   = document.getElementById('micDot');
const liveEl   = document.getElementById('liveEl');
const histEl   = document.getElementById('histEl');
const errEl    = document.getElementById('errEl');

function setStatus(txt, dotClass='') {{
  statusEl.textContent = txt;
  micDot.className = 'mic-dot ' + dotClass;
}}

function addMsg(role, text) {{
  const d = document.createElement('div');
  d.className = 'msg ' + (role === 'ia' ? 'ia' : 'usr');
  d.innerHTML = (role === 'ia' ? '<b>🍦 Urban:</b> ' : '<b>👟 Tú:</b> ') + text;
  histEl.appendChild(d);
  histEl.scrollTop = histEl.scrollHeight;
}}

function clearHistory() {{
  histEl.innerHTML = '';
}}

function animBars(energy) {{
  for (let i = 0; i < 5; i++) {{
    const bL = document.getElementById('vb_l_' + i);
    const bR = document.getElementById('vb_r_' + i);
    let h;
    if (isAiSpeaking) {{
      h = 8 + Math.abs(Math.sin((Date.now() / 200) + i * 0.7)) * 24;
    }} else if (isSpeaking) {{
      h = Math.min(32, energy * 0.6 + Math.random() * 4);
    }} else {{
      h = 6;
    }}
    if (bL) bL.style.height = h + 'px';
    if (bR) bR.style.height = h + 'px';
  }}
}}

function resetBars() {{
  for (let i = 0; i < 5; i++) {{
    const bL = document.getElementById('vb_l_' + i);
    const bR = document.getElementById('vb_r_' + i);
    if (bL) bL.style.height = '6px';
    if (bR) bR.style.height = '6px';
  }}
}}

// ═══════════════════════════════════════════════════
// AUDIO PLAYBACK (AudioContext)
// ═══════════════════════════════════════════════════
async function playB64Audio(b64) {{
  if (!b64 || !audioCtx) return;

  // Detener audio anterior (barge-in)
  stopCurrentAudio();

  try {{
    const bin  = atob(b64);
    const buf  = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    const decoded = await audioCtx.decodeAudioData(buf.buffer.slice(0));

    const src = audioCtx.createBufferSource();
    src.buffer = decoded;
    src.connect(audioCtx.destination);
    currentSrc  = src;
    isAiSpeaking = true;
    avCircle.classList.add('ai-speaking');
    setStatus('🤖 IA hablando...', 'proc');

    src.onended = () => {{
      isAiSpeaking = false;
      currentSrc   = null;
      avCircle.classList.remove('ai-speaking');
      if (isRunning) setStatus('🎤 Escuchando...', 'on');
    }};
    src.start(0);
  }} catch(e) {{
    console.error('[Audio] Error reproduciendo:', e);
    isAiSpeaking = false;
    avCircle.classList.remove('ai-speaking');
    if (isRunning) setStatus('🎤 Escuchando...', 'on');
  }}
}}

function stopCurrentAudio() {{
  if (currentSrc) {{
    try {{ currentSrc.stop(); }} catch(e) {{}}
    currentSrc   = null;
    isAiSpeaking = false;
    avCircle.classList.remove('ai-speaking');
  }}
}}

// ═══════════════════════════════════════════════════
// GRABACIÓN + ENVÍO A LA API
// ═══════════════════════════════════════════════════
function startRecording() {{
  if (mediaRecorder && mediaRecorder.state === 'recording') return;
  audioChunks = [];
  const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
               ? 'audio/webm;codecs=opus' : 'audio/webm';
  mediaRecorder = new MediaRecorder(stream, {{ mimeType: mime }});
  mediaRecorder.ondataavailable = e => {{ if (e.data.size > 0) audioChunks.push(e.data); }};
  mediaRecorder.start(100);
}}

async function stopAndSend() {{
  if (!mediaRecorder || mediaRecorder.state !== 'recording') return;
  isProcessing = true;
  setStatus('⚡ Procesando...', 'proc');

  await new Promise(resolve => {{
    mediaRecorder.onstop = resolve;
    mediaRecorder.stop();
  }});

  const blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
  audioChunks = [];

  // Ignorar clips demasiado cortos (ruido ambiente)
  const speechDur = Date.now() - speechStartTs;
  if (blob.size < 800 || speechDur < MIN_SPEECH_MS) {{
    console.log('[VAD] Descartado: muy corto (' + speechDur + 'ms)');
    isProcessing = false;
    if (isRunning) setStatus('🎤 Escuchando...', 'on');
    return;
  }}

  liveEl.textContent = '⚡ Enviando a la IA...';

  try {{
    const fd = new FormData();
    fd.append('session_id',  sessionId || '');
    fd.append('reset',       'false');
    fd.append('force_reply', 'true');
    fd.append('mime_type',   'audio/webm');
    fd.append('audio_chunk', blob, 'audio.webm');

    const resp = await fetch(API_URL + '/voz-stream', {{ method:'POST', body:fd }});
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();

    sessionId = data.session_id || sessionId;
    const tx  = (data.transcript_chunk || '').trim();
    const ai  = (data.assistant_text   || '').trim();
    const b64 = data.assistant_audio_b64 || '';

    liveEl.textContent = tx ? '✅ ' + tx : '';
    if (tx) addMsg('usr', tx);
    if (ai) addMsg('ia',  ai);
    if (b64) {{
      await playB64Audio(b64);  // autoplay inmediato
    }} else if (isRunning) {{
      setStatus('🎤 Escuchando...', 'on');
    }}
  }} catch(e) {{
    console.error('[API] Error:', e);
    setStatus('⚠️ Error de conexión', 'off');
    setTimeout(() => {{ if(isRunning) setStatus('🎤 Escuchando...', 'on'); }}, 2000);
    liveEl.textContent = '';
  }} finally {{
    isProcessing = false;
    isSpeaking   = false;
  }}
}}

// ═══════════════════════════════════════════════════
// VAD LOOP — El corazón del sistema (como voz_continua_pi.py)
// ═══════════════════════════════════════════════════
function startVADLoop() {{
  if (vadTimer) clearInterval(vadTimer);
  const freqData = new Uint8Array(analyser.frequencyBinCount);

  vadTimer = setInterval(() => {{
    if (!isRunning || !analyser) return;
    analyser.getByteFrequencyData(freqData);

    // Energía: media de las frecuencias
    let energy = 0;
    for (let i = 0; i < freqData.length; i++) energy += freqData[i];
    energy = energy / freqData.length;

    // Actualizar barras
    animBars(energy);

    if (isProcessing) return;  // esperando respuesta, no hacer nada

    if (energy > SPEECH_THR) {{
      // ──── VOZ DETECTADA ────
      if (isAiSpeaking) {{
        // BARGE-IN: usuario interrumpe a la IA
        console.log('[VAD] Barge-in detectado');
        stopCurrentAudio();
      }}
      if (!isSpeaking) {{
        isSpeaking   = true;
        speechStartTs = Date.now();
        startRecording();
        setStatus('🎤 Escuchando...', 'on');
        liveEl.textContent = '🎤 Hablando...';
      }}
      // Resetear el timer de silencio
      clearTimeout(silenceTimer);
      silenceTimer = setTimeout(() => {{
        if (isSpeaking && !isProcessing) {{
          isSpeaking = false;
          stopAndSend();
        }}
      }}, SILENCE_MS);

    }} else if (energy < SILENCE_THR && !isSpeaking) {{
      // Silencio de fondo: barras quietas
      resetBars();
    }}
  }}, CHUNK_INTERVAL);
}}

// ═══════════════════════════════════════════════════
// SALUDO INICIAL DESDE LA API
// ═══════════════════════════════════════════════════
async function fetchGreeting(sid) {{
  try {{
    const fd = new FormData();
    fd.append('reset',       'true');
    fd.append('force_reply', 'false');
    fd.append('session_id',  sid || '');
    const resp = await fetch(API_URL + '/voz-stream', {{ method:'POST', body:fd }});
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    sessionId = data.session_id || '';
    clearHistory();
    const txt = (data.assistant_text || '').trim();
    const b64 = data.assistant_audio_b64 || '';
    if (txt) addMsg('ia', txt);
    if (b64) await playB64Audio(b64);
    else setStatus('🎤 Escuchando...', 'on');
  }} catch(e) {{
    console.warn('[Greeting] Fallback local:', e);
    clearHistory();
    addMsg('ia', '¡Hola! Bienvenido a Gelatería Urbana, los mejores helados de Colombia. ¿Qué te preparo hoy?');
    setStatus('🎤 Escuchando...', 'on');
  }}
}}

// ═══════════════════════════════════════════════════
// CONTROL PRINCIPAL
// ═══════════════════════════════════════════════════
async function startCall() {{
  document.getElementById('btnStart').style.display = 'none';
  document.getElementById('btnEnd').style.display   = 'flex';
  const newBtn = document.getElementById('btnNew');
  if (newBtn) newBtn.style.display = 'none';
  const mainLbl = document.getElementById('mainBtnLabel');
  if (mainLbl) mainLbl.textContent = 'Finalizar llamada';
  
  callSeconds = 0;
  document.getElementById('callTimer').textContent = '00:00';
  if (callTimerInterval) clearInterval(callTimerInterval);
  callTimerInterval = setInterval(updateTimer, 1000);

  try {{
    stream   = await navigator.mediaDevices.getUserMedia({{ audio:true, video:false }});
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    const src = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.6;
    src.connect(analyser);

    isRunning = true;
    setStatus('🌐 Conectando con la IA...', 'proc');

    await fetchGreeting(sessionId);
    startVADLoop();  // 🔁 Loop continuo arranca aquí
    setStatus('🎤 Escuchando...', 'on');

  }} catch(e) {{
    console.error('[Mic] Error:', e);
    errEl.style.display = 'block';
    errEl.textContent   = '❌ Sin acceso al micrófono. Permite el micrófono en el navegador y vuelve a intentarlo.';
    setStatus('❌ Sin micrófono', 'off');
    document.getElementById('btnStart').style.display = 'flex';
    document.getElementById('btnEnd').style.display   = 'none';
    document.getElementById('btnNew').style.display   = 'none';
  }}
}}

function endCall() {{
  isRunning = false;
  clearInterval(vadTimer);
  clearTimeout(silenceTimer);
  if (callTimerInterval) clearInterval(callTimerInterval);
  
  stopCurrentAudio();
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
    try {{ mediaRecorder.stop(); }} catch(e) {{}}
  }}
  if (stream) stream.getTracks().forEach(t => t.stop());
  if (audioCtx) audioCtx.close();
  resetBars();
  setStatus('📵 Llamada finalizada', 'off');
  liveEl.textContent = 'Llamada finalizada.';
  
  document.getElementById('btnEnd').style.display = 'none';
  const newBtn = document.getElementById('btnNew');
  if (newBtn) newBtn.style.display = 'none';
  document.getElementById('btnStart').style.display = 'flex';
  const mainLbl = document.getElementById('mainBtnLabel');
  if (mainLbl) mainLbl.textContent = 'Iniciar Llamada';
  
  isRunning = false;
}}

function newCall() {{
  // Reset sin reiniciar el micrófono (ya está abierto)
  stopCurrentAudio();
  clearTimeout(silenceTimer);
  isSpeaking   = false;
  isProcessing = false;
  sessionId    = '';
  liveEl.textContent = '';
  setStatus('🔄 Reiniciando...', 'proc');
  fetchGreeting('').then(() => {{
    if (isRunning) setStatus('🎤 Escuchando...', 'on');
  }});
}}

// Auto-iniciar si ya hay sesión previa (el usuario volvió al modal)
window.addEventListener('load', () => {{
  if ({'true' if not is_fresh else 'false'} && sessionId) {{
    // Sesión existente: solo recuperar el micrófono
    startCall();
  }}
}});
</script>
</body>
</html>
"""
    return html_content
