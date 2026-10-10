"""يقرأ ملف الإكسل (شيت HOM) ويطلّع data.json للداشبورد.
الاستخدام:  python convert.py "مسار ملف الإكسل.xlsx" data.json
"""
import sys, os, json, datetime as dt
import openpyxl, pandas as pd

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "data.json"

wb = openpyxl.load_workbook(src, data_only=True, read_only=True)
SHEETS = [("HOM", "هوم"), ("HOM 36 ", "A36")]
frames = []
for sh, pname in SHEETS:
    rows = list(wb[sh].iter_rows(min_row=3, values_only=True, max_col=37))
    f = pd.DataFrame(rows[1:], columns=[str(c).strip() for c in rows[0]])
    f = f.loc[:, ~f.columns.duplicated()]
    f["project"] = pname
    frames.append(f)
df = pd.concat(frames, ignore_index=True)

for c in ["تاريخ السداد", "تاريخ التعاقد", "تاريخ الشيك"]:
    df[c] = pd.to_datetime(df[c], errors="coerce")
for c in ["المحصل", "المتبقى", "القيمة", "اجمالى الوحدة", "دفعه التعاقد", "مساحه الوحده"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

def ym(s): return s.dt.strftime("%Y-%m")
def clean(v): return None if pd.isna(v) else v
def system(v):
    if v is None or pd.isna(v) or v == 0: return "بدون"
    if isinstance(v, str): return v.strip()
    return f"{v*100:g}%" if v < 1 else f"{v:g}%"

# لو القسط مسدّد وتاريخ السداد ناقص نستخدم تاريخ الشيك بدل ما نخسر المبلغ
miss = df["تاريخ السداد"].isna() & (df["المحصل"] > 0)
df["تاريخ السداد"] = df["تاريخ السداد"].fillna(df["تاريخ الشيك"].where(miss))
print("صفوف مسددة بدون تاريخ سداد:", int(miss.sum()))

# ---- 1) المتحصل من الأقساط (حسب تاريخ السداد)
inst_types = ["قسط", "قسط0", "صيانة", "جراج"]
a = df[df["نوع الدفعة"].isin(inst_types) & (df["المحصل"] > 0) & df["تاريخ السداد"].notna()].copy()
a["m"] = ym(a["تاريخ السداد"])
installments = []
for _, r in a.iterrows():
    installments.append(dict(p=r["project"], m=r["m"], date=r["تاريخ السداد"].strftime("%Y-%m-%d"), unit=clean(r["عمارة شقة"]),
        kind=r["نوع الدفعة"], method=clean(r["نوع السداد"]) or "-",
        bank=(clean(r["البنك المحصل به"]) or "غير محدد").strip(),
        zero=str(r["نظام التعاقد"]).strip() == "صفر%", amount=float(r["المحصل"])))

# المستحق (المتبقي) لكل شهر استحقاق - للتوقع
d = df[df["نوع الدفعة"].isin(inst_types) & (df["المتبقى"] > 0) & df["تاريخ الشيك"].notna()].copy()
d["m"] = ym(d["تاريخ الشيك"])
due = [dict(p=p, m=m, v=round(float(v), 2)) for (p, m), v in d.groupby(["project", "m"])["المتبقى"].sum().items()]

# ---- 2) المبيعات (حسب تاريخ التعاقد)
s = df[(df["نوع الدفعة"] == "اجمالي الوحده") & df["تاريخ التعاقد"].notna()].copy()
s["m"] = ym(s["تاريخ التعاقد"])
sales = [dict(p=r["project"], m=r["m"], date=r["تاريخ التعاقد"].strftime("%Y-%m-%d"), unit=clean(r["عمارة شقة"]),
              building=clean(r["عمارة"]), system=system(r["نظام التعاقد"]),
              area=clean(r["مساحه الوحده"]), value=float(r["اجمالى الوحدة"] or 0))
         for _, r in s.iterrows()]

# ---- 3) دفعات التعاقد (حسب تاريخ السداد)
c = df[(df["نوع الدفعة"] == "مقدم تعاقد") & (df["المحصل"] > 0) & df["تاريخ السداد"].notna()].copy()
c["m"] = ym(c["تاريخ السداد"])
downs = [dict(p=r["project"], m=r["m"], date=r["تاريخ السداد"].strftime("%Y-%m-%d"), unit=clean(r["عمارة شقة"]),
              bank=(clean(r["البنك المحصل به"]) or "غير محدد").strip(), amount=float(r["المحصل"]))
         for _, r in c.iterrows()]
pend = df[(df["نوع الدفعة"] == "مقدم تعاقد") & (df["المتبقى"] > 0)]["المتبقى"].sum()

json.dump(dict(updated=(open("modified.txt").read().strip() if os.path.exists("modified.txt") else dt.datetime.fromtimestamp(os.path.getmtime(src)).strftime("%Y-%m-%d %H:%M")), installments=installments, due=due,
               sales=sales, downs=downs, downs_pending=float(pend)),
          open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("OK", len(installments), len(sales), len(downs), "->", out)
