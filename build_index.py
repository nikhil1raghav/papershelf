#!/usr/bin/env python3
"""Generate a categorized HTML index from the scraped Acolyer blog data."""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "acolyer_data.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "acolyer-index.html")

# High-level groupings mapping original tags to sections
SECTIONS = {
    "Distributed Systems & Consensus": [
        "Distributed Systems", "Consistency", "Concurrency",
        "Blockchain", "Transaction processing"
    ],
    "Machine Learning & AI": [
        "Machine Learning", "Deep Learning", "AI",
        "Data Science", "Analytics"
    ],
    "Database Systems & Data Engines": [
        "Datastores", "Storage", "Stream processing",
        "Time series", "Graph", "Web Scale"
    ],
    "Software Engineering, Testing, & Security": [
        "Software Engineering", "Testing", "Security",
        "Privacy", "Formal methods", "Ethics", "Operations"
    ],
    "Operating Systems, Networks, & Hardware": [
        "Operating Systems", "Networking", "Hardware",
        "Containers", "Virtualization", "IoT", "mobile", "Scheduling"
    ],
    "Programming Languages & Algorithms": [
        "Programming Languages", "Programming",
        "Algorithms and data structures"
    ],
    "By Company": [
        "Amazon", "Facebook", "Google", "Microsoft"
    ],
    "More Topics": [
        "Great moments", "HCI", "Provenance", "quantum",
        "Robotics", "Social Networks"
    ],
}


def build_html(data):
    categories = data["categories"]
    generated = data["generated"]

    sections_html = ""

    for section_name, tag_names in SECTIONS.items():
        total_in_section = 0
        tags_html = ""

        for tag_name in tag_names:
            if tag_name not in categories:
                continue
            posts = categories[tag_name]
            if not posts:
                continue

            total_in_section += len(posts)
            post_items = ""
            for p in posts:
                title = p["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                url = p["url"].replace("&", "&amp;")
                date = p.get("date", "")
                post_items += f'                    <li><a href="{url}" class="block py-1 hover:text-[#C8102E] transition-colors motion-safe:transition-colors"><span class="text-stone-900/70 dark:text-stone-50/70 text-xs tabular-nums mr-2">{date}</span>{title}</a></li>\n'

            tag_id = tag_name.lower().replace(" ", "-").replace(",", "")
            tags_html += f"""
                <div class="border border-stone-200 dark:border-stone-800 rounded-sm">
                    <button onclick="toggleCategory('{tag_id}')"
                            class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none"
                            aria-expanded="false" aria-controls="cat-{tag_id}">
                        <span class="text-base font-medium text-stone-900 dark:text-stone-50">{tag_name}</span>
                        <span class="flex items-center gap-2">
                            <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{len(posts)}</span>
                            <svg class="w-4 h-4 text-stone-900/40 dark:text-stone-50/40 transition-transform motion-safe:transition-transform" id="icon-{tag_id}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                        </span>
                    </button>
                    <div id="cat-{tag_id}" class="hidden">
                        <ul class="px-4 pb-3 space-y-0.5 max-h-[60vh] overflow-y-auto">
{post_items}                        </ul>
                    </div>
                </div>
"""

        section_id = section_name.lower().replace(" ", "-").replace(",", "").replace("&", "and")
        sections_html += f"""
            <section class="py-16 md:py-20 border-b border-stone-200 dark:border-stone-800" id="{section_id}">
                <div class="max-w-5xl mx-auto px-4 md:px-8">
                    <div class="flex items-baseline justify-between mb-8">
                        <h2 class="text-2xl md:text-3xl font-light tracking-tight text-stone-900 dark:text-stone-50 text-balance">{section_name}</h2>
                        <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{total_in_section} papers</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
{tags_html}                    </div>
                </div>
            </section>
"""

    # Build the full HTML
    total_posts = sum(len(v) for v in categories.values())
    unique_posts = len(set(
        p["url"] for v in categories.values() for p in v
    ))

    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" content="#fafaf9" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0c0a09" media="(prefers-color-scheme: dark)">
    <title>The Morning Paper · Adrian Colyer · Index</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'media',
            theme: {{
                fontFamily: {{
                    sans: ['IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', 'system-ui', 'sans-serif'],
                }}
            }}
        }}
    </script>
    <style>
        html {{ color-scheme: light dark; }}
        body {{ font-family: 'IBM Plex Sans', 'Hanken Grotesk', 'Barlow', 'Host Grotesk', 'DM Sans', system-ui, sans-serif; }}
    </style>
</head>
<body class="bg-stone-50 dark:bg-stone-950 text-stone-900 dark:text-stone-50 antialiased">

    <!-- Header -->
    <header class="border-b border-stone-200 dark:border-stone-800 sticky top-0 bg-stone-50/95 dark:bg-stone-950/95 backdrop-blur-sm z-10">
        <div class="max-w-5xl mx-auto px-4 md:px-8 py-6">
            <div class="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-4">
                <div>
                    <h1 class="text-3xl md:text-4xl font-light tracking-tight text-stone-900 dark:text-stone-50 text-balance">The Morning Paper</h1>
                    <p class="text-sm text-stone-900/50 dark:text-stone-50/50 mt-1">A categorized index of Computer Science research paper breakdowns by <a href="https://blog.acolyer.org/about/" class="underline hover:text-[#C8102E] transition-colors motion-safe:transition-colors">Adrian Colyer</a></p>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-xs text-stone-900/40 dark:text-stone-50/40 tabular-nums">{total_posts} entries · {unique_posts} unique papers</span>
                </div>
            </div>
            <!-- Search -->
            <div class="mt-4 relative">
                <input type="text" id="search" placeholder="Search papers…"
                       class="w-full px-4 py-2 bg-stone-100 dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-sm text-base text-stone-900 dark:text-stone-50 placeholder:text-stone-900/30 dark:placeholder:text-stone-50/30 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#C8102E] transition-colors motion-safe:transition-colors"
                       oninput="filterPapers()">
                <span id="search-count" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-stone-900/30 dark:text-stone-50/30 hidden"></span>
            </div>
            <!-- Quick nav -->
            <nav class="mt-4 flex flex-wrap gap-2" aria-label="Jump to section">
                {''.join(f'<a href="#{s.lower().replace(" ", "-").replace(",", "").replace("&", "and")}" class="text-xs px-2 py-1 bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-sm hover:border-[#C8102E]/40 hover:text-[#C8102E] transition-colors motion-safe:transition-colors focus-visible:ring-2 focus-visible:ring-[#C8102E] focus-visible:outline-none min-h-[44px] min-w-[44px] inline-flex items-center">{s}</a>' for s in SECTIONS.keys())}
            </nav>
        </div>
    </header>

    <main>
{sections_html}    </main>

    <!-- Footer -->
    <footer class="py-16 border-t border-stone-200 dark:border-stone-800">
        <div class="max-w-5xl mx-auto px-4 md:px-8 text-center">
            <p class="text-xs text-stone-900/40 dark:text-stone-50/40">
                Data sourced from <a href="https://blog.acolyer.org" class="underline hover:text-[#C8102E] transition-colors motion-safe:transition-colors">blog.acolyer.org</a> · Generated {generated}<br>
                All paper breakdowns © Adrian Colyer · Built as a community index
            </p>
        </div>
    </footer>

    <script>
        // Toggle category expansion
        function toggleCategory(id) {{
            const panel = document.getElementById('cat-' + id);
            const icon = document.getElementById('icon-' + id);
            const button = panel.previousElementSibling;
            const isOpen = !panel.classList.contains('hidden');
            if (isOpen) {{
                panel.classList.add('hidden');
                icon.style.transform = 'rotate(0deg)';
                button.setAttribute('aria-expanded', 'false');
            }} else {{
                panel.classList.remove('hidden');
                icon.style.transform = 'rotate(180deg)';
                button.setAttribute('aria-expanded', 'true');
            }}
        }}

        // Search / filter papers
        function filterPapers() {{
            const query = document.getElementById('search').value.toLowerCase().trim();
            const countEl = document.getElementById('search-count');
            const sections = document.querySelectorAll('main > section');
            let visibleSections = 0;

            sections.forEach(section => {{
                const buttons = section.querySelectorAll('button[onclick^="toggleCategory"]');
                let sectionHasVisible = false;

                buttons.forEach(button => {{
                    const panelId = button.getAttribute('aria-controls');
                    const panel = document.getElementById(panelId);
                    const container = button.parentElement;
                    const links = panel.querySelectorAll('a');
                    let anyVisible = false;

                    links.forEach(link => {{
                        const text = link.textContent.toLowerCase();
                        if (!query || text.includes(query)) {{
                            link.style.display = '';
                            anyVisible = true;
                        }} else {{
                            link.style.display = 'none';
                        }}
                    }});

                    if (anyVisible || !query) {{
                        container.style.display = '';
                        sectionHasVisible = true;
                        if (query && anyVisible) {{
                            panel.classList.remove('hidden');
                            const icon = panel.parentElement.querySelector('svg');
                            if (icon) icon.style.transform = 'rotate(180deg)';
                            button.setAttribute('aria-expanded', 'true');
                        }}
                    }} else {{
                        container.style.display = 'none';
                    }}
                }});

                if (sectionHasVisible || !query) {{
                    section.style.display = '';
                    visibleSections++;
                }} else {{
                    section.style.display = 'none';
                }}
            }});

            if (query) {{
                countEl.classList.remove('hidden');
                countEl.textContent = visibleSections + ' sections';
            }} else {{
                countEl.classList.add('hidden');
                // Collapse all back
                document.querySelectorAll('[id^="cat-"]').forEach(p => p.classList.add('hidden'));
                document.querySelectorAll('button[onclick^="toggleCategory"]').forEach(b => b.setAttribute('aria-expanded', 'false'));
                document.querySelectorAll('svg[id^="icon-"]').forEach(s => s.style.transform = 'rotate(0deg)');
            }}
        }}
    </script>
</body>
</html>
"""

    return html


def main():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    html = build_html(data)

    with open(OUTPUT_FILE, "w") as f:
        f.write(html)

    print(f"Generated {OUTPUT_FILE}")

    # Count stats
    cats = data["categories"]
    total = sum(len(v) for v in cats.values())
    unique = len(set(p["url"] for v in cats.values() for p in v))
    print(f"Total entries: {total}")
    print(f"Unique papers: {unique}")
    print(f"Categories: {len(cats)}")
    print(f"Sections: {len(SECTIONS)}")


if __name__ == "__main__":
    main()
