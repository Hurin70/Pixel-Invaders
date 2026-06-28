"""
inject_loader.py
Inyecta la pantalla de carga arcade en el index.html generado por pygbag.
Ejecutar después de: pygbag --build .
"""
import re

INDEX_PATH = "build/web/index.html"

# ── CSS de la pantalla de carga ──────────────────────────────────────────────
LOADER_CSS = """
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; background: #000814; font-family: 'Share Tech Mono', monospace; overflow: hidden; }

        /* ── PYGBAG REQUIRED ── */
        #status { display: none; }
        #progress { display: none; }
        #infobox { position: fixed; background: transparent; color: transparent; font-size: 0; z-index: 999999; pointer-events: none; }
        div.emscripten { text-align: center; }
        div.emscripten_border { border: 1px solid #0ff2; }
        div.thick_border { border: 4px solid #0ff4; }
        canvas.emscripten { border: 0px none; background-color: transparent; width: 100%; height: 100%; z-index: 5; padding: 0; margin: 0 auto; position: absolute; top: 0; bottom: 0; left: 0; right: 0; }
        .topright { position:absolute; top:0; right:0; }
        .bottomright { position:absolute; top:40%; right:0; }
        .center { display:flex; align-items:center; justify-content:center; }
        .trinfo { position:relative; right:0; border:1px solid #0ff3; }
        .framed { position:relative; top:150px; right:10px; border:1px solid #0ff3; }

        /* ── ARCADE LOADER ── */
        #arcade-loader { position: fixed; inset: 0; z-index: 9000; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #000814; overflow: hidden; }
        #arcade-loader::before { content: ''; position: absolute; inset: 0; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.18) 2px, rgba(0,0,0,0.18) 4px); pointer-events: none; z-index: 1; }
        #stars { position: absolute; inset: 0; overflow: hidden; }
        .star { position: absolute; background: #fff; border-radius: 50%; animation: twinkle var(--d) ease-in-out infinite alternate; opacity: var(--o); }
        @keyframes twinkle { from { opacity: var(--o); transform: scale(1); } to { opacity: calc(var(--o) * 0.2); transform: scale(0.5); } }
        #grid-floor { position: absolute; bottom: 0; left: 0; right: 0; height: 45%; background: linear-gradient(to bottom, transparent 0%, rgba(0,240,255,0.04) 100%); perspective: 300px; overflow: hidden; }
        #grid-floor::before { content: ''; position: absolute; inset: 0; background-image: linear-gradient(rgba(0,240,255,0.25) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.25) 1px, transparent 1px); background-size: 60px 60px; transform: rotateX(55deg) scaleY(3) translateY(-40%); animation: gridScroll 3s linear infinite; }
        @keyframes gridScroll { from { background-position: 0 0; } to { background-position: 0 60px; } }
        #retro-sun { position: absolute; bottom: 42%; left: 50%; transform: translateX(-50%); width: 180px; height: 90px; border-radius: 90px 90px 0 0; background: linear-gradient(180deg, #ff6b35 0%, #ff0080 60%, #8b00ff 100%); box-shadow: 0 0 60px rgba(255,0,128,0.6), 0 0 120px rgba(139,0,255,0.3); overflow: hidden; }
        #retro-sun::after { content: ''; position: absolute; inset: 0; background: repeating-linear-gradient(180deg, transparent 0px, transparent 6px, rgba(0,0,0,0.55) 6px, rgba(0,0,0,0.55) 10px); }
        #loader-content { position: relative; z-index: 2; text-align: center; margin-bottom: 20px; }
        #loader-title { font-family: 'Orbitron', sans-serif; font-size: clamp(13px, 2.8vw, 22px); font-weight: 700; letter-spacing: 0.25em; color: #ff0080; text-transform: uppercase; text-shadow: 0 0 10px #ff0080, 0 0 30px #ff008088; margin-bottom: 6px; animation: titlePulse 2s ease-in-out infinite alternate; }
        @keyframes titlePulse { from { text-shadow: 0 0 10px #ff0080, 0 0 30px #ff008088; } to { text-shadow: 0 0 20px #ff0080, 0 0 60px #ff0080bb; } }
        #loader-subtitle { font-family: 'Orbitron', sans-serif; font-size: clamp(18px, 4.5vw, 38px); font-weight: 900; letter-spacing: 0.18em; color: #00f0ff; text-transform: uppercase; text-shadow: 0 0 12px #00f0ff, 0 0 40px #00f0ff88; margin-bottom: 40px; animation: subtitlePulse 1.8s ease-in-out infinite alternate; }
        @keyframes subtitlePulse { from { text-shadow: 0 0 12px #00f0ff, 0 0 40px #00f0ff88; } to { text-shadow: 0 0 24px #00f0ff, 0 0 80px #00f0ffbb; } }
        #progress-wrap { width: clamp(260px, 55vw, 500px); margin: 0 auto 16px auto; }
        #progress-label { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; font-family: 'Share Tech Mono', monospace; font-size: clamp(10px, 1.5vw, 13px); color: #ff0080cc; letter-spacing: 0.12em; text-transform: uppercase; }
        #progress-bar-outer { width: 100%; height: 18px; border: 1px solid #00f0ff55; background: #000814; position: relative; box-shadow: 0 0 10px #00f0ff22, inset 0 0 8px #00001a; }
        #progress-bar-outer::before { content: ''; position: absolute; inset: 0; background: repeating-linear-gradient(90deg, transparent, transparent 18px, rgba(0,240,255,0.07) 18px, rgba(0,240,255,0.07) 19px); }
        #progress-bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #8b00ff, #ff0080, #00f0ff); box-shadow: 0 0 14px #ff0080, 0 0 28px #00f0ff88; transition: width 0.15s ease-out; position: relative; }
        #progress-bar-fill::after { content: ''; position: absolute; right: 0; top: 0; bottom: 0; width: 4px; background: #fff; box-shadow: 0 0 8px #fff, 0 0 16px #00f0ff; animation: scanHead 0.08s steps(1) infinite; }
        @keyframes scanHead { 0%{opacity:1} 50%{opacity:0.4} }
        #progress-pct { margin-top: 12px; font-family: 'Orbitron', sans-serif; font-size: clamp(26px, 5vw, 44px); font-weight: 900; color: #fff; letter-spacing: 0.08em; text-shadow: 0 0 20px #00f0ff, 0 0 40px #00f0ff88; }
        #progress-msg { margin-top: 8px; font-family: 'Share Tech Mono', monospace; font-size: clamp(9px, 1.4vw, 12px); color: #00f0ffaa; letter-spacing: 0.2em; text-transform: uppercase; min-height: 1.4em; }
        #blink-cursor { display:inline-block; animation: blink 0.7s steps(1) infinite; color:#ff0080; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        .corner { position:absolute; width:20px; height:20px; z-index:3; }
        .corner-tl { top:16px; left:16px; border-top:2px solid #ff0080; border-left:2px solid #ff0080; }
        .corner-tr { top:16px; right:16px; border-top:2px solid #ff0080; border-right:2px solid #ff0080; }
        .corner-bl { bottom:16px; left:16px; border-bottom:2px solid #ff0080; border-left:2px solid #ff0080; }
        .corner-br { bottom:16px; right:16px; border-bottom:2px solid #ff0080; border-right:2px solid #ff0080; }
        #click-to-start { display: none; position: fixed; inset: 0; z-index: 8999; align-items: center; justify-content: center; background: rgba(0,8,20,0.85); flex-direction: column; gap: 20px; }
        #click-to-start.visible { display: flex; }
        #click-to-start p { font-family: 'Orbitron', sans-serif; font-size: clamp(18px, 4vw, 32px); font-weight: 900; color: #00f0ff; letter-spacing: 0.2em; text-transform: uppercase; text-shadow: 0 0 20px #00f0ff; animation: subtitlePulse 1s ease-in-out infinite alternate; }
    </style>
"""

# ── HTML del loader (se inserta justo antes de </body>) ──────────────────────
LOADER_HTML = """
    <!-- ── ARCADE LOADER ── -->
    <div id="arcade-loader">
        <div id="stars"></div>
        <div id="grid-floor"></div>
        <div id="retro-sun"></div>
        <div class="corner corner-tl"></div>
        <div class="corner corner-tr"></div>
        <div class="corner corner-bl"></div>
        <div class="corner corner-br"></div>
        <div id="loader-content">
            <div id="loader-title">— Sistema de arranque —</div>
            <div id="loader-subtitle">Tu nave se está<br>ensamblando</div>
            <div id="progress-wrap">
                <div id="progress-label">
                    <span>CARGANDO MÓDULOS</span>
                    <span id="progress-part-label">PARTE 1 / 4</span>
                </div>
                <div id="progress-bar-outer">
                    <div id="progress-bar-fill"></div>
                </div>
            </div>
            <div id="progress-pct">0%</div>
            <div id="progress-msg">INICIALIZANDO SISTEMAS<span id="blink-cursor">_</span></div>
        </div>
    </div>
    <div id="click-to-start">
        <p>— CLICK PARA INICIAR —</p>
    </div>
"""

# ── JS del loader ─────────────────────────────────────────────────────────────
LOADER_JS = """
    <script>
    // ── STAR FIELD ──
    (function() {
        const container = document.getElementById('stars');
        if (!container) return;
        for (let i = 0; i < 120; i++) {
            const s = document.createElement('div');
            s.className = 'star';
            const size = Math.random() * 2.5 + 0.5;
            const o = (Math.random() * 0.5 + 0.2).toFixed(2);
            const d = (Math.random() * 3 + 1.5).toFixed(1) + 's';
            s.style.cssText = `width:${size}px;height:${size}px;left:${Math.random()*100}%;top:${Math.random()*60}%;--o:${o};--d:${d};animation-delay:${(Math.random()*3).toFixed(1)}s;`;
            container.appendChild(s);
        }
    })();

    const PART_MSGS = [
        'CARGANDO NÚCLEO DE PROPULSIÓN',
        'ENSAMBLANDO ESCUDOS DEFLECTORES',
        'CALIBRANDO SISTEMAS DE ARMAS',
        'ACTIVANDO INTELIGENCIA DE VUELO',
        'NAVE LISTA PARA EL DESPEGUE'
    ];
    let loaderDone = false;

    setInterval(() => {
        const progressEl = document.getElementById('progress');
        if (!progressEl) return;
        let value = parseFloat(progressEl.value) || 0;
        let max   = parseFloat(progressEl.max)   || 100;
        let partPercentage = Math.min((value / max) * 100, 100);
        let currentPart = window.currentLoadingPart || 1;
        let globalPct = 0;
        if (currentPart >= 1 && currentPart <= 4) {
            globalPct = Math.round(((currentPart - 1) * 25) + (partPercentage * 0.25));
        } else {
            globalPct = 100;
        }
        globalPct = Math.min(globalPct, 100);
        const fill = document.getElementById('progress-bar-fill');
        const pct  = document.getElementById('progress-pct');
        const msg  = document.getElementById('progress-msg');
        const part = document.getElementById('progress-part-label');
        if (fill) fill.style.width = globalPct + '%';
        if (pct)  pct.textContent = globalPct + '%';
        if (part && currentPart <= 4) part.textContent = `PARTE ${currentPart} / 4`;
        if (msg) {
            const idx = Math.min((currentPart || 1) - 1, PART_MSGS.length - 1);
            msg.innerHTML = PART_MSGS[idx] + '<span id="blink-cursor">_</span>';
        }
        if (globalPct >= 100 && !loaderDone) {
            loaderDone = true;
            const loader = document.getElementById('arcade-loader');
            const clickStart = document.getElementById('click-to-start');
            if (loader) {
                loader.style.transition = 'opacity 0.6s ease';
                loader.style.opacity = '0';
                setTimeout(() => {
                    loader.style.display = 'none';
                    if (clickStart) clickStart.classList.add('visible');
                }, 650);
            }
        }
    }, 50);

    document.addEventListener('click', function hideStart() {
        const el = document.getElementById('click-to-start');
        if (el) el.style.display = 'none';
        document.removeEventListener('click', hideStart);
    });
    document.addEventListener('keydown', function hideStartKey() {
        const el = document.getElementById('click-to-start');
        if (el) el.style.display = 'none';
        document.removeEventListener('keydown', hideStartKey);
    });
    </script>
"""

# ── INYECCIÓN ────────────────────────────────────────────────────────────────
with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Insertar CSS justo antes de </head>
html = html.replace("</head>", LOADER_CSS + "\n</head>", 1)

# 2. Insertar HTML del loader justo antes del primer <canvas
html = html.replace('<canvas class="emscripten"', LOADER_HTML + '\n    <canvas class="emscripten"', 1)

# 3. Insertar JS del loader justo antes de </body>
html = html.replace("</body>", LOADER_JS + "\n</body>", 1)

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Pantalla de carga inyectada en {INDEX_PATH}")
