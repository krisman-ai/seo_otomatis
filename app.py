import re
import json
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="SEO Wizard (Private)", layout="wide")
st.title("SEO Wizard (Private) — Tools SEO untuk Kamu Sendiri (Tanpa API)")

# =========================
# HELPERS
# =========================
def json_dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70]

def detect_intent(keyword: str) -> str:
    k = keyword.lower()
    trans = ["harga", "promo", "diskon", "beli", "order", "daftar", "paket", "biaya", "termurah", "best price"]
    local = ["terdekat", "jakarta", "bandung", "surabaya", "tangerang", "bekasi", "depok", "malang", "medan", "bogor"]
    commercial = ["jasa", "service", "konsultan", "vendor", "agency", "terbaik", "rekomendasi", "review"]
    howto = ["cara", "panduan", "tutorial", "contoh", "apa itu", "tips", "strategi"]

    if any(x in k for x in trans): return "transaksional"
    if any(x in k for x in local): return "lokal"
    if any(x in k for x in commercial): return "komersial"
    if any(x in k for x in howto): return "informatif"
    return "informatif"

def recommended_page(intent: str, content_type: str) -> str:
    if content_type == "landing":
        return "Landing Page"
    if intent in ["komersial", "transaksional", "lokal"]:
        return "Landing Page + Artikel Pendukung"
    return "Artikel Blog"

def build_blueprint(keyword: str, content_type: str, intent: str):
    kw = keyword.strip()

    if content_type == "landing":
        sections = [
            ("Ringkasan Layanan", ["siapa targetnya", "hasil yang realistis", "apa yang termasuk"]),
            ("Masalah yang Sering Terjadi", ["masalah 1", "masalah 2", "dampak jika dibiarkan"]),
            ("Solusi & Cara Kerja", ["step proses", "timeline", "yang dibutuhkan dari klien"]),
            ("Paket / Harga (Range)", ["paket basic/standard/premium", "range harga", "deliverables"]),
            ("Bukti & Kepercayaan", ["testimoni", "portofolio", "logo klien (jika ada)"]),
            ("FAQ", ["3–8 pertanyaan umum"]),
            ("CTA (Hubungi)", ["WA", "jam operasional", "ajakan konsultasi"]),
        ]
        faq = [
            f"Berapa lama proses {kw.lower()}?",
            "Apakah bisa menyesuaikan budget?",
            "Apa yang perlu disiapkan sebelum mulai?",
            "Bagaimana sistem revisinya?",
        ]
        cta = "Klik WhatsApp untuk konsultasi awal."
        h1 = f"{kw} — {intent.title()} | Konsultasi & Penawaran"
    else:
        sections = [
            ("Apa itu dan Kenapa Penting", ["definisi singkat", "manfaat", "siapa yang butuh"]),
            ("Kapan Kamu Harus Mulai", ["tanda-tanda butuh", "contoh kondisi", "prioritas"]),
            ("Langkah-langkah Praktis", ["step 1", "step 2", "step 3", "tools yang dipakai"]),
            ("Contoh / Template", ["contoh nyata", "template", "tips implementasi"]),
            ("Kesalahan Umum & Cara Menghindari", ["kesalahan 1", "kesalahan 2", "solusi"]),
            ("FAQ", ["3–8 pertanyaan umum"]),
            ("Kesimpulan + Next Step", ["ringkasan", "ajak tindakan"]),
        ]
        faq = [
            f"Berapa lama hasil {kw.lower()} bisa terlihat?",
            "Apa yang paling penting untuk pemula?",
            "Apakah butuh budget besar?",
            "Tool gratis apa yang bisa dipakai?",
        ]
        cta = "Kalau kamu mau, tulis tujuanmu — nanti kita rapihin jadi rencana eksekusi."
        h1 = f"Panduan {kw} (Lengkap & Praktis)"

    return {"h1": h1, "sections": sections, "faq": faq, "cta": cta}

def word_count_from_html(content_html: str) -> int:
    text = re.sub("<[^<]+?>", " ", content_html)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return 0
    return len(text.split(" "))

def seo_score(content_html: str, keyword: str, content_type: str):
    h = content_html.lower()
    text = re.sub("<[^<]+?>", " ", h)
    text = re.sub(r"\s+", " ", text).strip()
    k = keyword.lower().strip()

    checks = []
    checks.append(("Ada H1", "<h1" in h))
    checks.append(("Minimal 4 H2", h.count("<h2") >= 4))
    checks.append(("Keyword muncul di 120 kata awal", k in " ".join(text.split()[:120])))
    checks.append(("Panjang minimal 900 kata", word_count_from_html(content_html) >= 900))
    checks.append(("Ada list/bullet", ("<ul" in h) or ("<ol" in h)))
    checks.append(("Ada FAQ (atau tanda tanya)", ("faq" in text) or ("?" in content_html)))

    if content_type == "landing":
        checks.append(("Ada CTA (hubungi/wa/konsultasi)", any(x in text for x in ["hubungi", "whatsapp", "wa", "konsultasi"])))
        checks.append(("Ada harga/paket/biaya", any(x in text for x in ["harga", "paket", "biaya"])))
        checks.append(("Ada trust (testimoni/portofolio/klien)", any(x in text for x in ["testimoni", "portofolio", "klien"])))
    else:
        checks.append(("Ada langkah/cara/panduan", any(x in text for x in ["langkah", "cara", "panduan", "tutorial"])))
        checks.append(("Ada contoh", "contoh" in text))
        checks.append(("Ada kesalahan umum", any(x in text for x in ["kesalahan", "hindari", "jangan"])))

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    score = int((passed / total) * 100)
    missing = [name for name, ok in checks if not ok]
    return score, missing, checks

def build_meta(keyword: str):
    title = keyword.strip()[:65]
    desc = f"Panduan tentang {keyword.strip()} yang praktis, terstruktur, dan siap diterapkan. Lengkap dengan langkah, tips, dan contoh."
    desc = desc[:160]
    return title, desc

def faq_schema_jsonld(faqs: list[str]):
    items = []
    for q in faqs[:10]:
        items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": "Jawaban bisa disesuaikan sesuai kondisi Anda."}
        })
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items
    }

# ====== FITUR BARU: Generate Template HTML Otomatis ======
def generate_html_template(keyword: str, content_type: str, bp: dict, wa_link: str = "") -> str:
    """
    Membuat kerangka HTML siap diedit:
    - H1 + intro
    - H2 sesuai blueprint
    - bullet must_cover
    - FAQ section
    - CTA
    """
    kw = keyword.strip()
    h1 = bp.get("h1", kw)
    sections = bp.get("sections", [])
    faq = bp.get("faq", [])
    cta = bp.get("cta", "Hubungi kami untuk info lebih lanjut.")

    intro = (
        f"<p>Halaman ini membahas <b>{kw}</b> secara terstruktur sesuai kebutuhan pencarian pengguna. "
        "Silakan sesuaikan detailnya dengan layanan/brand kamu.</p>"
        if content_type == "landing"
        else
        f"<p>Di artikel ini kamu akan belajar tentang <b>{kw}</b> dengan langkah-langkah yang praktis dan mudah diterapkan.</p>"
    )

    out = []
    out.append(f"<h1>{h1}</h1>")
    out.append(intro)

    # Sections
    for h2, must_cover in sections:
        out.append(f"<h2>{h2}</h2>")
        out.append("<p><i>(Tulis penjelasan bagian ini di sini. Buat jelas, ringkas, dan relevan.)</i></p>")
        if must_cover:
            out.append("<ul>")
            for item in must_cover:
                out.append(f"<li>{item}</li>")
            out.append("</ul>")

        # mini tips for landing
        if content_type == "landing" and ("harga" in h2.lower() or "paket" in h2.lower()):
            out.append("<p><b>Catatan:</b> Tulis range harga yang wajar, jelaskan apa yang didapat, dan syaratnya jika ada.</p>")

    # FAQ
    out.append("<h2>FAQ</h2>")
    for q in faq:
        out.append(f"<h3>{q}</h3>")
        out.append("<p>Jawab singkat dan jelas (2–4 kalimat). Sesuaikan dengan layanan kamu.</p>")

    # CTA
    out.append("<h2>Konsultasi</h2>")
    out.append(f"<p>{cta}</p>")
    if wa_link.strip():
        out.append(f'<p><a href="{wa_link.strip()}">👉 Chat WhatsApp Sekarang</a></p>')
    else:
        out.append("<p><i>(Opsional) Tambahkan link WhatsApp kamu di settings.</i></p>")

    return "\n".join(out)

# =========================
# STATE
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1

def go(step: int):
    st.session_state.step = step

# =========================
# SIDEBAR NAV
# =========================
st.sidebar.header("Navigasi")
st.sidebar.write(f"Step saat ini: **{st.session_state.step}**")

st.sidebar.button("Step 1 — Keyword", on_click=go, args=(1,))
st.sidebar.button("Step 2 — Blueprint", on_click=go, args=(2,))
st.sidebar.button("Step 3 — Tulis/Edit", on_click=go, args=(3,))
st.sidebar.button("Step 4 — Skor SEO", on_click=go, args=(4,))
st.sidebar.button("Step 5 — Export", on_click=go, args=(5,))
st.sidebar.divider()

wa_link = st.sidebar.text_input("Link WhatsApp (opsional)", value=st.session_state.get("wa_link",""), placeholder="https://wa.me/62xxxxxxxxxxx")
st.session_state.wa_link = wa_link

if st.sidebar.button("Reset Semua"):
    for k in [
        "keyword","content_type","goal","platform","intent","rec_page","focus","bp",
        "draft_html","score","missing","checks","meta_title","meta_desc","slug","wa_link"
    ]:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.step = 1
    st.rerun()

# =========================
# STEP 1
# =========================
if st.session_state.step == 1:
    st.subheader("Step 1 — Keyword & Pengaturan")
    c1, c2 = st.columns([1,1])

    with c1:
        keyword = st.text_input("Keyword / Topik", value=st.session_state.get("keyword",""), placeholder="contoh: jasa SEO UMKM Jakarta")
        content_type = st.selectbox("Tipe Konten", ["blog", "landing"], index=0 if st.session_state.get("content_type","blog")=="blog" else 1)
        goal = st.selectbox("Tujuan", ["edukasi", "jual"], index=0 if st.session_state.get("goal","edukasi")=="edukasi" else 1)
        platform = st.selectbox("Platform Export", ["wordpress", "blogspot", "html"],
                                index=["wordpress","blogspot","html"].index(st.session_state.get("platform","wordpress")))

    with c2:
        st.info(
            "Tips cepat:\n"
            "- Keyword mengandung **jasa/harga/paket** → pilih **landing**.\n"
            "- Keyword mengandung **cara/panduan** → pilih **blog**.\n"
            "- Tujuan **jual** cocok untuk landing."
        )

    if st.button("Analisa Otomatis"):
        if not keyword.strip():
            st.error("Keyword wajib diisi.")
        else:
            intent = detect_intent(keyword)
            rec = recommended_page(intent, content_type)
            focus = f"Fokus konten: {keyword.strip()} sesuai intent {intent}."

            st.session_state.keyword = keyword.strip()
            st.session_state.content_type = content_type
            st.session_state.goal = goal
            st.session_state.platform = platform
            st.session_state.intent = intent
            st.session_state.rec_page = rec
            st.session_state.focus = focus
            st.success("Analisa selesai ✅")

    if "intent" in st.session_state:
        st.write("**Intent:**", st.session_state.intent)
        st.write("**Rekomendasi Halaman:**", st.session_state.rec_page)
        st.write("**Focus:**", st.session_state.focus)
        st.button("Lanjut ke Step 2", on_click=go, args=(2,))

# =========================
# STEP 2
# =========================
if st.session_state.step == 2:
    st.subheader("Step 2 — Blueprint (Kerangka SEO)")
    if "keyword" not in st.session_state:
        st.warning("Isi Step 1 dulu.")
        st.button("Ke Step 1", on_click=go, args=(1,))
    else:
        if st.button("Buat Blueprint Otomatis"):
            bp = build_blueprint(st.session_state.keyword, st.session_state.content_type, st.session_state.intent)
            st.session_state.bp = bp
            st.success("Blueprint dibuat ✅")

        if "bp" in st.session_state:
            bp = st.session_state.bp
            st.write("**H1:**", bp["h1"])
            st.write("**Sections:**")
            for i, (h2, must_cover) in enumerate(bp["sections"], 1):
                st.markdown(f"**{i}. {h2}**  \n- Must cover: {', '.join(must_cover)}")
            st.write("**FAQ:**")
            for q in bp["faq"]:
                st.write("- " + q)
            st.write("**CTA:**", bp["cta"])

            st.button("Lanjut ke Step 3", on_click=go, args=(3,))

# =========================
# STEP 3
# =========================
if st.session_state.step == 3:
    st.subheader("Step 3 — Tulis / Paste Konten (HTML)")
    if "bp" not in st.session_state:
        st.warning("Buat blueprint dulu di Step 2.")
        st.button("Ke Step 2", on_click=go, args=(2,))
    else:
        st.caption("Kamu bisa menulis manual, atau paste konten. Sekarang ada tombol untuk bikin template HTML otomatis.")
        cA, cB = st.columns([1,1])

        with cA:
            if st.button("⚡ Generate Template HTML Otomatis"):
                html_tpl = generate_html_template(
                    keyword=st.session_state.keyword,
                    content_type=st.session_state.content_type,
                    bp=st.session_state.bp,
                    wa_link=st.session_state.get("wa_link","")
                )
                st.session_state.draft_html = html_tpl
                st.success("Template HTML dibuat ✅ (silakan edit isi paragrafnya)")

        with cB:
            if st.button("🧹 Bersihkan Draft (kosongkan)"):
                st.session_state.draft_html = ""

        draft = st.text_area(
            "Konten HTML",
            value=st.session_state.get("draft_html",""),
            height=380,
            placeholder="<h1>...</h1>\n<p>...</p>\n<h2>...</h2>"
        )

        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("Simpan Draft"):
                st.session_state.draft_html = draft
                st.success("Draft tersimpan ✅")
        with c2:
            st.button("Lanjut ke Step 4", on_click=go, args=(4,))

# =========================
# STEP 4
# =========================
if st.session_state.step == 4:
    st.subheader("Step 4 — Skor SEO (Gratis)")
    if "draft_html" not in st.session_state or not st.session_state.draft_html.strip():
        st.warning("Isi draft dulu di Step 3 (bisa generate template dulu).")
        st.button("Ke Step 3", on_click=go, args=(3,))
    else:
        if st.button("Hitung Skor"):
            score, missing, checks = seo_score(
                st.session_state.draft_html,
                st.session_state.keyword,
                st.session_state.content_type
            )
            st.session_state.score = score
            st.session_state.missing = missing
            st.session_state.checks = checks
            st.success("Skor dihitung ✅")

        if "score" in st.session_state:
            st.metric("Skor SEO", st.session_state.score)
            st.write(f"Perkiraan jumlah kata: **{word_count_from_html(st.session_state.draft_html)}**")

            st.write("Checklist:")
            for name, ok in st.session_state.checks:
                st.write(("✅ " if ok else "❌ ") + name)

            if st.session_state.missing:
                st.warning("Yang perlu dibenahi:")
                for m in st.session_state.missing:
                    st.write("- " + m)
            else:
                st.success("Checklist dasar terpenuhi. Mantap.")

            st.button("Lanjut ke Step 5", on_click=go, args=(5,))

# =========================
# STEP 5
# =========================
if st.session_state.step == 5:
    st.subheader("Step 5 — Export (WordPress / Blogspot / HTML)")
    if "draft_html" not in st.session_state or not st.session_state.draft_html.strip():
        st.warning("Isi draft dulu di Step 3.")
        st.button("Ke Step 3", on_click=go, args=(3,))
    else:
        meta_title, meta_desc = build_meta(st.session_state.keyword)
        slug = slugify(st.session_state.keyword)

        st.write("**Meta Title:**", meta_title)
        st.write("**Meta Description:**", meta_desc)
        st.write("**Slug:**", slug)

        st.download_button(
            "⬇️ Download HTML",
            data=st.session_state.draft_html,
            file_name=f"{slug}.html",
            mime="text/html",
        )

        # Schema FAQ from blueprint
        faq_list = st.session_state.bp.get("faq", []) if "bp" in st.session_state else []
        if faq_list:
            st.write("### Schema FAQ (JSON-LD) — Copy ke WordPress (blok Custom HTML di bawah konten)")
            schema = faq_schema_jsonld(faq_list)
            st.code(
                '<script type="application/ld+json">\n' + json_dump(schema) + "\n</script>",
                language="html"
            )

        st.info("Untuk WordPress: paste HTML konten ke blok **Custom HTML** atau editor yang mendukung HTML. Meta Title/Description isi di Yoast/RankMath.")
