# -*- coding: utf-8 -*-
"""بيانات تاب الشركاء: كشوف المصروفات + نسبة زايا التجميعية، مع تشفير بكلمة سر."""
import re, json, base64, hashlib, hmac, os

NUM = (int, float)

def _txt(v):
    return re.sub(r"\s+", " ", v).strip() if isinstance(v, str) else None

# ---------------- تصنيف المصاريف (عدّل الكلمات هنا لو احتجت) ----------------
CATS = [
    ("شراء قسط الأرض",        ["الارض", "الأرض"]),
    ("استشاري ومكاتب هندسية", ["رينو", "صبور", "استشار"]),
    ("غفرة وأمن",             ["الغفر"]),
    ("مكتب المبيعات والتسويق", ["sales", "سيلز", "يفط", "اعلام"]),
    ("إقامة وتسكين",          ["الفندق", "التسكين", "السياحه"]),
    ("استرداد للعملاء",       ["استرداد"]),
    ("مصروفات الجهاز والمرافق", ["الجهاز", "المياه"]),
    ("مبالغ مسلّمة للأفراد (عهد وتحويلات)", ["عبدالله", "عبد الله", "ممدوح", "محمود اسماعيل", "الدبيحه", "مازن", "التسعير", "رحمي"]),
]
def categorize(name):
    n = (name or "").lower()
    for cat, keys in CATS:
        if any(k.lower() in n for k in keys): return cat
    return "أخرى"

def _date(s):
    m = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})", s or "")
    return (int(m.group(3)), int(m.group(2))) if m else None

def parse_expenses(ws):
    stmts, cur = [], None
    for row in ws.iter_rows(values_only=True, max_col=5):
        a, b, c, d, e = (list(row) + [None] * 5)[:5]
        if isinstance(b, str) and "المصروفات كشف رقم" in b:
            n = int(re.search(r"\(\s*(\d+)\s*\)", b).group(1))
            ds = re.findall(r"\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{4}", b)
            if ds: ym = _date(ds[0]); m = f"{ym[0]}-{ym[1]:02d}"
            else:  m = "2026-03"        # الكشف 1 بدون تاريخ = حتى 31/3/2026
            cur = dict(n=n, m=m, title=_txt(b), items=[], total=None); continue
        if cur is None: continue
        if _txt(a) == "الاجمالي":
            cur["total"] = dict(total=c or 0, paid=d or 0, rem=e or 0); stmts.append(cur); cur = None; continue
        if isinstance(a, NUM) and _txt(b):
            if not any(isinstance(x, NUM) and x for x in (c, d, e)): continue
            name = _txt(b)
            cur["items"].append(dict(i=int(a), name=name, total=float(c or 0), paid=float(d or 0), rem=float(e or 0), cat=categorize(name)))
    for s in stmts:
        s["paid"] = sum(i["paid"] for i in s["items"])
        s["check"] = abs(s["paid"] - float(s["total"]["paid"] or 0)) < 1
    return stmts

def parse_zaya(ws):
    """تجميعي نسبة زايا من شيت تقفيل شركاء: لكل شهر (تعاقدات + نسبة زايا + بنودها)."""
    months, cur, mode = [], None, None
    for row in ws.iter_rows(values_only=True, max_col=6):
        a, b, c, d, e, f = (list(row) + [None] * 6)[:6]
        if isinstance(a, str) and "كشف تفصيلي مشروع" in a:
            ym = _date(a)
            if not ym: cur = None; continue
            cur = dict(m=f"{ym[0]}-{ym[1]:02d}", contracts=0.0, downs=0.0, units=0, zaya=0.0, items=[]); months.append(cur); mode = "sales"; continue
        if cur is None: continue
        if _txt(b) and "تسويه نسبه شركه زايا" in _txt(b): mode = "zaya"; continue
        if _txt(b) and "تسويه حساب المشروع في البنك" in _txt(b) or (_txt(a) and "تسويه حساب المشروع في البنك" in _txt(a)): mode = "done"; continue
        if mode == "sales" and _txt(c) == "الرصيد":
            cur["contracts"] = float(b or 0); cur["downs"] = float(d or 0); cur["units"] = int(e or 0)
        elif mode == "zaya":
            if isinstance(b, NUM) and isinstance(c, NUM) and _txt(d):
                cur["items"].append(dict(name=_txt(d), amount=float(c)))
            elif b is None and isinstance(c, NUM) and _txt(d) and _txt(d).startswith("نسبه شركه زايا"):
                cur["zaya"] = float(c); mode = "done"
    return [m for m in months if m["contracts"] or m["zaya"]]

def build_partners(wb):
    out = {"exp": parse_expenses(wb["كشوف مصروفات"]), "zaya": parse_zaya(wb["تقفيل شركاء"])}
    return out

