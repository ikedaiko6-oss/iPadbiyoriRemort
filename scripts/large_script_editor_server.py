#!/usr/bin/env python3
"""
大きい文字の台本ビューア／エディタ（ローカル専用サーバー）

03_台本/ 内の .txt を、大きい文字のスライド風テレプロンプターとして
ブラウザ（127.0.0.1）に表示する。編集して保存もできる。

外部公開はしない。127.0.0.1 のみでLISTENする。
"""
import http.server
import socketserver
import urllib.parse
import pathlib
import html
import webbrowser
import sys

PORT = 8765
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
SCRIPT_DIR = BASE_DIR / "03_台本"

PAGE_CSS = """
<style>
  :root{--ink:#1e222a;--ink-dim:#8a8f98;--panel:#f4f5f7;--border:#e3e5e9;--accent:#4a7dfc;}
  *{box-sizing:border-box;}
  body{margin:0;font-family:-apple-system,"Hiragino Sans",sans-serif;background:var(--panel);color:var(--ink);}
  header{padding:16px 24px;background:#fff;border-bottom:1px solid var(--border);
    display:flex;justify-content:space-between;align-items:center;}
  header h1{font-size:16px;margin:0;}
  main{padding:24px;max-width:900px;margin:0 auto;}
  ul.filelist{list-style:none;padding:0;}
  ul.filelist li{margin-bottom:10px;}
  ul.filelist a{display:block;padding:14px 18px;background:#fff;border:1px solid var(--border);
    border-radius:8px;text-decoration:none;color:var(--ink);font-size:15px;}
  ul.filelist a:hover{border-color:var(--accent);}
  .slide{background:#fff;border-top:8px solid var(--accent);border-radius:10px;
    padding:6% 8%;min-height:60vh;display:flex;align-items:center;justify-content:center;
    box-shadow:0 2px 10px rgba(0,0,0,.06);margin-bottom:20px;}
  .slide-text{font-size:var(--fs,32px);line-height:1.8;white-space:pre-wrap;font-weight:600;}
  .toolbar{display:flex;gap:10px;align-items:center;margin-bottom:16px;flex-wrap:wrap;}
  button, .btn{background:#fff;border:1px solid var(--border);padding:10px 18px;border-radius:8px;
    font-size:14px;cursor:pointer;color:var(--ink);text-decoration:none;}
  button.primary{background:var(--accent);color:#fff;border-color:transparent;}
  .nav{display:flex;gap:10px;justify-content:center;margin-top:16px;}
  textarea{width:100%;min-height:60vh;font-size:16px;line-height:1.7;padding:16px;
    border:1px solid var(--border);border-radius:8px;font-family:inherit;}
  .slide-index{font-size:12px;color:var(--ink-dim);text-align:center;margin-bottom:8px;}
</style>
"""


def parse_slides(text: str):
    blocks = [b.strip() for b in text.split("---") if b.strip()]
    return blocks if blocks else [text]


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
<title>台本一覧</title>{PAGE_CSS}</head><body>
<header><h1>台本 大きい文字ビューア</h1></header>
<main><ul class="filelist">{items}</ul></main>
</body></html>"""


def render_view(name: str, idx: int):
    path = SCRIPT_DIR / name
    if not path.exists():
        return "<h1>ファイルが見つかりません</h1>"
    slides = parse_slides(path.read_text(encoding="utf-8"))
    idx = max(0, min(idx, len(slides) - 1))
    body = html.escape(slides[idx])
    qname = urllib.parse.quote(name)
    prev_disabled = "disabled" if idx == 0 else ""
    next_disabled = "disabled" if idx == len(slides) - 1 else ""
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>{html.escape(name)}</title>{PAGE_CSS}</head><body>
<header>
  <h1>{html.escape(name)}</h1>
  <div>
    <a class="btn" href="/">一覧へ</a>
    <a class="btn" href="/edit?file={qname}">編集</a>
  </div>
</header>
<main>
  <div class="toolbar">
    <button onclick="adjust(-4)">A-</button>
    <button onclick="adjust(4)">A+</button>
  </div>
  <div class="slide-index">{idx+1} / {len(slides)}</div>
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
  if (e.key === 'ArrowRight' || e.key === ' ') {{
    document.querySelector('.nav-btn-next')?.click();
  }}
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
        print(f"台本ビューア起動: {url}  (Ctrl+Cで終了)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    sys.exit(main())
