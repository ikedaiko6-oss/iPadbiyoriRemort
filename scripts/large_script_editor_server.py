#!/usr/bin/env python3
"""
大きい文字の台本ビューア／エディタ（ローカル専用サーバー・シンちゃん版）

03_台本/ 内の .txt を、大きい文字のテレプロンプターとして
ブラウザ（127.0.0.1）に表示する。編集して保存もできる。

外部公開はしない。127.0.0.1 のみでLISTENする。
"""
import http.server
import socketserver
import urllib.parse
import pathlib
import html
import re
import webbrowser
import sys

PORT_RANGE_START = 8801
PORT_RANGE_END = 8850
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
# シンちゃん版専用フォルダ（ナギちゃん版の03_台本とは共有しない。
# 編集はここだけに書き込まれるので、互いの編集が影響し合わない）
SCRIPT_DIR = BASE_DIR / "03_台本_シンちゃん版"
PORT_FILE = pathlib.Path("/tmp/ipadbiyori_shinchan.port")

# セクション名のキーワード→色（縦帯・進捗ドットに使う）
SECTION_COLORS = [
    (("結果",), "#c9714e"),   # 結果を先に見せる：テラコッタ
    (("困りごと", "予告"), "#5b7fa6"),   # 困りごと：ブルーグレー
    (("手順",), "#7a9463"),   # 手順：グリーン
    (("応用",), "#9b7fb0"),   # 応用：パープル
    (("注意",), "#c24545"),   # 注意点：レッド
    (("コメント", "次回"), "#c9a13a"),   # コメント募集：ゴールド
]
DEFAULT_COLOR = "#9a9284"


def color_for(section_label: str) -> str:
    for keywords, color in SECTION_COLORS:
        if any(k in section_label for k in keywords):
            return color
    return DEFAULT_COLOR


PAGE_CSS = """
<style>
  :root{
    --paper:#faf6ef; --ink:#2b2620; --ink-dim:#8d8375;
    --border:#e6ddcc; --accent:#c9714e;
  }
  *{box-sizing:border-box;}
  body{margin:0;background:var(--paper);color:var(--ink);
    font-family:"Hiragino Mincho ProN","Yu Mincho",serif;}
  header{padding:20px 28px;background:var(--paper);border-bottom:2px solid var(--border);
    display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;}
  header h1{font-size:17px;margin:0;font-weight:600;letter-spacing:.02em;}
  header .mark{font-size:11px;color:var(--ink-dim);letter-spacing:.15em;}
  main{padding:32px 24px 60px;max-width:840px;margin:0 auto;}
  body.script-page main{margin-left:190px;margin-right:auto;}

  ul.filelist{list-style:none;padding:0;}
  ul.filelist li{margin-bottom:12px;}
  ul.filelist a{display:block;padding:18px 22px;background:#fff;border:1px solid var(--border);
    border-left:6px solid var(--accent);border-radius:4px;text-decoration:none;
    color:var(--ink);font-size:16px;transition:transform .12s;}
  ul.filelist a:hover{transform:translateX(4px);}

  .toolbar{display:flex;gap:10px;align-items:center;margin-bottom:20px;flex-wrap:wrap;}
  button, .btn{background:#fff;border:1px solid var(--border);padding:10px 20px;border-radius:4px;
    font-size:14px;cursor:pointer;color:var(--ink);text-decoration:none;font-family:inherit;}
  button.primary{background:var(--accent);color:#fff;border-color:transparent;}

  .toc{position:fixed;top:var(--bar-h, 64px);left:0;bottom:0;width:170px;
    display:flex;flex-direction:column;gap:8px;overflow-y:auto;
    padding:16px 12px;background:var(--paper);border-right:1px solid var(--border);z-index:15;}
  .toc a{font-size:12px;padding:7px 12px;border-radius:20px;text-decoration:none;
    color:#fff;opacity:.85;text-align:left;line-height:1.4;}

  @media (max-width:780px){
    body.script-page main{margin-left:auto;}
    .toc{position:static;width:auto;height:auto;flex-direction:row;flex-wrap:wrap;
      padding:0;border-right:none;background:transparent;margin-bottom:24px;}
  }

  .block{margin-bottom:38px;padding-bottom:38px;border-bottom:1px dashed var(--border);}
  .block:last-child{border-bottom:none;}
  .section-label{font-size:13px;color:#fff;background:var(--c);display:inline-block;
    padding:4px 14px;border-radius:20px;letter-spacing:.1em;margin-bottom:16px;}
  .time-badge{font-size:14px;font-weight:700;color:var(--ink);background:#fff;
    margin-left:10px;letter-spacing:.03em;padding:2px 10px;border-radius:12px;
    border:1px solid var(--c);}
  .total-time{font-size:15px;font-weight:700;color:var(--ink);margin-bottom:18px;}
  .block-text{font-size:var(--fs,30px);line-height:2;white-space:pre-wrap;
    letter-spacing:.02em;border-left:8px solid var(--c);padding:2% 4%;background:#fff;
    border-radius:4px;box-shadow:0 3px 14px rgba(43,38,32,.06);
    outline:none;cursor:text;}
  .block-text:focus{box-shadow:0 0 0 2px var(--c);}
  .save-flash{position:fixed;bottom:24px;right:24px;background:#3f6b3f;color:#fff;
    padding:10px 20px;border-radius:20px;font-size:13px;opacity:0;transition:opacity .3s;
    pointer-events:none;}
  .save-flash.show{opacity:1;}

  /* 撮影バー */
  .shoot-bar{position:sticky;top:0;z-index:20;background:var(--paper);
    border-bottom:2px solid var(--border);padding:12px 24px;
    display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
  .shoot-bar button{font-weight:700;}
  .shoot-bar .elapsed{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;
    color:var(--accent);min-width:64px;}
  body.paused .shoot-bar .elapsed{color:var(--ink-dim);}
  body.shooting main{cursor:pointer;}
  .shoot-bar .speed{font-size:13px;color:var(--ink-dim);display:flex;align-items:center;gap:8px;}
  .shoot-bar .speed input[type=range]{width:130px;vertical-align:middle;}
  .shoot-bar .speed #speedLabel{font-variant-numeric:tabular-nums;min-width:42px;display:inline-block;}

  .block{transition:opacity .25s;}
  body.shooting .block:not(.current){opacity:.35;}
  body.shooting .block.current .block-text{box-shadow:0 0 0 3px var(--accent);}

  body.focus-mode header,
  body.focus-mode .shoot-bar .aux,
  body.focus-mode .toc,
  body.focus-mode .total-time{display:none;}
  body.focus-mode .shoot-bar{background:rgba(250,246,239,.92);}
  body.focus-mode main{padding-top:12px;margin-left:auto;}

  @media (max-width:600px){ .slide-text{font-size:calc(var(--fs, 32px) * 0.75);} }
</style>
"""


def parse_slides(text: str):
    blocks = [b.strip() for b in text.split("---") if b.strip()]
    return blocks if blocks else [text]


def section_label(slide_text: str) -> str:
    m = re.match(r"^【(.+?)】", slide_text)
    return m.group(1) if m else ""


CHARS_PER_MINUTE = 300  # 日本語の実況・説明を想定した目安（ゆっくりめ）


def estimate_seconds(text: str) -> int:
    # 見出し【】・（画面録画：〜）のようなト書き・記号は読み上げないので除外してから数える
    body = re.sub(r"^【.+?】\n?", "", text)
    body = re.sub(r"（.*?）", "", body)
    chars = len(re.sub(r"\s", "", body))
    return max(5, round(chars / CHARS_PER_MINUTE * 60))


def format_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m}分{s:02d}秒" if m else f"{s}秒"


def list_files():
    if not SCRIPT_DIR.exists():
        return []
    return sorted(p.name for p in SCRIPT_DIR.glob("*.txt"))


def render_index():
    items = "".join(
        f'<li><a href="/view?file={urllib.parse.quote(name)}">{html.escape(name)}</a></li>'
        for name in list_files()
    )
    if not items:
        items = "<li>03_台本/ に .txt がありません</li>"
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>台本 大きい文字（シンちゃん版）</title>{PAGE_CSS}</head><body>
<header><h1>台本 大きい文字ビューア</h1><span class="mark">シンちゃん版</span></header>
<main><ul class="filelist">{items}</ul></main>
</body></html>"""


def render_view(name: str):
    """
    全スライドを1本の縦スクロールで表示する。
    iPadで操作しながら喋る用途なので、Mac側のクリック操作を発生させない。
    """
    path = SCRIPT_DIR / name
    if not path.exists():
        return "<h1>ファイルが見つかりません</h1>"
    slides = parse_slides(path.read_text(encoding="utf-8"))
    qname = urllib.parse.quote(name)

    toc = "".join(
        f'<a href="#s{i}" style="background:{color_for(section_label(s))}">'
        f'{html.escape(section_label(s)) or f"{i+1}"}</a>'
        for i, s in enumerate(slides)
    )

    durations = [estimate_seconds(s) for s in slides]
    total_seconds = sum(durations)

    blocks = "".join(
        f'<div class="block" id="s{i}" style="--c:{color_for(section_label(s))}">'
        f'<div class="section-label">{html.escape(section_label(s)) or "&nbsp;"}'
        f'<span class="time-badge">約{format_duration(durations[i])}</span></div>'
        f'<div class="block-text txt" contenteditable="true" spellcheck="false" '
        f'data-idx="{i}">{html.escape(s)}</div>'
        f'</div>'
        for i, s in enumerate(slides)
    )

    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>{html.escape(name)}</title>{PAGE_CSS}</head><body class="script-page">
<header class="aux">
  <h1>{html.escape(name)}</h1>
  <div>
    <a class="btn" href="/">一覧へ</a>
  </div>
</header>
<div class="shoot-bar">
  <button class="primary" id="shootBtn" onclick="toggleShoot()">▶ 撮影開始</button>
  <span class="elapsed" id="elapsed">0:00</span>
  <button onclick="adjust(-4)">A－</button>
  <button onclick="adjust(4)">A＋</button>
  <span class="speed aux">速度
    <input type="range" id="speedSlider" min="10" max="250" value="100" step="5"
      oninput="onSpeedInput(this.value)">
    <span id="speedLabel">100%</span>
  </span>
  <button onclick="toggleFocus()">集中モード</button>
</div>
<main>
  <div class="toc">{toc}</div>
  <div class="total-time aux">本文をタップして直接編集できます（触れなくなったら自動保存）／全体の目安時間：約{format_duration(total_seconds)}</div>
  {blocks}
</main>
<div class="save-flash" id="flash">保存しました</div>
<script>
let fs = 30;
function adjust(d){{
  fs = Math.max(18, Math.min(56, fs + d));
  document.querySelectorAll('.txt').forEach(el => el.style.setProperty('--fs', fs + 'px'));
}}

// 撮影バーの実際の高さを測って目次の開始位置に反映する（見切れ防止）
function syncBarHeight(){{
  const bar = document.querySelector('.shoot-bar');
  if (bar) document.documentElement.style.setProperty('--bar-h', bar.offsetHeight + 'px');
}}
syncBarHeight();
window.addEventListener('resize', syncBarHeight);
new ResizeObserver(syncBarHeight).observe(document.querySelector('.shoot-bar'));

const totalSeconds = {total_seconds};
const fileName = {name!r};
document.querySelectorAll('.block-text').forEach(el => {{
  let original = el.innerText;
  el.addEventListener('blur', () => {{
    const text = el.innerText;
    if (text === original) return;
    original = text;
    fetch('/save-block?file=' + encodeURIComponent(fileName) + '&idx=' + el.dataset.idx, {{
      method: 'POST',
      headers: {{'Content-Type': 'text/plain; charset=utf-8'}},
      body: text
    }}).then(() => {{
      const flash = document.getElementById('flash');
      flash.classList.add('show');
      setTimeout(() => flash.classList.remove('show'), 1200);
    }});
  }});
}});

/* ===== 撮影サポート：自動スクロール＋経過時間タイマー ===== */
let shooting = false;
let paused = false;
let elapsedSec = 0;
let timerId = null;
let scrollId = null;
let lastFrameTime = null;
let speedMultiplier = 1.0; // スライダー(10%〜250%)からそのまま算出

function updateElapsedDisplay(){{
  const m = Math.floor(elapsedSec / 60), s = elapsedSec % 60;
  document.getElementById('elapsed').textContent = m + ':' + String(s).padStart(2, '0');
}}

function setBlocksEditable(editable){{
  document.querySelectorAll('.block-text').forEach(el => {{
    el.setAttribute('contenteditable', editable ? 'true' : 'false');
  }});
}}

function toggleShoot(){{
  shooting = !shooting;
  paused = false;
  const btn = document.getElementById('shootBtn');
  document.body.classList.toggle('shooting', shooting);
  setBlocksEditable(!shooting);
  if (shooting){{
    btn.textContent = '■ 停止';
    timerId = setInterval(() => {{ if (!paused){{ elapsedSec++; updateElapsedDisplay(); }} }}, 1000);
    startAutoScroll();
  }} else {{
    btn.textContent = '▶ 撮影開始';
    clearInterval(timerId);
    cancelAnimationFrame(scrollId);
  }}
}}

function togglePause(){{
  if (!shooting) return;
  paused = !paused;
  document.body.classList.toggle('paused', paused);
  lastFrameTime = null; // 再開時にジャンプしないようリセット
}}

function startAutoScroll(){{
  // 本文の総文字数 ÷ 目安時間 から、1秒あたりに進めるべきスクロール量を概算する
  const doc = document.documentElement;
  const scrollable = doc.scrollHeight - window.innerHeight;
  const pxPerSecond = totalSeconds > 0 ? (scrollable / totalSeconds) : 0;
  let scrollAccum = 0; // 1px未満の端数はブラウザに切り捨てられるので、次のフレームに繰り越す
  function step(now){{
    if (!shooting) return;
    if (paused || lastFrameTime === null){{
      lastFrameTime = now;
      scrollId = requestAnimationFrame(step);
      return;
    }}
    const dt = (now - lastFrameTime) / 1000;
    lastFrameTime = now;
    scrollAccum += pxPerSecond * speedMultiplier * dt;
    const move = Math.floor(scrollAccum);
    if (move >= 1){{
      window.scrollBy(0, move);
      scrollAccum -= move;
    }}
    scrollId = requestAnimationFrame(step);
  }}
  scrollId = requestAnimationFrame(step);
}}

function onSpeedInput(value){{
  speedMultiplier = value / 100;
  document.getElementById('speedLabel').textContent = value + '%';
}}

function toggleFocus(){{
  document.body.classList.toggle('focus-mode');
}}

// 撮影中は、画面（本文エリア）をタップ／クリックすると一時停止・再開できる
document.addEventListener('click', (e) => {{
  if (!shooting) return;
  if (e.target.closest('.shoot-bar') || e.target.closest('header')) return;
  togglePause();
}});

/* 今どのセクションを読んでいるかを画面中央付近の要素から判定して強調する */
const blocks = Array.from(document.querySelectorAll('.block'));
function highlightCurrent(){{
  const centerY = window.innerHeight * 0.4;
  let current = blocks[0];
  for (const b of blocks){{
    const r = b.getBoundingClientRect();
    if (r.top <= centerY) current = b;
  }}
  blocks.forEach(b => b.classList.toggle('current', b === current));
}}
document.addEventListener('scroll', highlightCurrent, {{passive: true}});
highlightCurrent();
</script>
</body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def _send_html(self, body: str, status: int = 200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/":
            self._send_html(render_index())
        elif parsed.path == "/view":
            name = qs.get("file", [""])[0]
            self._send_html(render_view(name))
        else:
            self._send_html("<h1>404</h1>", 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/save-block":
            name = qs.get("file", [""])[0]
            idx = int(qs.get("idx", ["-1"])[0])
            length = int(self.headers.get("Content-Length", 0))
            new_text = self.rfile.read(length).decode("utf-8").strip()

            path = SCRIPT_DIR / name
            slides = parse_slides(path.read_text(encoding="utf-8")) if path.exists() else []
            if 0 <= idx < len(slides):
                slides[idx] = new_text
                path.write_text("\n\n---\n\n".join(slides) + "\n", encoding="utf-8")
                self._send_html("ok")
            else:
                self._send_html("bad index", 400)
        else:
            self._send_html("<h1>404</h1>", 404)

    def log_message(self, fmt, *args):
        pass  # 静かに動かす


class Server(socketserver.TCPServer):
    allow_reuse_address = True


def find_free_server():
    for port in range(PORT_RANGE_START, PORT_RANGE_END + 1):
        try:
            return Server(("127.0.0.1", port), Handler), port
        except OSError:
            continue
    raise RuntimeError("空いているポートが見つかりませんでした")


def main():
    SCRIPT_DIR.mkdir(exist_ok=True)
    httpd, port = find_free_server()
    PORT_FILE.write_text(str(port), encoding="utf-8")
    with httpd:
        url = f"http://127.0.0.1:{port}/"
        webbrowser.open(url)
        print(f"台本ビューア（シンちゃん版）起動: {url}  (Ctrl+Cで終了)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    sys.exit(main())
