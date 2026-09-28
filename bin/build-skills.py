#!/usr/bin/env python3
"""Render skills/index.html from the brainprotocol-skills marketplace manifest.

The catalogue is data: it lives in the skills repo's .claude-plugin/marketplace.json.
This script reads that manifest — from a local checkout when one is given, otherwise
from GitHub raw — and writes a static page. Nothing is fetched at page load, so the
page keeps working when GitHub does not.

    python3 bin/build-skills.py                      # read the manifest from GitHub
    python3 bin/build-skills.py /path/to/skills-repo  # read a local checkout
"""
import html
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "skills" / "index.html"
MANIFEST_PATH = ".claude-plugin/marketplace.json"
MANIFEST_URL = (
    "https://raw.githubusercontent.com/giobi/brainprotocol-skills/main/" + MANIFEST_PATH
)
REPO_URL = "https://github.com/giobi/brainprotocol-skills"

LABELS = {
    "workflow": "Thinking & Building",
    "creative": "Creative",
    "brain": "Brain core",
    "osint": "OSINT & Research",
    "design": "Design",
    "testing": "Testing & QA",
    "devops": "DevOps",
    "web": "Web & Content",
    "content": "Content & Publishing",
    "writing": "Writing",
    "email": "Email",
    "messaging": "Messaging",
    "productivity": "Productivity",
    "automation": "Automation",
    "ai": "AI",
    "infrastructure": "Infrastructure",
    "domains": "Domains",
    "learning": "Learning",
    "developer": "Developer",
    "meta": "Meta",
}
ORDER = list(LABELS)

# The two skills this page leads with: they are one idea in two halves.
FEATURED = {
    "design": (
        "Builds shared understanding before anyone writes anything. It grills you one "
        "question at a time until the concept holds in three sentences, captures the "
        "vocabulary as it surfaces — the words you and the agent are using differently "
        "without noticing — and settles the system into a few deep modules with narrow "
        "interfaces. The output is a design.md a future session can read cold."
    ),
    "build": (
        "Implements those modules under two constraints at once: TDD for the rhythm (one "
        "test, one implementation, no code without a test that demands it) and deep modules "
        "for the structure — you design the interface, the agent may write the "
        "implementation. After each area it asks whether the module can be delegated now, "
        "then loops back to update design.md so the map stays alive."
    ),
}


def load_manifest(argv):
    if len(argv) > 1:
        path = pathlib.Path(argv[1]) / MANIFEST_PATH
        print(f"manifest: {path}")
        return json.loads(path.read_text())
    print(f"manifest: {MANIFEST_URL}")
    with urllib.request.urlopen(MANIFEST_URL, timeout=20) as response:
        return json.loads(response.read())


def esc(text):
    return html.escape(str(text), quote=True)


def skill_card(plugin, featured=False):
    name = esc(plugin["name"])
    source = plugin.get("source", "").lstrip("./")
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in plugin.get("tags", [])[:4])
    body = FEATURED[plugin["name"]] if featured else plugin["description"]
    cls = "skill-card featured" if featured else "skill-card"
    return f"""      <article class="{cls}" data-name="{name}" data-search="{esc((plugin['name'] + ' ' + plugin['description'] + ' ' + ' '.join(plugin.get('tags', []))).lower())}">
        <div class="skill-head">
          <h3>/{name}</h3>
          <a class="skill-src" href="{REPO_URL}/tree/main/{esc(source)}">source</a>
        </div>
        <p>{esc(body)}</p>
        <div class="skill-foot">
          <div class="tags">{tags}</div>
          <code>/plugin install {name}</code>
        </div>
      </article>"""


def render(manifest):
    plugins = manifest["plugins"]
    total = len(plugins)
    featured = [p for p in plugins if p["name"] in FEATURED]
    featured.sort(key=lambda p: list(FEATURED).index(p["name"]))

    groups = {}
    for plugin in plugins:
        groups.setdefault(plugin.get("category", "other"), []).append(plugin)

    sections = []
    for category in ORDER + [c for c in sorted(groups) if c not in ORDER]:
        if category not in groups:
            continue
        cards = "\n".join(
            skill_card(p) for p in sorted(groups[category], key=lambda x: x["name"])
        )
        sections.append(
            f"""    <section class="cat-section" data-category="{esc(category)}">
      <div class="cat-header">
        <h2>{esc(LABELS.get(category, category.title()))}</h2>
        <span class="cat-count">{len(groups[category])}</span>
      </div>
      <div class="skill-grid">
{cards}
      </div>
    </section>"""
        )

    featured_cards = "\n".join(skill_card(p, featured=True) for p in featured)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skills — Brain Protocol</title>
  <meta name="description" content="{total} installable skills for Brain Protocol brains: design, build, research, testing, DevOps, publishing.">
  <meta property="og:title" content="Brain Protocol Skills">
  <meta property="og:description" content="{total} installable skills for Brain Protocol brains.">
  <meta property="og:url" content="https://brainprotocol.it/skills/">
  <meta property="og:type" content="website">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Rethink+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --negative: #e8e4df;
      --positive: #262c35;
      --positive-bold: #12151a;
      --positive-muted: #4c5159;
      --negative-muted: #d5d0cb;
      --accent: #4631e2;
      --accent-alt: #814bd1;
      --font-body: 'Rethink Sans', sans-serif;
      --font-mono: 'DM Mono', monospace;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-body);
      background: var(--negative);
      color: var(--positive);
      font-size: 16px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: var(--positive); text-decoration: none; }}
    a:hover {{ color: var(--accent); }}
    code, .mono {{ font-family: var(--font-mono); }}
    .container {{
      max-width: min(1200px, 90vw);
      margin: 0 auto;
      border-left: 1px solid var(--positive);
      border-right: 1px solid var(--positive);
    }}

    .nav {{
      position: sticky; top: 0; z-index: 50;
      background: rgba(232, 228, 223, 0.92);
      backdrop-filter: blur(12px);
      display: flex; justify-content: space-between; align-items: center;
      padding: 18px 48px;
      border-bottom: 1px solid var(--positive);
      font-family: var(--font-mono); font-size: 13px;
    }}
    .nav-logo {{ font-weight: 500; font-size: 15px; letter-spacing: -0.02em; color: var(--positive-bold); }}
    .nav-links {{ display: flex; gap: 24px; align-items: center; }}
    .nav-links a {{ color: var(--positive-muted); }}
    .nav-links a:hover {{ color: var(--positive-bold); }}

    .hero {{ padding: 64px 48px 48px; border-bottom: 1px solid var(--positive); }}
    .eyebrow {{
      font-family: var(--font-mono); font-size: 11px; color: var(--accent);
      text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 18px;
    }}
    .hero h1 {{ font-size: clamp(36px, 6vw, 64px); line-height: 1.05; letter-spacing: -0.03em; font-weight: 700; margin-bottom: 20px; }}
    .hero p {{ max-width: 62ch; font-size: 17px; color: var(--positive-muted); }}
    .hero p + p {{ margin-top: 14px; }}

    .install {{ border-bottom: 1px solid var(--positive); padding: 32px 48px; }}
    .install h2 {{ font-family: var(--font-mono); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--positive-muted); margin-bottom: 16px; }}
    pre {{
      font-family: var(--font-mono); font-size: 13px; line-height: 1.8;
      background: var(--positive-bold); color: var(--negative);
      padding: 20px 22px; overflow-x: auto;
    }}
    pre .c {{ color: #8d93a1; }}

    .cat-section {{ border-bottom: 1px solid var(--positive); }}
    .cat-header {{
      display: flex; align-items: baseline; gap: 12px;
      padding: 28px 48px 0;
    }}
    .cat-header h2 {{ font-size: 22px; letter-spacing: -0.02em; font-weight: 600; }}
    .cat-count {{ font-family: var(--font-mono); font-size: 12px; color: var(--positive-muted); }}
    .featured-section .cat-header h2 {{ font-size: 26px; }}

    .skill-grid {{
      display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      margin-top: 24px;
      border-top: 1px solid var(--positive);
    }}
    .skill-card {{
      background: var(--negative);
      padding: 24px 28px;
      display: flex; flex-direction: column; gap: 12px;
      border-right: 1px solid var(--positive);
      border-bottom: 1px solid var(--positive);
    }}
    .skill-grid > .skill-card:last-child {{ border-right: none; }}
    .cat-section:last-of-type .skill-card {{ border-bottom: none; }}
    .skill-card.featured {{ box-shadow: inset 3px 0 0 var(--accent); }}
    .skill-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }}
    .skill-head h3 {{ font-family: var(--font-mono); font-size: 17px; font-weight: 500; color: var(--positive-bold); }}
    .skill-src {{ font-family: var(--font-mono); font-size: 11px; color: var(--positive-muted); white-space: nowrap; }}
    .skill-card p {{ font-size: 14px; color: var(--positive-muted); line-height: 1.6; flex: 1; }}
    .skill-foot {{ display: flex; flex-direction: column; gap: 10px; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{
      font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.04em;
      color: var(--positive-muted); border: 1px solid var(--negative-muted);
      padding: 2px 7px; border-radius: 111px;
    }}
    .skill-foot code {{ font-size: 12px; color: var(--positive-bold); border-top: 1px dashed var(--negative-muted); padding-top: 10px; }}

    .filter-bar {{
      display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
      padding: 20px 48px; border-bottom: 1px solid var(--positive);
      position: sticky; top: 61px; z-index: 40;
      background: rgba(232, 228, 223, 0.94); backdrop-filter: blur(12px);
    }}
    .filter-bar input {{
      font-family: var(--font-mono); font-size: 13px;
      padding: 9px 14px; min-width: 260px; flex: 1; max-width: 420px;
      border: 1px solid var(--positive); background: var(--negative);
      color: var(--positive); border-radius: 111px;
    }}
    .filter-bar input:focus {{ outline: 2px solid var(--accent); outline-offset: -1px; }}
    .filter-count {{ font-family: var(--font-mono); font-size: 12px; color: var(--positive-muted); }}
    .no-results {{ padding: 40px 48px; font-family: var(--font-mono); font-size: 13px; color: var(--positive-muted); display: none; }}

    .write {{ padding: 40px 48px; border-bottom: 1px solid var(--positive); }}
    .write h2 {{ font-size: 24px; letter-spacing: -0.02em; margin-bottom: 14px; }}
    .write p {{ max-width: 68ch; font-size: 15px; color: var(--positive-muted); margin-bottom: 14px; }}

    .footer {{
      display: grid; grid-template-columns: 1fr 1fr 1fr; padding: 36px 48px;
      font-family: var(--font-mono); font-size: 12px; color: var(--positive-muted);
      border-bottom: 1px solid var(--positive);
    }}
    .footer-center {{ text-align: center; }}
    .footer-right {{ text-align: right; }}
    .footer a {{ color: var(--positive-muted); }}
    .footer a:hover {{ color: var(--positive-bold); }}

    @media (max-width: 768px) {{
      .container {{ max-width: 100vw; border: none; }}
      .nav {{ padding: 16px 20px; }}
      .nav-links {{ gap: 16px; }}
      .hero {{ padding: 40px 20px 36px; }}
      .install, .write, .cat-header, .filter-bar, .footer {{ padding-left: 20px; padding-right: 20px; }}
      .cat-header {{ padding-top: 24px; }}
      .skill-grid {{ grid-template-columns: 1fr; }}
      .skill-card {{ border-right: none; padding: 22px 20px; }}
      .filter-bar {{ top: 57px; }}
      .filter-bar input {{ max-width: none; }}
      .footer {{ grid-template-columns: 1fr; gap: 10px; text-align: left; }}
      .footer-center, .footer-right {{ text-align: left; }}
    }}
  </style>
</head>
<body>
<div class="container">
  <nav class="nav">
    <div class="nav-logo"><a href="/">Brain Protocol</a></div>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/brain.md">Spec</a>
      <a href="{REPO_URL}" target="_blank" rel="noopener">Repo</a>
    </div>
  </nav>

  <header class="hero">
    <div class="eyebrow mono">{total} skills &middot; MIT</div>
    <h1>Skills</h1>
    <p>A skill is a markdown file that teaches an agent a procedure: how to design something
    before building it, how to research a company, how to verify a page with a real browser,
    how to document an incident.</p>
    <p>They are protocol-level, so they work on any brain with any model. Install one, and the
    agent knows a way of working it did not know before.</p>
  </header>

  <section class="install">
    <h2>Install</h2>
    <pre><span class="c"># as a Claude Code plugin marketplace</span>
/plugin marketplace add giobi/brainprotocol-skills
/plugin install design

<span class="c"># or with the /brain package manager, inside any brain</span>
/brain install design

<span class="c"># or by hand — one folder, no build step</span>
curl -sL {REPO_URL}/raw/main/plugins/design/skills/design/SKILL.md \\
  -o .claude/skills/design/SKILL.md</pre>
  </section>

  <div class="filter-bar">
    <input type="search" id="q" placeholder="filter skills..." aria-label="Filter skills">
    <span class="filter-count mono" id="count">{total} of {total}</span>
  </div>
  <div class="no-results mono" id="empty">No skill matches that.</div>

  <section class="cat-section featured-section">
    <div class="cat-header">
      <h2>Start here: design, then build</h2>
      <span class="cat-count">2</span>
    </div>
    <div class="skill-grid">
{featured_cards}
    </div>
  </section>

{chr(10).join(sections)}

  <section class="write">
    <h2>Writing your own</h2>
    <p>A skill is a folder with a <code>SKILL.md</code>. The frontmatter is the whole contract:
    a name, a one-line description the agent matches on, and whether a human can invoke it.
    Everything after it is plain markdown — when to use it, when <em>not</em> to, the workflow,
    the fallbacks when a companion skill is missing.</p>
    <p>Write it in English, including the name: a skill name is an address, and addresses do not
    get translated. Keep the "when not to use this" section honest — it is what stops an agent
    reaching for the wrong tool.</p>
    <p><a href="{REPO_URL}#writing-your-own">How to publish one here &rarr;</a></p>
  </section>

  <footer class="footer">
    <div>Brain Protocol &copy; 2026</div>
    <div class="footer-center">
      <a href="{REPO_URL}">Skills repo</a> &middot;
      <a href="https://github.com/giobi/brainprotocol">Protocol</a> &middot;
      <a href="/brain.md">Spec</a>
    </div>
    <div class="footer-right">
      <a href="https://giobi.com" target="_blank" rel="noopener">giobi.com</a>
    </div>
  </footer>
</div>

<script>
  (function () {{
    var input = document.getElementById('q');
    var count = document.getElementById('count');
    var empty = document.getElementById('empty');
    var cards = Array.prototype.slice.call(document.querySelectorAll('.skill-card'));
    var sections = Array.prototype.slice.call(document.querySelectorAll('.cat-section'));
    var total = {total};

    function apply() {{
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {{
        var hit = !q || card.dataset.search.indexOf(q) !== -1;
        card.style.display = hit ? '' : 'none';
        if (hit && !card.classList.contains('featured')) shown++;
      }});
      sections.forEach(function (section) {{
        var visible = section.querySelectorAll('.skill-card:not([style*="none"])').length;
        section.style.display = visible ? '' : 'none';
      }});
      count.textContent = shown + ' of ' + total;
      empty.style.display = shown ? 'none' : 'block';
    }}

    input.addEventListener('input', apply);
  }})();
</script>
</body>
</html>
"""


def main():
    manifest = load_manifest(sys.argv)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(manifest))
    print(f"wrote {OUT} ({len(manifest['plugins'])} skills, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
