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

PORT = 8801
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
SCRIPT_DIR = BASE_DIR / "03_台本"

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

  .dots{display:flex;gap:7px;justify-content:center;margin-bottom:22px;}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--border);}
  .dot.active{background:var(--accent);width:22px;border-radius:5px;}

  .section-label{text-align:center;font-size:13px;color:var(--ink-dim);
    letter-spacing:.1em;margin-bottom:10px;}
  .slide{background:#fff;border-left:10px solid var(--accent);border-radius:4px;
    padding:7% 9%;min-height:56vh;display:flex;align-items:center;justify-content:center;
    box-shadow:0 3px 14px rgba(43,38,32,.08);margin-bottom:24px;}
  .slide-text{font-size:var(--fs,32px);line-height:1.95;white-space:pre-wrap;
    letter-spacing:.02em;}

  .nav{display:flex;gap:12px;justify-content:center;margin-top:8px;}
  .nav .btn{padding:14px 30px;font-size:15px;}

  textarea{width:100%;min-height:56vh;font-size:16px;line-height:1.8;padding:18px;
    border:1px solid var(--border);border-radius:4px;font-family:inherit;background:#fff;}

  @media (max-width:600px){ .slide-text{font-size:calc(var(--fs, 32px) * 0.75);} }
</style>
"""


def parse_slides(text: str):
    blocks = [b.strip() for b in text.split("---") if b.strip()]
    return blocks if blocks else [text]


def section_label(slide_text: str) -> str:
    m = re.match(r"^【(.+?)】", slide_text)
    return m.group(1) if m else ""


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


def render_view(name: str, idx: int):
    path = SCRIPT_DIR / name
    if not path.exists():
        return "<h1>ファイルが見つかりません</h1>"
    slides = parse_slides(path.read_text(encoding="utf-8"))
    idx = max(0, min(idx, len(slides) - 1))
    label = section_label(slides[idx])
    accent = color_for(label)
    body = html.escape(slides[idx])
    qname = urllib.parse.quote(name)
    prev_disabled = "disabled" if idx == 0 else ""
    next_disabled = "disabled" if idx == len(slides) - 1 else ""

    dots = "".join(
        f'<a class="dot{" active" if i == idx else ""}" '
        f'style="background:{color_for(section_label(s)) if i == idx else "var(--border)"}" '
        f'href="/view?file={qname}&idx={i}"></a>'
        for i, s in enumerate(slides)
    )

    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>{html.escape(name)}</title>{PAGE_CSS}</head><body style="--accent:{accent}">
<header>
  <h1>{html.escape(name)}</h1>
  <div>
    <a class="btn" href="/">一覧へ</a>
    <a class="btn" href="/edit?file={qname}">編集</a>
  </div>
</header>
<main>
  <div class="toolbar">
    <button onclick="adjust(-4)">A－</button>
    <button onclick="adjust(4)">A＋</button>
  </div>
  <div class="dots">{dots}</div>
  <div class="section-label">{html.escape(label) or "&nbsp;"}（{idx+1} / {len(slides)}）</div>
  <div class="slide"><div class="slide-text" id="txt" style="--fs:32px">{body}</div></div>
  <div class="nav">
    <a class="btn" {prev_disabled} href="/view?file={qname}&idx={idx-1}">← 前へ</a>
    <a class="btn primary" {next_disabled} href="/view?file={qname}&idx={idx+1}">次へ →</a>
  </div>
</main>
<script>
let fs = 32;
function adjust(d){{
  fs = Math.max(18, Math.min(56, fs + d));
  document.getElementById('txt').style.setProperty('--fs', fs + 'px');
}}
document.addEventListener('keydown', (e) => {{
  if (e.key === 'ArrowRight' || e.key === ' ') location.href = "/view?file={qname}&idx={idx+1}";
  if (e.key === 'ArrowLeft') location.href = "/view?file={qname}&idx={idx-1}";
}});
</script>
</body></html>"""


def render_edit(name: str):
    path = SCRIPT_DIR / name
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    qname = urllib.parse.quote(name)
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>編集: {html.escape(name)}</title>{PAGE_CSS}</head><body>
<header><h1>編集: {html.escape(name)}</h1>
  <a class="btn" href="/view?file={qname}">表示に戻る</a>
</header>
<main>
  <form method="post" action="/save?file={qname}">
    <textarea name="content">{html.escape(content)}</textarea><br><br>
    <button class="primary" type="submit">保存</button>
  </form>
</main>
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
            idx = int(qs.get("idx", ["0"])[0])
            self._send_html(render_view(name, idx))
        elif parsed.path == "/edit":
            name = qs.get("file", [""])[0]
            self._send_html(render_edit(name))
        else:
            self._send_html("<h1>404</h1>", 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/save":
            name = qs.get("file", [""])[0]
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            form = urllib.parse.parse_qs(body)
            content = form.get("content", [""])[0]
            path = SCRIPT_DIR / name
            path.write_text(content, encoding="utf-8")
            self.send_response(303)
            self.send_header("Location", f"/view?file={urllib.parse.quote(name)}")
            self.end_headers()
        else:
            self._send_html("<h1>404</h1>", 404)

    def log_message(self, fmt, *args):
        pass  # 静かに動かす


def main():
    SCRIPT_DIR.mkdir(exist_ok=True)
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}/"
        webbrowser.open(url)
        print(f"台本ビューア（シンちゃん版）起動: {url}  (Ctrl+Cで終了)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    sys.exit(main())
