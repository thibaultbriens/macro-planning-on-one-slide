# app.py
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
from collections import defaultdict
import io
import json
import shelve
import os

st.set_page_config(
    page_title="Roadmap Builder",
    page_icon="🗺️",
    layout="wide"
)

# ─────────────────────────────────────────────
#  PERSISTANCE
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "roadmap_data")

def db_load(key, default):
    with shelve.open(DB_PATH) as db:
        return db.get(key, default)

def db_save(key, value):
    with shelve.open(DB_PATH) as db:
        db[key] = value

def db_save_all(data: dict):
    with shelve.open(DB_PATH) as db:
        for k, v in data.items():
            db[k] = v

def db_load_all(keys_defaults: dict) -> dict:
    result = {}
    with shelve.open(DB_PATH) as db:
        for k, default in keys_defaults.items():
            result[k] = db.get(k, default)
    return result

# ─────────────────────────────────────────────
#  COULEURS
# ─────────────────────────────────────────────
C_BG        = '#F5F6FA'
C_HEADER    = '#E8EAF0'
C_DONE      = '#27AE60'
C_INPROG    = '#E67E22'
C_RECUR     = '#2980B9'
C_TODO      = '#D0D3DE'
C_VACANCES  = '#E67E22'
C_TEXT      = '#1A1A2E'
C_SUBTEXT   = '#6B7280'
C_BORDER    = '#C8CBDA'
C_JALON     = '#8E44AD'
C_ROW_ALT   = '#ECEEF5'

C_PHASE_CONCEPTION = '#27AE60'
C_PHASE_DEV        = '#E74C3C'
C_PHASE_TEST       = '#2980B9'
C_PHASE_RA        = '#8E44AD'
C_PHASE_INFRA      = '#D35400'
C_PHASE_ANALYSE    = '#16A085'

PHASES = {
    "conception": ("CNCPT", C_PHASE_CONCEPTION),
    "dev":        ("DEV",   C_PHASE_DEV),
    "test":       ("TEST",  C_PHASE_TEST),
    "ra":         ("R&A",    C_PHASE_RA),
    "infra":      ("INFRA", C_PHASE_INFRA),
    "analyse":    ("ANAL",  C_PHASE_ANALYSE),
}
PHASE_KEYS = list(PHASES.keys())

STATUT_VALS = {
    "—  Inactif":  None,
    "À venir":     0,
    "En cours":    0.3,
    "Récurrent":   0.5,
    "Terminé":     1,
}
STATUT_KEYS = list(STATUT_VALS.keys())

STATUT_COLOR = {
    0:   '#B0B5C8',
    0.3: C_INPROG,
    0.5: C_RECUR,
    1:   C_DONE,
}

# ─────────────────────────────────────────────
#  DONNÉES PAR DÉFAUT
# ─────────────────────────────────────────────
DEFAULT_SPRINTS = [
    {"label": "S1",      "dates": "S11-S14"},
    {"label": "S2",      "dates": "S15-S18"},
    {"label": "S3",      "dates": "S20-S23"},
    {"label": "S4",      "dates": "S24-S27"},
    {"label": "S5",      "dates": "S28-S31"},
    {"label": "S6",      "dates": "S32-S35"},
    {"label": "S7-S9",   "dates": "S36-S44"},
    {"label": "S10-S11", "dates": "S45-S51"},
]

DEFAULT_CHANTIERS = [
    {"name": "Refonte UX/UI", "charge": "3 Dev",
     "livrable": "Page home\n+ header",
     "description": "",
     "jalon_label": "UI valide client", "jalon_sprint": 2,
     "progress": [(1,"dev"),(1,"dev"),(0.3,"test"),(0,"test"),(None,"dev"),(None,"dev"),(None,"dev"),(None,"dev")]},
    {"name": "Resolution dependances", "charge": "1 Dev",
     "livrable": "0 Critical/High",
     "description": "",
     "jalon_label": "0 issues Dependabot", "jalon_sprint": 1,
     "progress": [(1,"analyse"),(0.3,"dev"),(0,"test"),(None,"test"),(None,"test"),(None,"test"),(None,"test"),(None,"test")]},
    {"name": "Infra / Octo 3.0", "charge": "2 Ops",
     "livrable": "Env. staging\noperationnel",
     "description": "",
     "jalon_label": "Env. prod OK", "jalon_sprint": 2,
     "progress": [(1,"infra"),(1,"infra"),(0.3,"infra"),(0,"infra"),(None,"test"),(None,"test"),(None,"ra"),(None,"ra")]},
    {"name": "Reduction couts infra", "charge": "2 Ops",
     "livrable": "-26% couts\nobserves",
     "description": "",
     "jalon_label": "-26% couts infra", "jalon_sprint": 7,
     "progress": [(None,"analyse"),(1,"infra"),(0.5,"infra"),(0.5,"infra"),(0.5,"infra"),(0.5,"infra"),(0.5,"infra"),(0.5,"infra")]},
    {"name": "Recherche par contenu", "charge": "2 Dev",
     "livrable": "Plan valide\nclient",
     "description": "",
     "jalon_label": "Algo recherche OK", "jalon_sprint": 3,
     "progress": [(None,"conception"),(0.3,"conception"),(0.3,"dev"),(0.3,"dev"),(0,"test"),(0,"test"),(None,"ra"),(None,"ra")]},
    {"name": "Publication auto live", "charge": "1 Dev",
     "livrable": "--",
     "description": "",
     "jalon_label": "Publication auto", "jalon_sprint": 4,
     "progress": [(None,"conception"),(None,"conception"),(0,"dev"),(0.3,"dev"),(0.3,"dev"),(0,"test"),(None,"test"),(None,"ra")]},
    {"name": "Sous-titres auto", "charge": "1 Dev",
     "livrable": "--",
     "description": "",
     "jalon_label": "Sous-titres front+DB", "jalon_sprint": 5,
     "progress": [(None,"conception"),(None,"conception"),(None,"dev"),(0,"dev"),(0.3,"dev"),(0.3,"dev"),(0,"test"),(None,"test")]},
    {"name": "IaC / Terraform", "charge": "2 Ops",
     "livrable": "--",
     "description": "",
     "jalon_label": "SFU via Terraform", "jalon_sprint": 7,
     "progress": [(None,"conception"),(None,"conception"),(None,"infra"),(0,"infra"),(0,"infra"),(0.3,"infra"),(0.3,"infra"),(0.3,"infra")]},
]

DEFAULTS = {
    "sprints":                DEFAULT_SPRINTS,
    "chantiers":              [{**c, "progress": list(c["progress"])} for c in DEFAULT_CHANTIERS],
    "current_sprint":         1,
    "titre":                  "ROADMAP  -  Vue d'ensemble projet",
    "maj_date":               "30/04/2026",
    "sprint_progress":        78,
    "sprint_progress_label":  "SPRINT 2",
    "capacite":               "Max : 4 Dev / 2 Ops / semaine",
    "vacances_sprint":        2,
    "vacances_label":         "Vacances S19",
    "show_vacances":          True,
}

# ─────────────────────────────────────────────
#  INIT SESSION STATE (depuis DB ou défauts)
# ─────────────────────────────────────────────
if "initialized" not in st.session_state:
    loaded = db_load_all(DEFAULTS)
    for k, v in loaded.items():
        st.session_state[k] = v
    st.session_state.initialized = True

# ─────────────────────────────────────────────
#  SAUVEGARDE AUTO (appelée avant chaque rerun)
# ─────────────────────────────────────────────
def persist():
    """Sauvegarde tout l'état courant dans shelve."""
    db_save_all({k: st.session_state[k] for k in DEFAULTS.keys()})

# ─────────────────────────────────────────────
#  GÉNÉRATION ROADMAP
# ─────────────────────────────────────────────
def generate_roadmap(sprints, chantiers, current_sprint, titre, maj_date,
                     sprint_progress, sprint_progress_label, capacite,
                     show_vacances, vacances_sprint, vacances_label):

    plt.rcParams['font.family'] = 'DejaVu Sans'

    n_sp  = len(sprints)
    n_ch  = len(chantiers)

    x_name    = 0.15
    w_name    = 4.30
    x_charge  = 4.55
    w_charge  = 0.85
    x_start   = 5.50
    col_w     = 1.50
    row_h     = 0.88
    header_h  = 0.62

    y_top     = 12.20
    x_liv     = x_start + col_w * n_sp + 0.20
    w_liv     = 2.70
    x_right   = x_liv + w_liv

    fig_h = y_top + 1.30
    fig_w = x_right + 0.35

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')
    fig.patch.set_facecolor(C_BG)

    grid_h     = n_ch * row_h
    y_grid_bot = y_top - header_h - grid_h

    ax.add_patch(FancyBboxPatch(
        (0.10, y_grid_bot), x_right - 0.20, header_h + grid_h,
        boxstyle="square,pad=0", facecolor='#FFFFFF',
        edgecolor=C_BORDER, linewidth=0.8, zorder=1))

    y_title = y_top + 0.70
    ax.text(x_right / 2, y_title, titre,
            ha='center', va='center', fontsize=18,
            fontweight='bold', color=C_TEXT)
    ax.text(x_right - 0.10, y_title, f"MAJ : {maj_date}",
            ha='right', va='center', fontsize=9, color=C_SUBTEXT)

    def header_box(x, w, label, sublabel=None,
                   fc=C_HEADER, tc=C_TEXT, border=C_BORDER, lw=0.8):
        ax.add_patch(FancyBboxPatch(
            (x + 0.04, y_top - header_h + 0.04), w - 0.08, header_h - 0.08,
            boxstyle="round,pad=0.03",
            facecolor=fc, edgecolor=border, linewidth=lw, zorder=2))
        if sublabel:
            ax.text(x + w/2, y_top - header_h/2 + 0.10, label,
                    ha='center', va='center', fontsize=10,
                    fontweight='bold', color=tc, zorder=3)
            ax.text(x + w/2, y_top - header_h/2 - 0.13, sublabel,
                    ha='center', va='center', fontsize=7.5,
                    color=C_SUBTEXT, zorder=3)
        else:
            ax.text(x + w/2, y_top - header_h/2, label,
                    ha='center', va='center', fontsize=10,
                    fontweight='bold', color=tc, zorder=3)

    header_box(x_name,   w_name,   "Chantier")
    header_box(x_charge, w_charge, "Charge")

    for j, sp in enumerate(sprints):
        x = x_start + j * col_w
        header_box(x, col_w, sp["label"], sp["dates"],
                   tc=C_DONE if j == current_sprint else C_TEXT)

    ax.add_patch(FancyBboxPatch(
        (x_liv + 0.04, y_top - header_h + 0.04), w_liv - 0.08, header_h - 0.08,
        boxstyle="round,pad=0.03",
        facecolor='#EAF9EF', edgecolor=C_DONE, linewidth=1.5, zorder=2))
    ax.text(x_liv + w_liv/2, y_top - header_h/2,
            "Livrable S2", ha='center', va='center',
            fontsize=10, fontweight='bold', color=C_DONE, zorder=3)

    for i in range(n_ch):
        y  = y_top - header_h - (i + 1) * row_h
        bg = C_ROW_ALT if i % 2 == 0 else '#FFFFFF'
        ax.add_patch(FancyBboxPatch(
            (0.10, y + 0.03), x_right - 0.20, row_h - 0.06,
            boxstyle="square,pad=0", facecolor=bg,
            edgecolor='none', zorder=2))
        ax.plot([0.10, x_right - 0.10], [y + row_h, y + row_h],
                color=C_BORDER, lw=0.5, alpha=0.6, zorder=2)

    if 0 <= current_sprint < n_sp:
        x_cur     = x_start + current_sprint * col_w
        y_cur_bot = y_grid_bot
        y_cur_top = y_top - header_h
        ax.add_patch(FancyBboxPatch(
            (x_cur + 0.02, y_cur_bot + 0.02),
            col_w - 0.04, (y_cur_top - y_cur_bot - 0.04),
            boxstyle="round,pad=0.03",
            facecolor='#EAF9EF', edgecolor=C_DONE,
            linewidth=2.2, zorder=3))

    def draw_cell(x, y, val, phase_key):
        if val is None:
            return
        if phase_key not in PHASES:
            phase_key = "dev"
        phase_label, phase_color = PHASES[phase_key]
        statut_color = STATUT_COLOR.get(val, '#B0B5C8')
        alpha = 0.22 if val == 0 else 0.75

        ax.add_patch(FancyBboxPatch(
            (x + 0.09, y + 0.11), col_w - 0.18, row_h - 0.22,
            boxstyle="round,pad=0.04",
            facecolor=phase_color, edgecolor='none',
            alpha=alpha, zorder=4))

        txt_col = '#FFFFFF' if val != 0 else C_SUBTEXT
        ax.text(x + col_w/2, y + row_h/2 + 0.05, phase_label,
                ha='center', va='center', fontsize=7,
                fontweight='bold', color=txt_col,
                alpha=0.95 if val != 0 else 0.40, zorder=5)

        if val != 0:
            cx, cy = x + col_w - 0.27, y + 0.26
            ax.add_patch(Circle((cx, cy), 0.12, color=statut_color, zorder=6))
            ax.add_patch(Circle((cx, cy), 0.12, fill=False,
                                edgecolor='white', linewidth=0.8, zorder=7))

    for i, ch in enumerate(chantiers):
        y = y_top - header_h - (i + 1) * row_h

        desc = (ch.get("description", "") or "").strip()
        name_y = y + row_h/2 + (0.10 if desc else 0.0)
        ax.text(x_name + 0.15, name_y, ch["name"],
            ha='left', va='center', fontsize=9.5,
            fontweight='bold', color=C_TEXT, zorder=4)
        if desc:
            ax.text(x_name + 0.15, y + row_h/2 - 0.18, desc,
                ha='left', va='center', fontsize=7.6,
                color=C_SUBTEXT, zorder=4)
        ax.text(x_charge + w_charge/2, y + row_h/2, ch["charge"],
                ha='center', va='center', fontsize=9,
                color=C_SUBTEXT, zorder=4)

        prog = ch.get("progress", [])
        for j in range(n_sp):
            if j < len(prog):
                val, phase = prog[j]
            else:
                val, phase = None, "dev"
            draw_cell(x_start + j * col_w, y, val, phase)

        liv   = ch.get("livrable", "--")
        empty = liv.strip() in ("", "--")
        ax.add_patch(FancyBboxPatch(
            (x_liv + 0.08, y + 0.11), w_liv - 0.16, row_h - 0.22,
            boxstyle="round,pad=0.04",
            facecolor='#EAF9EF' if not empty else C_ROW_ALT,
            edgecolor=C_DONE    if not empty else C_BORDER,
            linewidth=0.8, zorder=4))
        lines = liv.split('\n')
        for li, line in enumerate(lines):
            off = 0.13 if len(lines) > 1 else 0
            ax.text(x_liv + w_liv/2, y + row_h/2 + off - li * 0.26, line,
                    ha='center', va='center', fontsize=8.5,
                    color=C_DONE if not empty else C_SUBTEXT,
                    fontweight='bold' if not empty else 'normal', zorder=5)

    y_jal = y_grid_bot - 1.52
    jal_h = 1.48

    ax.add_patch(FancyBboxPatch(
        (0.10, y_jal), x_right - 0.20, jal_h,
        boxstyle="round,pad=0.04",
        facecolor='#FAF5FF', edgecolor='#D7BEF0', linewidth=0.8))
    ax.text(0.35, y_jal + jal_h - 0.22, "LIVRABLES FINAUX PAR CHANTIER",
            ha='left', va='center', fontsize=11,
            fontweight='bold', color=C_JALON)

    y_line = y_jal + 0.60
    ax.plot([x_start - 0.1, x_start + n_sp * col_w + 0.1],
            [y_line, y_line], color=C_JALON, lw=1.2, alpha=0.35)

    groups = defaultdict(list)
    for ch in chantiers:
        groups[ch["jalon_sprint"]].append(ch["jalon_label"])

    sorted_sp_idx = sorted(groups.keys())
    positions     = {s: (i % 2 == 0) for i, s in enumerate(sorted_sp_idx)}

    for sprint_idx, labels in groups.items():
        if sprint_idx >= n_sp:
            continue
        x_j      = x_start + sprint_idx * col_w + col_w / 2
        combined = " + ".join(labels)
        go_above = positions[sprint_idx]
        y_tick   = y_line + 0.27 if go_above else y_line - 0.25
        ax.plot([x_j, x_j], [y_line, y_tick], color=C_JALON, lw=1.8, alpha=0.9)
        ax.plot(x_j, y_tick, 'o', color=C_JALON, markersize=7)
        y_text = y_line + 0.48 if go_above else y_line - 0.44
        bw     = min(len(combined) * 0.088 + 0.4, 4.2)
        ax.add_patch(FancyBboxPatch(
            (x_j - bw/2, y_text - 0.17), bw, 0.30,
            boxstyle="round,pad=0.05",
            facecolor=C_JALON, edgecolor='none', alpha=0.15))
        ax.text(x_j, y_text, combined,
                ha='center', va='center', fontsize=8,
                color=C_JALON, fontweight='bold')

    if show_vacances and 0 <= vacances_sprint < n_sp:
        x_vac = x_start + vacances_sprint * col_w
        ax.add_patch(FancyBboxPatch(
            (x_vac + 0.05, y_line - 0.01), col_w - 0.10, 0.22,
            boxstyle="round,pad=0.04",
            facecolor=C_VACANCES, edgecolor='none', alpha=0.75))
        ax.text(x_vac + col_w/2, y_line + 0.10, vacances_label,
                ha='center', va='center', fontsize=8,
                color='#FFFFFF', fontweight='bold')

    y_bot = y_jal - 0.76
    ax.add_patch(FancyBboxPatch(
        (0.10, y_bot), x_right - 0.20, 0.68,
        boxstyle="round,pad=0.05",
        facecolor=C_HEADER, edgecolor=C_BORDER, linewidth=1))

    ax.text(0.40, y_bot + 0.50, f"{sprint_progress_label} :",
            ha='left', va='center', fontsize=9.5,
            fontweight='bold', color=C_TEXT)
    ax.text(0.40 + len(sprint_progress_label) * 0.18 + 0.30,
            y_bot + 0.50, f"{sprint_progress}%",
            ha='left', va='center', fontsize=10,
            fontweight='bold', color=C_DONE)

    bx, by, bw2, bh = 0.40, y_bot + 0.09, 4.20, 0.24
    ax.add_patch(FancyBboxPatch(
        (bx, by), bw2, bh,
        boxstyle="round,pad=0.02", facecolor=C_TODO, edgecolor='none'))
    ax.add_patch(FancyBboxPatch(
        (bx, by), bw2 * (sprint_progress / 100), bh,
        boxstyle="round,pad=0.02", facecolor=C_DONE,
        edgecolor='none', alpha=0.9))

    x_leg = bx + bw2 + 0.60
    legend_gap = 1.35
    statut_items = [
        (C_DONE,    "OK"),
        (C_INPROG,  "WIP"),
        (C_RECUR,   "REC"),
        ('#B0B5C8', "A venir"),
    ]
    for k, (color, label) in enumerate(statut_items):
        xl = x_leg + k * legend_gap
        ax.add_patch(Circle((xl + 0.12, y_bot + 0.50), 0.10, color=color))
        ax.add_patch(Circle((xl + 0.12, y_bot + 0.50), 0.10, fill=False,
                            edgecolor='white', linewidth=0.8))
        ax.text(xl + 0.28, y_bot + 0.50, label,
                ha='left', va='center', fontsize=8.5, color=C_TEXT)

    x_sep = x_leg + len(statut_items) * legend_gap + 0.15
    ax.plot([x_sep, x_sep], [y_bot + 0.08, y_bot + 0.60],
            color=C_BORDER, lw=1.2, alpha=0.7)

    phase_items = [
        (C_PHASE_CONCEPTION, "Conception"),
        (C_PHASE_DEV,        "Dev"),
        (C_PHASE_TEST,       "Test"),
        (C_PHASE_RA,        "Recettes &\nAjustements"),
        (C_PHASE_INFRA,      "Infra"),
        (C_PHASE_ANALYSE,    "Analyse"),
    ]
    x_ph = x_sep + 0.30
    phase_gap = 1.35
    for k, (color, label) in enumerate(phase_items):
        xl = x_ph + k * phase_gap
        ax.add_patch(FancyBboxPatch(
            (xl, y_bot + 0.09), 0.22, 0.22,
            boxstyle="round,pad=0.03",
            facecolor=color, edgecolor='none', alpha=0.85))
        ax.text(xl + 0.30, y_bot + 0.20, label,
                ha='left', va='center', fontsize=8.5, color=C_TEXT)

    ax.text(x_right - 0.15, y_bot + 0.50, capacite,
            ha='right', va='center', fontsize=8.5, color=C_SUBTEXT)

    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=180, bbox_inches='tight',
                facecolor=C_BG, edgecolor='none')
    plt.close()
    buf.seek(0)
    return buf

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #F5F6FA; color: #1A1A2E; }
    .block-container { padding-top: 1rem; }
    .section-title {
        font-size: 1.05rem; font-weight: 700; color: #4A4A6A;
        margin: 0.8rem 0 0.4rem 0;
        border-left: 4px solid #8E44AD; padding-left: 9px;
    }
    .save-badge {
        display: inline-block; background: #EAF9EF;
        color: #27AE60; border: 1px solid #27AE60;
        border-radius: 12px; padding: 2px 12px;
        font-size: 0.82rem; font-weight: 600; margin-bottom: 6px;
    }
    .stButton > button {
        background-color: #27AE60; color: #FFFFFF;
        font-weight: bold; border: none; border-radius: 8px;
        padding: 0.45rem 1.4rem;
    }
    .stButton > button:hover { background-color: #1E8449; }
    .stDownloadButton > button {
        background-color: #2980B9; color: #FFFFFF;
        font-weight: bold; border: none; border-radius: 8px;
    }
    .stDownloadButton > button:hover { background-color: #1F618D; }
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #D0D3DE; border-radius: 8px;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        background-color: #FFFFFF; color: #1A1A2E;
        border: 1px solid #C8CBDA; border-radius: 6px;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF; border: 1px solid #C8CBDA; color: #1A1A2E;
    }
    hr { border-color: #D0D3DE; }
    label { color: #4A4A6A !important; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("# 🗺️ Roadmap Builder")
st.markdown("Personnalisez vos chantiers, sprints et livrables, puis générez votre roadmap.")

# Indicateur de sauvegarde
db_exists = os.path.exists(DB_PATH + ".db") or os.path.exists(DB_PATH + ".dir")
if db_exists:
    st.markdown('<span class="save-badge">💾 Données sauvegardées localement</span>',
                unsafe_allow_html=True)

st.divider()

col_left, col_right = st.columns([1, 2], gap="large")

with col_left:

    st.markdown('<div class="section-title">⚙️ Informations générales</div>',
                unsafe_allow_html=True)

    titre = st.text_input("Titre", value=st.session_state.titre)
    if titre != st.session_state.titre:
        st.session_state.titre = titre; persist()

    maj_date = st.text_input("Date de mise à jour", value=st.session_state.maj_date)
    if maj_date != st.session_state.maj_date:
        st.session_state.maj_date = maj_date; persist()

    capacite = st.text_input("Capacité équipe", value=st.session_state.capacite)
    if capacite != st.session_state.capacite:
        st.session_state.capacite = capacite; persist()

    c1, c2 = st.columns(2)
    with c1:
        spl = st.text_input("Libellé sprint actuel",
                            value=st.session_state.sprint_progress_label)
        if spl != st.session_state.sprint_progress_label:
            st.session_state.sprint_progress_label = spl; persist()
    with c2:
        spv = st.number_input("Avancement (%)", min_value=0, max_value=100,
                              value=st.session_state.sprint_progress)
        if spv != st.session_state.sprint_progress:
            st.session_state.sprint_progress = spv; persist()

    st.divider()
    st.markdown('<div class="section-title">📅 Sprints</div>', unsafe_allow_html=True)

    sprint_labels = [f"{i}: {s['label']}" for i, s in enumerate(st.session_state.sprints)]
    cur_sp = st.selectbox(
        "Sprint courant (encadré vert)",
        options=list(range(len(st.session_state.sprints))),
        format_func=lambda i: sprint_labels[i],
        index=st.session_state.current_sprint)
    if cur_sp != st.session_state.current_sprint:
        st.session_state.current_sprint = cur_sp; persist()

    with st.expander("✏️ Éditer les sprints", expanded=False):
        sprints_updated = []
        changed = False
        for i, sp in enumerate(st.session_state.sprints):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                lbl = st.text_input(f"Nom #{i+1}",   value=sp["label"], key=f"sp_lbl_{i}")
            with c2:
                dat = st.text_input(f"Dates #{i+1}", value=sp["dates"], key=f"sp_dat_{i}")
            with c3:
                st.write(""); st.write("")
                del_sp = st.button("🗑", key=f"del_sp_{i}")
            if not del_sp:
                sprints_updated.append({"label": lbl, "dates": dat})
                if lbl != sp["label"] or dat != sp["dates"]:
                    changed = True
            else:
                changed = True
        if changed:
            st.session_state.sprints = sprints_updated; persist()

        new_lbl = st.text_input("Nouveau sprint — nom",   key="new_sp_lbl")
        new_dat = st.text_input("Nouveau sprint — dates", key="new_sp_dat")
        if st.button("➕ Ajouter un sprint"):
            if new_lbl:
                st.session_state.sprints.append({"label": new_lbl, "dates": new_dat})
                persist()
                st.rerun()

    with st.expander("🏖️ Vacances", expanded=False):
        sv = st.toggle("Afficher les vacances", value=st.session_state.show_vacances)
        if sv != st.session_state.show_vacances:
            st.session_state.show_vacances = sv; persist()

        if st.session_state.show_vacances:
            vsp = st.number_input("Sur quel sprint (index)", min_value=0,
                                  max_value=max(0, len(st.session_state.sprints) - 1),
                                  value=min(st.session_state.vacances_sprint,
                                            len(st.session_state.sprints) - 1))
            if vsp != st.session_state.vacances_sprint:
                st.session_state.vacances_sprint = vsp; persist()

            vlbl = st.text_input("Label vacances", value=st.session_state.vacances_label)
            if vlbl != st.session_state.vacances_label:
                st.session_state.vacances_label = vlbl; persist()

    st.divider()
    st.markdown('<div class="section-title">🏗️ Chantiers</div>', unsafe_allow_html=True)

    n_sp = len(st.session_state.sprints)
    chantiers_updated = []

    def statut_key_from_val(val):
        for k, v in STATUT_VALS.items():
            if v == val:
                return k
        return "—  Inactif"

    for i, ch in enumerate(st.session_state.chantiers):
        with st.expander(f"📌 {ch['name']}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                ch_name   = st.text_input("Nom",    value=ch["name"],   key=f"ch_name_{i}")
            with c2:
                ch_charge = st.text_input("Charge", value=ch["charge"], key=f"ch_charge_{i}")

            ch_description = st.text_area(
                "Description",
                value=ch.get("description", ""),
                key=f"ch_desc_{i}",
                height=60,
            )

            ch_livrable = st.text_area("Livrable",
                                       value=ch.get("livrable", "--"),
                                       key=f"ch_liv_{i}", height=60)

            c1, c2 = st.columns(2)
            with c1:
                ch_jalon_label  = st.text_input("Label jalon",
                                                value=ch.get("jalon_label", ""),
                                                key=f"ch_jl_{i}")
            with c2:
                ch_jalon_sprint = st.number_input(
                    "Sprint jalon (index)", min_value=0,
                    max_value=max(0, n_sp - 1),
                    value=min(ch.get("jalon_sprint", 0), max(0, n_sp - 1)),
                    key=f"ch_js_{i}")

            st.markdown("**Planning par sprint :**")
            prog_updated  = []
            existing_prog = list(ch.get("progress", []))

            for row_start in range(0, n_sp, 2):
                cols = st.columns(2)
                for col_idx, col in enumerate(cols):
                    j = row_start + col_idx
                    if j >= n_sp:
                        break
                    sp_label = st.session_state.sprints[j]["label"]
                    cur_val, cur_phase = (existing_prog[j] if j < len(existing_prog)
                                          else (None, "dev"))
                    cur_statut_key = statut_key_from_val(cur_val)
                    cur_phase_idx  = (PHASE_KEYS.index(cur_phase)
                                      if cur_phase in PHASE_KEYS else 1)
                    with col:
                        st.markdown(f"**{sp_label}**")
                        sel_statut = st.selectbox(
                            "Statut", options=STATUT_KEYS,
                            index=STATUT_KEYS.index(cur_statut_key),
                            key=f"st_{i}_{j}")
                        if STATUT_VALS[sel_statut] is not None:
                            sel_phase = st.selectbox(
                                "Phase", options=PHASE_KEYS,
                                index=cur_phase_idx,
                                key=f"ph_{i}_{j}")
                        else:
                            sel_phase = cur_phase
                            st.selectbox("Phase", options=PHASE_KEYS,
                                         index=cur_phase_idx,
                                         key=f"ph_{i}_{j}", disabled=True)
                        prog_updated.append((STATUT_VALS[sel_statut], sel_phase))

            del_ch = st.button(f"🗑️ Supprimer ce chantier", key=f"del_ch_{i}")
            if not del_ch:
                new_ch = {
                    "name":         ch_name,
                    "charge":       ch_charge,
                    "description":  ch_description,
                    "livrable":     ch_livrable,
                    "jalon_label":  ch_jalon_label,
                    "jalon_sprint": ch_jalon_sprint,
                    "progress":     prog_updated,
                }
                chantiers_updated.append(new_ch)
                # Sauvegarde si changement détecté
                if new_ch != ch:
                    pass  # on sauvegarde en bloc après

    # Sauvegarde en bloc si chantiers ont changé
    if chantiers_updated != st.session_state.chantiers:
        st.session_state.chantiers = chantiers_updated
        persist()
    else:
        st.session_state.chantiers = chantiers_updated

    st.markdown("---")
    with st.expander("➕ Ajouter un chantier"):
        new_name     = st.text_input("Nom",         key="new_ch_name")
        new_charge   = st.text_input("Charge",      key="new_ch_charge",  value="1 Dev")
        new_desc     = st.text_area("Description",  key="new_ch_desc",    height=60)
        new_livrable = st.text_input("Livrable",    key="new_ch_liv",     value="--")
        new_jalon    = st.text_input("Label jalon", key="new_ch_jal")
        new_jal_sp   = st.number_input("Sprint jalon", min_value=0,
                                       max_value=max(0, n_sp - 1),
                                       key="new_ch_jal_sp")
        if st.button("✅ Créer le chantier"):
            if new_name:
                st.session_state.chantiers.append({
                    "name":         new_name,
                    "charge":       new_charge,
                    "description":  new_desc,
                    "livrable":     new_livrable,
                    "jalon_label":  new_jalon,
                    "jalon_sprint": new_jal_sp,
                    "progress":     [(None, "dev")] * n_sp,
                })
                persist()
                st.rerun()

    st.divider()
    st.markdown('<div class="section-title">💾 Import / Export JSON</div>',
                unsafe_allow_html=True)

    export_data = {
        "titre":                 st.session_state.titre,
        "maj_date":              st.session_state.maj_date,
        "capacite":              st.session_state.capacite,
        "sprint_progress":       st.session_state.sprint_progress,
        "sprint_progress_label": st.session_state.sprint_progress_label,
        "current_sprint":        st.session_state.current_sprint,
        "show_vacances":         st.session_state.show_vacances,
        "vacances_sprint":       st.session_state.vacances_sprint,
        "vacances_label":        st.session_state.vacances_label,
        "sprints":               st.session_state.sprints,
        "chantiers": [
            {**c, "progress": [[v, p] for v, p in c["progress"]]}
            for c in st.session_state.chantiers
        ],
    }

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "📥 Exporter JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name="roadmap_config.json",
            mime="application/json",
            use_container_width=True)
    with c2:
        if st.button("🔄 Reset défauts", use_container_width=True):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v if not isinstance(v, list) else [
                    {**x} if isinstance(x, dict) else x for x in v]
            persist()
            st.rerun()

    uploaded = st.file_uploader("📤 Importer une config JSON", type="json")
    if uploaded:
        data = json.load(uploaded)
        for key in DEFAULTS.keys():
            if key in data:
                st.session_state[key] = data[key]
        if "chantiers" in data:
            st.session_state.chantiers = [
                {**c, "progress": [tuple(p) for p in c["progress"]]}
                for c in data["chantiers"]
            ]
        persist()
        st.success("✅ Config importée et sauvegardée !")
        st.rerun()

# ════════════════════════════════════════════
#  APERÇU
# ════════════════════════════════════════════
with col_right:
    st.markdown('<div class="section-title">👁️ Aperçu de la roadmap</div>',
                unsafe_allow_html=True)

    buf = generate_roadmap(
        sprints               = st.session_state.sprints,
        chantiers             = st.session_state.chantiers,
        current_sprint        = st.session_state.current_sprint,
        titre                 = st.session_state.titre,
        maj_date              = st.session_state.maj_date,
        sprint_progress       = st.session_state.sprint_progress,
        sprint_progress_label = st.session_state.sprint_progress_label,
        capacite              = st.session_state.capacite,
        show_vacances         = st.session_state.show_vacances,
        vacances_sprint       = st.session_state.vacances_sprint,
        vacances_label        = st.session_state.vacances_label,
    )

    st.image(buf, use_container_width=True)

    st.download_button(
        label     = "⬇️ Télécharger la roadmap (PNG)",
        data      = buf,
        file_name = "roadmap.png",
        mime      = "image/png",
        use_container_width=True,
    )

