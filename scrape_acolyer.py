#!/usr/bin/env python3
"""Scrape all paper breakdowns from blog.acolyer.org by tag category."""

import subprocess
import json
import time
import os
import sys

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(OUTPUT_DIR, "acolyer_data.json")

TAGS = [
    "AI|ai",
    "Algorithms and data structures|algorithms-and-data-structures",
    "Amazon|amazon",
    "Analytics|analytics",
    "Blockchain|blockchain",
    "Concurrency|concurrency",
    "Consistency|consistency",
    "Containers|containers",
    "Data Science|data-science",
    "Datastores|datastores",
    "Deep Learning|deep-learning",
    "Distributed Systems|distributed-systems",
    "Ethics|ethics",
    "Facebook|facebook",
    "Formal methods|formal-methods",
    "Google|google",
    "Graph|graph",
    "Great moments|great-moments",
    "Hardware|hardware",
    "HCI|hci",
    "IoT|iot",
    "Machine Learning|machine-learning",
    "Microsoft|microsoft",
    "mobile|mobile",
    "Networking|networking",
    "Operating Systems|operating-systems",
    "Operations|operations",
    "Performance|performance",
    "Privacy|privacy",
    "Programming|programming",
    "Programming Languages|programming-languages",
    "Provenance|provenance",
    "quantum|quantum",
    "Robotics|robotics",
    "Scheduling|scheduling",
    "Security|security",
    "Social Networks|social-networks",
    "Software Engineering|software-engineering",
    "Storage|storage",
    "Stream processing|stream-processing",
    "Testing|testing",
    "Time series|time-series",
    "Transaction processing|transaction-processing",
    "Virtualization|virtualization",
    "Web Scale|web-scale",
]

def run_browser(*args):
    """Run agent-browser command, return stdout."""
    result = subprocess.run(
        ["agent-browser"] + list(args),
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()

def eval_js_raw(js_code):
    """Run JS eval, return raw stdout string."""
    result = subprocess.run(
        ["agent-browser", "eval", "--stdin"],
        input=js_code, capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()

def eval_js(js_code):
    """
    Run JS eval and parse result.
    agent-browser eval returns values as JSON-encoded strings.
    e.g., the number 5 is returned as the string "5",
          a JSON array is returned as a quoted JSON string "[...]"
          a boolean is returned as "true" or "false"
    We attempt to JSON-parse once, then if it's a string, parse again.
    """
    raw = eval_js_raw(js_code)
    # First parse: get the JSON-encoded value
    try:
        val = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    
    # If the result is a string that looks like JSON, parse it too
    if isinstance(val, str) and val.strip().startswith(('[', '{')):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return val
    
    return val

def scrape_tag(tag_name, tag_slug):
    """Scrape all posts for a given tag across all pages."""
    all_posts = []
    page_num = 1
    
    while True:
        if page_num == 1:
            url = f"https://blog.acolyer.org/tag/{tag_slug}/"
        else:
            url = f"https://blog.acolyer.org/tag/{tag_slug}/page/{page_num}/"
        
        run_browser("open", url)
        time.sleep(0.5)
        run_browser("wait", "--load", "networkidle")
        
        # Check if page exists
        title = run_browser("eval", "document.title")
        if "Page not found" in title:
            break
        
        # Extract posts
        js_code = """
        JSON.stringify(
          Array.from(document.querySelectorAll('article')).map(article => {
            const titleLink = article.querySelector('h1 a, h2 a, .entry-title a');
            const dateEl = article.querySelector('time, .entry-date');
            return {
              title: titleLink ? titleLink.textContent.trim() : '',
              url: titleLink ? titleLink.href : '',
              date: dateEl ? dateEl.textContent.trim() : ''
            };
          }).filter(p => p.title && p.url)
        )
        """
        
        page_posts = eval_js(js_code)
        
        if isinstance(page_posts, list) and len(page_posts) > 0:
            all_posts.extend(page_posts)
            print(f"  Page {page_num}: {len(page_posts)} posts (total: {len(all_posts)})")
        else:
            if page_num == 1:
                print(f"  No posts found on page 1")
            break
        
        # Check for "Older posts" link
        has_next = eval_js('!!Array.from(document.querySelectorAll("a")).find(a => a.textContent.includes("Older posts"))')
        
        if not has_next:
            break
        
        page_num += 1
        if page_num > 50:  # Safety limit
            break
    
    return all_posts


def main():
    result = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "https://blog.acolyer.org",
        "categories": {}
    }
    
    total = len(TAGS)
    for i, tag_entry in enumerate(TAGS):
        tag_name, tag_slug = tag_entry.split("|", 1)
        print(f"\n[{i+1}/{total}] Scraping: {tag_name}")
        sys.stdout.flush()
        
        try:
            posts = scrape_tag(tag_name, tag_slug)
            result["categories"][tag_name] = posts
            print(f"  Total: {len(posts)} posts")
            
            # Save incrementally
            with open(DATA_FILE, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"  ERROR: {e}")
            result["categories"][tag_name] = []
    
    print(f"\nDone! Saved to {DATA_FILE}")
    print(f"Total categories: {len(result['categories'])}")
    total_posts = sum(len(v) for v in result["categories"].values())
    print(f"Total posts (with duplicates across categories): {total_posts}")


if __name__ == "__main__":
    main()
