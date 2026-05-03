"""
app/ia/llamada/estilos_llamada.py
─────────────────────────────────
Estilos CSS para la interfaz de llamada inmersiva.
"""

def obtener_estilos_llamada(color_acento, color_fondo, color_texto, color_tarjeta):
    """Retorna el bloque de estilos CSS para la interfaz de llamada."""
    return f"""
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
    background-color: {color_fondo};
    color: {color_texto};
  }}
  
  .app-layout {{
    display: flex;
    width: 100vw;
    height: 100vh;
    padding: 20px;
    gap: 30px;
    background-color: {color_fondo};
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
    scrollbar-color: {color_acento}22 transparent;
  }}

  .hist::-webkit-scrollbar {{ width: 6px; }}
  .hist::-webkit-scrollbar-thumb {{ background: {color_acento}22; border-radius: 10px; }}

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
  .msg-row.ia .msg-name {{ color: {color_acento}; }}

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
    border-left: 4px solid {color_acento};
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
    background: {color_tarjeta};
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
    background: {color_acento};
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
    color: {color_acento};
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
  .v-bar {{ width: 4px; height: 4px; background: {color_acento}55; border-radius: 2px; transition: height 0.1s; }}

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
  .status-dot.active {{ background: {color_acento}; box-shadow: 0 0 10px {color_acento}AA; }}

  .controls-row {{ display: flex; align-items: center; justify-content: center; gap: 30px; }}
  .btn-sec {{
    width: 55px; height: 55px; border-radius: 50%; background: #F3F3F3; border: none;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; color: {color_acento}; transition: all 0.2s;
  }}
  .btn-sec:hover {{ background: #FFE4EC; transform: translateY(-3px); }}
  .btn-main {{
    width: 80px; height: 80px; border-radius: 50%; background: {color_acento}; border: none;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 2.1rem; color: white; box-shadow: 0 15px 40px rgba(255, 75, 125, 0.35);
  }}
  .btn-main:hover {{ transform: scale(1.05) translateY(-4px); }}
  
  .btn-label {{ font-size: 0.75rem; font-weight: 800; color: #888; text-transform: uppercase; margin-top: 10px; }}
  .control-group {{ display: flex; flex-direction: column; align-items: center; }}
  .error-box {{ margin-top: 20px; padding: 12px; background: #FFF0F0; color: #D32F2F; border-radius: 12px; font-size: 0.85rem; display: none; }}
</style>
"""
