# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 15:49:10 2026

@author: vzocc
"""

"""
FTP recursive mapper + exporters (buffered + progress)
"""

import ftplib
import json

FTP_HOST = "ftp.deepneural.net"

with open("C:\\Users\\vzocc\\pass.json") as f:
    config = json.load(f)

FTP_USER = config["FTP_USER"]
FTP_PASS = config["FTP_PASS"]


# ─────────────────────────────────────────────
# FTP CONNECT
# ─────────────────────────────────────────────

def connect_ftp():
    print(f"🌐 Connecting to FTP: {FTP_HOST} ...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("✔ Connected.\n")
    return ftp


# ─────────────────────────────────────────────
# TREE BUILD
# ─────────────────────────────────────────────

def build_tree(paths):
    tree = {}

    for path in paths:
        parts = path.strip("/").split("/")
        node = tree

        for p in parts:
            node = node.setdefault(p, {})

    return tree


# ─────────────────────────────────────────────
# EXPORTERS
# ─────────────────────────────────────────────

def export_json(paths, filename="tree.json"):
    tree = build_tree(paths)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)

    return tree


def export_ascii(paths, filename="tree.txt"):
    tree = build_tree(paths)

    def walk(node, indent=0, f=None):
        for key in sorted(node.keys()):
            line = "  " * indent + key
            print(line)
            if f:
                f.write(line + "\n")
            walk(node[key], indent + 1, f)

    with open(filename, "w", encoding="utf-8") as f:
        walk(tree, f=f)

    return tree


def export_html(paths, filename="tree.html"):
    tree = build_tree(paths)

    def to_html(node):
        html = "<ul>"
        for key in sorted(node.keys()):
            html += f"<li>{key}"
            if node[key]:
                html += to_html(node[key])
            html += "</li>"
        html += "</ul>"
        return html

    html_output = f"""
<html>
<head>
<style>
ul {{ font-family: Arial; }}
li {{ margin: 4px; }}
</style>
</head>
<body>
{to_html(tree)}
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_output)

    return tree


# ─────────────────────────────────────────────
# FTP WALK (WITH PROGRESS)
# ─────────────────────────────────────────────

processed = 0

def walk(ftp, path, indent=0, buffer=None):
    global processed
    results = []

    try:
        items = ftp.nlst(path)
    except Exception as e:
        print(f"Error listing {path}: {e}")
        return results

    for item in items:
        processed += 1

        if processed % 50 == 0:
            print(f"[PROGRESS] Processed {processed} items | current: {path}")

        if "/deepneural.net/wordpress" in item:
            continue

        if item.endswith("/.") or item.endswith("/.."):
            continue

        name = item.split("/")[-1]

        line = "  " * indent + name

        if buffer is not None:
            buffer.append(line)

        try:
            ftp.cwd(item)
            ftp.cwd("..")

            results.append(item)
            results.extend(walk(ftp, item, indent + 1, buffer))

        except:
            results.append(item)

    return results


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

ftp = connect_ftp()
ftp.encoding = "latin-1"

buffer = []

all_items = walk(ftp, "/deepneural.net", buffer=buffer)

with open("ftp_map.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(buffer))

export_json(all_items)
export_ascii(all_items)
export_html(all_items)

ftp.quit()