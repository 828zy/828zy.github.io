"""Regenerate the static homepage from profile.json; no dependencies required."""
import json
import hashlib
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE_VERSION = hashlib.sha256((ROOT / 'assets/css/site.css').read_bytes()).hexdigest()[:12]
base_profile = json.loads((ROOT / 'profile.json').read_text())
def build(p, language, output):
    e = lambda value: escape(str(value), quote=True)
    t = lambda zh, en: en if language == 'en' else zh

    def linked_label(label, url=None):
        if not url:
            return e(label)
        return f'<a class="profile-reference" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'

    references = dict(p.get('school_links', {}))
    for item in p.get('internships', []):
        for field in ('institution', 'mentor'):
            if item.get(field + '_url'):
                references[item[field]] = item[field + '_url']

    def linked_text(text):
        if not references:
            return e(text)
        pattern = '(' + '|'.join(re.escape(label) for label in sorted(references, key=len, reverse=True)) + ')'
        return ''.join(linked_label(part, references.get(part)) for part in re.split(pattern, str(text)))

    sections = [('about', 'About Me'), ('experience', 'Experience'), ('honors', 'Honors'), ('publications', 'Publications'), ('projects', 'Projects')]
    nav = ''.join(f'<li><a class="site-nav__link" href="#{key}">{label}</a></li>' for key, label in sections)
    cards = ''
    for item in p['projects']:
        title = linked_label(item['name'], item.get('url'))
        status = f'<p class="project-status">{e(item["status"])}</p>' if item.get('status') else ''
        link = f'<a class="project-page-link" href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">{t("项目主页", "Project page")} ↗</a>' if item.get('url') else ''
        image = f'<div class="research-project-image"><img src="{e(item["image"])}" alt="{e(item.get("image_alt", item["name"]))}" width="1600" height="780" loading="lazy"></div>' if item.get('image') else ''
        image_class = ' research-project-with-image' if image else ''
        cards += f'<article class="research-project{image_class}">{image}<div class="research-project-content"><h3>{title}</h3><p>{e(item["description"])}</p>{status}{link}</div></article>'
    email = f'<a class="email-link" href="mailto:{e(p["email"])}" aria-label="{t("发送邮件至", "Email")} {e(p["email"])}">{e(p["email"])}</a>' if p['email'] else ''
    phone = f'<a class="phone-link" href="tel:{e(p["phone"])}">{t("电话：", "Phone: ")}{e(p["phone"])}</a>' if p.get('phone') else ''
    education = ''
    for item in p.get('education', []):
        highlights = ''.join(f'<span>{e(value)}</span>' for value in item['highlights'])
        detail = f'<p class="timeline-detail">{e(item["detail"])}</p>' if item['detail'] else ''
        education += f'''<li class="timeline-entry"><span class="timeline-point" aria-hidden="true"></span><div class="timeline-heading"><h4>{linked_text(item['institution'])}</h4><span class="timeline-date">{e(item['period'])}</span></div>{detail}<div class="academic-highlights">{highlights}</div></li>'''
    internships = ''
    research_summary = linked_text(p.get('research_summary', ''))
    for item in p.get('internships', []):
        institution = linked_text(item['institution'])
        mentor = linked_text(item['mentor'])
        internships += f'''<li class="timeline-entry"><span class="timeline-point" aria-hidden="true"></span><div class="timeline-heading"><h4>{institution}</h4><span class="timeline-date">{e(item['period'])}</span></div><p class="timeline-role">{e(item['role'])}</p><p class="timeline-detail">{t("研究方向：", "Research: ")}{e(item['direction'])}</p><p class="timeline-mentor">{e(item['mentor_label'])}{t("：", ": ")}{mentor}</p></li>'''
    def honor_list(items):
        rows = ''
        for item in items:
            trophy = '🏆 ' if item.get('trophy', True) else ''
            if item.get('award'):
                prize = (f' ({e(item["prize"])})' if language == 'en' else f'（{e(item["prize"])}）') if item.get('prize') else ''
                award = f'<strong>{e(item["award"])}{prize}</strong>' if item.get('prize_emphasized') else f'<strong>{e(item["award"])}</strong>{prize}'
                content = f'{e(item["name"])}{t("，获", ", ")}{award}{t("。", ".")}<span class="honor-location">{e(item["location"])}</span>'
            else:
                emphasis = ' class="honor-emphasized"' if item.get('emphasized') else ''
                content = f'{t("获得", "")}<strong{emphasis}>{e(item["name"])}</strong>{t("。", "")}'
            rows += f'<li class="honor-row"><p><em><time datetime="{e(item["date"].replace(".", "-"))}">{e(item["date"])}</time>{t("：", ":")}</em> {trophy}{content}</p></li>'
        return f'<ul class="honor-list">{rows}</ul>' if rows else f'<p class="honors-pending">{t("待补充", "Coming soon")}</p>'

    scholarships = honor_list(p.get('honors', {}).get('scholarships', []))
    competitions = honor_list(p.get('honors', {}).get('competitions', []))
    publication_groups = {}
    for item in p.get('publications', []):
        authors = []
        for name in item['authors']:
            author = f'<strong>{e(name)}</strong>' if name == p.get('publication_author_name') else e(name)
            if name in item.get('equal_contribution', []):
                author += '<sup>*</sup>'
            authors.append(author)
        contribution = f' · <span class="publication-contribution">{t("共同一作", "Co-first author")}</span>' if p.get('publication_author_name') in item.get('equal_contribution', []) else ''
        links = ''.join(f'<a href="{e(link["url"])}" target="_blank" rel="noopener noreferrer">{e(t(link["label"], {"论文": "Paper", "会议页面": "Conference"}.get(link["label"], link["label"])))}</a>' for link in item.get('links', []))
        publication_groups.setdefault(item['year'], []).append(f'''<li class="publication-item"><h3 class="publication-title"><a href="{e(item['url'])}" target="_blank" rel="noopener noreferrer">{e(item['title'])}</a></h3><p class="publication-venue">{e(item['venue'])} {e(item['year'])}{contribution}</p><p class="publication-authors">{', '.join(authors)}</p><div class="publication-links">{links}</div></li>''')
    publications = ''.join(f'<h3 class="publication-year">{e(year)}</h3><ol class="publication-list">{"".join(items)}</ol>' for year, items in sorted(publication_groups.items(), reverse=True))
    if any(item.get('equal_contribution') for item in p.get('publications', [])):
        publications += f'<p class="publication-note">{t("* 共同第一作者（Equal contribution）", "* Equal contribution")}</p>'
    projects_content = f'<h2><span class="section-symbol" aria-hidden="true">▦</span> Projects</h2><div class="research-projects">{cards}</div>' if cards else f'<h2><span class="section-symbol" aria-hidden="true">▦</span> Projects</h2><p class="honors-pending">{t("待补充", "Coming soon")}</p>'

    html = f'''<!doctype html>
    <html lang="{t("zh-CN", "en")}" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{e(p['site_name'])} — {e(p['name'])}</title><meta name="description" content="{e(p['bio'])}">
    <meta name="color-scheme" content="light dark"><link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="assets/css/template.css"><link rel="stylesheet" href="assets/css/template-additions.css"><link rel="stylesheet" href="assets/css/site.css?v={STYLE_VERSION}">
    <script>try{{const t=localStorage.getItem('mzy-theme-v2');if(['light','yellow','blue','dark'].includes(t)){{if(t==='light')delete document.documentElement.dataset.theme;else document.documentElement.dataset.theme=t;}}}}catch(e){{}}</script>
    <script src="assets/js/site.js" defer></script></head>
    <body><a class="skip-link" href="#about">{t('跳到正文', 'Skip to content')}</a>
    <header class="masthead"><div class="masthead__inner-wrap"><a href="#about" class="site-brand">{e(p['site_name'])}<span class="brand-dot"></span></a><nav id="site-nav" class="site-nav" aria-label="{t('主页导航', 'Main navigation')}"><ul class="site-nav__links">{nav}</ul></nav></div></header>
    <div id="main" role="main"><aside class="sidebar sticky"><div class="profile_box">
    <div class="author__avatar"><div class="portrait-frame"><img src="{e(p['avatar'])}" alt="{e(p['name'])}{t('的头像', '’s portrait')}" width="1024" height="1536"><span class="portrait-tag">HELLO, WORLD.</span></div></div>
    <div class="author__content"><h1 class="author__name">{e(p['name'])}</h1></div>
    <p class="author__direction">{linked_text(p['affiliation'])}<br>{e(p['direction'])}</p>
    <div class="author__social-icons">{email}{phone}</div>
    <div class="profile-note"><span class="status-dot"></span> A little work in progress</div>
    <div class="appearance-controls"><fieldset class="theme-picker"><legend>APPEARANCE</legend><button type="button" data-theme-choice="light" aria-label="{t('白色主题', 'Light theme')}" aria-pressed="true"></button><button type="button" data-theme-choice="yellow" aria-label="{t('暖色主题', 'Warm theme')}" aria-pressed="false"></button><button type="button" data-theme-choice="blue" aria-label="{t('蓝色主题', 'Blue theme')}" aria-pressed="false"></button><button type="button" data-theme-choice="dark" aria-label="{t('深色主题', 'Dark theme')}" aria-pressed="false"></button></fieldset><a class="language-toggle" href="{'index.html' if language == 'zh' else 'zh.html'}" lang="{'en' if language == 'zh' else 'zh-CN'}" aria-label="{t('Switch to English', '切换为中文')}">{t('EN', '中文')}</a></div>
    </div></aside>
    <article class="page"><div class="page__inner-wrap"><div class="page__content">
    <section id="about" class="about-section"><div class="section-kicker">MY LITTLE CORNER OF THE INTERNET</div><h2><span class="section-symbol" aria-hidden="true">✳</span> About Me</h2><p class="intro-lead">{t('你好，我是', 'Hi, I’m')} <strong>{e(p['name'])}</strong><span class="wave"> 👋</span></p><p>{linked_text(p['bio'])}</p><p>{research_summary}</p><p>{linked_text(p.get("next_step", ""))}</p><div class="topic-pills"><span>{t('多模态大模型', 'Large multimodal models')}</span><span>{t('世界模型', 'World models')}</span></div></section>
    <section id="experience"><h2><span class="section-symbol" aria-hidden="true">◷</span> Experience</h2><h3 class="experience-group-title">{t('教育经历', 'Education')} <span>EDUCATION</span></h3><ol class="personal-timeline">{education}</ol><h3 class="experience-group-title">{t('实习经历', 'Research experience')} <span>RESEARCH EXPERIENCE</span></h3><ol class="personal-timeline">{internships}</ol></section>
    <section id="honors"><h2><span class="section-symbol" aria-hidden="true">✧</span> Honors</h2><h3 class="experience-group-title">{t('奖学金', 'Scholarships')} <span>SCHOLARSHIPS</span></h3>{scholarships}<h3 class="experience-group-title">{t('竞赛', 'Competitions')} <span>COMPETITIONS</span></h3>{competitions}</section>
    <section id="publications"><h2><span class="section-symbol" aria-hidden="true">▤</span> Publications</h2>{publications}</section>
    <section id="projects">{projects_content}</section>
    <footer class="site-footer"><span>© 2026 {e(p['name'])} <span class="footer-dot">·</span> Keep exploring.</span><a href="#about">{t('回到顶部', 'Back to top')} ↑</a></footer>
    </div></div></article></div><noscript><p class="noscript-note">{t("正文与项目链接可正常浏览；主题切换需要 JavaScript。", "Content and links work without JavaScript. Theme switching requires JavaScript.")}</p></noscript></body></html>'''
    (ROOT / output).write_text(html)
    print(f'Built {output} ({language})')


build(base_profile, "zh", "zh.html")
english = {**base_profile, **json.loads((ROOT / "locales/en.json").read_text())}
build(english, "en", "index.html")
