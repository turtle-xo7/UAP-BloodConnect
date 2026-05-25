"""
UAP-BloodConnect — Diagram Generator
Generates all project diagrams as PNG images.
Run: python docs/diagrams/generate_diagrams.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__))
DPI = 150

# ─── Palette ───────────────────────────────────────────────────────────────
C_BG     = '#F8FAFC'
C_DARK   = '#0F172A'
C_SLATE  = '#1E293B'
C_MID    = '#334155'
C_LIGHT  = '#94A3B8'
C_WHITE  = '#FFFFFF'
C_RED    = '#C62828'
C_RED2   = '#EF5350'
C_GOLD   = '#F59E0B'
C_GREEN  = '#16A34A'
C_BLUE   = '#1D4ED8'
C_PURPLE = '#7C3AED'
C_TEAL   = '#0D9488'
C_ORANGE = '#EA580C'

def fig_setup(w, h, title=None):
    fig, ax = plt.subplots(figsize=(w/100, h/100))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    ax.axis('off')
    if title:
        ax.text(w/2, h-22, title, ha='center', va='center',
                fontsize=13, fontweight='bold', color=C_DARK,
                fontfamily='DejaVu Sans')
        ax.add_patch(FancyBboxPatch((w*0.05, h-40), w*0.9, 24,
                     boxstyle="round,pad=2", facecolor=C_RED, alpha=0.1,
                     linewidth=0, zorder=0))
    return fig, ax

def box(ax, x, y, w, h, label, sublabel=None, fc=C_SLATE, tc=C_WHITE,
        fs=9, border=None, alpha=1.0, radius=6):
    bp = FancyBboxPatch((x, y), w, h,
                        boxstyle=f"round,pad=1,rounding_size={radius}",
                        facecolor=fc, edgecolor=border or fc,
                        linewidth=1.5 if border else 0, alpha=alpha, zorder=2)
    ax.add_patch(bp)
    cy = y + h/2 + (5 if sublabel else 0)
    ax.text(x+w/2, cy, label, ha='center', va='center',
            fontsize=fs, fontweight='bold', color=tc,
            fontfamily='DejaVu Sans', zorder=3, wrap=True)
    if sublabel:
        ax.text(x+w/2, y+h/2-8, sublabel, ha='center', va='center',
                fontsize=fs-1.5, color=tc, alpha=0.75,
                fontfamily='DejaVu Sans', zorder=3)

def arrow(ax, x1, y1, x2, y2, color=C_LIGHT, lw=1.5, style='->', label=None):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle='arc3,rad=0.0'))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+3, my+3, label, fontsize=7, color=color, zorder=5)

def dbshape(ax, x, y, w, h, label, fc=C_TEAL):
    """ Cylinder-like data store shape """
    ew = w; eh = 14
    rect = FancyBboxPatch((x, y), ew, h,
                          boxstyle="round,pad=1,rounding_size=3",
                          facecolor=fc, edgecolor=fc, linewidth=0, zorder=2)
    ax.add_patch(rect)
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((x+w/2, y+h), w/2, eh,
                         facecolor=fc, edgecolor='white', linewidth=0.5, zorder=3))
    ax.add_patch(Ellipse((x+w/2, y), w/2, eh,
                         facecolor=fc, edgecolor='white', linewidth=0.5, zorder=3))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center',
            fontsize=8, fontweight='bold', color='white', zorder=4)


# ══════════════════════════════════════════════════════════════════════════════
# 1. SYSTEM ARCHITECTURE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
def diagram_architecture():
    W, H = 1100, 720
    fig, ax = fig_setup(W, H)

    # Title
    ax.text(W/2, H-18, "UAP-BloodConnect — System Architecture",
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.05, xmax=0.95)

    layers = [
        (H-80,  70, C_BLUE,   "LAYER 1 — CLIENT",         [(150,'Web Browser'),(350,'Mobile Browser'),(550,'REST Client')]),
        (H-185, 70, '#065F46',"LAYER 2 — PRESENTATION",    [(110,'Django\nTemplates'),(260,'CSS3 +\nAnimations'),(410,'Three.js\n(WebGL)'),(560,'Font Awesome\nAOS'),(710,'Google\nFonts')]),
        (H-295, 70, C_RED,    "LAYER 3 — APPLICATION",     [(120,'accounts\napp'),(280,'donors\napp'),(440,'requests\napp'),(600,'bloodconnect\n(config)')]),
        (H-400, 70, C_MID,    "LAYER 4 — BUSINESS LOGIC",  [(110,'Models &\nMigrations'),(265,'Views &\nDecorators'),(420,'Forms &\nValidation'),(575,'Context\nProcessors'),(730,'Middleware')]),
        (H-505, 70, '#4C1D95',"LAYER 5 — DATA",            [(200,'SQLite3\nDatabase'),(420,'Media\nFile Storage'),(640,'Django\nAdmin Panel')]),
    ]

    for (ly, lh, lc, ltitle, items) in layers:
        # Layer background
        ax.add_patch(FancyBboxPatch((40, ly), W-80, lh,
                     boxstyle="round,pad=2,rounding_size=8",
                     facecolor=lc, edgecolor=lc, linewidth=0, alpha=0.12, zorder=1))
        ax.add_patch(FancyBboxPatch((40, ly), 135, lh,
                     boxstyle="round,pad=2,rounding_size=4",
                     facecolor=lc, edgecolor='none', linewidth=0, alpha=0.7, zorder=1))
        # Layer title
        ax.text(50, ly + lh/2, ltitle, ha='left', va='center',
                fontsize=7.5, fontweight='bold', color='white', zorder=3,
                rotation=0)
        # Items
        for (ix, ilabel) in items:
            bx = 180 + ix
            bw, bh = 115, lh - 12
            box(ax, bx, ly+6, bw, bh, ilabel, fc='white',
                tc=lc if lc != C_MID else C_DARK, fs=7.5, border=lc)

        # Arrow between layers
        if ly > H-505:
            ax.annotate('', xy=(W/2, ly+lh+2), xytext=(W/2, ly+lh+14),
                        arrowprops=dict(arrowstyle='<->', color=C_LIGHT, lw=1.5))

    # External CDN box
    box(ax, W-210, H-505, 155, 55, "External CDNs", "Three.js · AOS · FontAwesome\nGoogle Fonts · Cloudflare",
        fc='#78350F', tc='white', fs=7.5)
    ax.annotate('', xy=(W-55, H-455), xytext=(W-160, H-460),
                arrowprops=dict(arrowstyle='->', color='#92400E', lw=1.5,
                                linestyle='dashed'))
    ax.text(W-140, H-445, 'CDN', fontsize=7, color='#92400E')

    # Role badges
    roles = ['Super Admin','Faculty Advisor','Club President','Moderator','Donor','Student']
    rx = 42; ry = 135
    ax.text(rx+15, ry+52, '9 USER ROLES', fontsize=7.5, fontweight='bold',
            color=C_RED, ha='center')
    for i, r in enumerate(roles):
        col = [C_GOLD, C_PURPLE, C_BLUE, C_GREEN, C_RED, C_LIGHT][i]
        ax.add_patch(FancyBboxPatch((rx, ry + i*(-16)), 90, 13,
                     boxstyle="round,pad=1", facecolor=col, alpha=0.15,
                     edgecolor=col, linewidth=1, zorder=2))
        ax.text(rx+45, ry+6.5 + i*(-16), r, ha='center', va='center',
                fontsize=6.5, color=col, fontweight='bold', zorder=3)

    # Legend
    ax.text(42, 40, 'Project: UAP-BloodConnect  |  Stack: Django 4.x + SQLite3 + Three.js  |  Team: Shahariar · Moshiur · Rajash',
            fontsize=7, color=C_LIGHT, ha='left')

    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '01_architecture.png'), dpi=DPI, bbox_inches='tight',
                facecolor=C_BG)
    plt.close()
    print("OK 01_architecture.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. USE-CASE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
def diagram_usecase():
    W, H = 1100, 780
    fig, ax = fig_setup(W, H)
    ax.text(W/2, H-18, "UAP-BloodConnect — Use-Case Diagram",
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.05, xmax=0.95)

    # System boundary
    ax.add_patch(FancyBboxPatch((200, 50), 690, H-110,
                 boxstyle="round,pad=4,rounding_size=10",
                 facecolor='none', edgecolor=C_RED, linewidth=2, linestyle='--', zorder=1))
    ax.text(545, H-52, '« system »  UAP-BloodConnect Platform',
            ha='center', va='center', fontsize=9, color=C_RED, fontweight='bold')

    def actor(x, y, name, color=C_DARK):
        # Head
        ax.add_patch(plt.Circle((x, y+28), 12, facecolor=color, edgecolor='white', lw=1.5, zorder=3))
        # Body lines
        ax.plot([x, x], [y+16, y-10], color=color, lw=2, zorder=3)
        ax.plot([x-16, x+16], [y+2, y+2], color=color, lw=2, zorder=3)
        ax.plot([x, x-14], [y-10, y-24], color=color, lw=2, zorder=3)
        ax.plot([x, x+14], [y-10, y-24], color=color, lw=2, zorder=3)
        ax.text(x, y-34, name, ha='center', va='top', fontsize=8,
                fontweight='bold', color=color, multialignment='center')

    def usecase(x, y, w, h, text, color=C_SLATE):
        from matplotlib.patches import Ellipse
        ax.add_patch(Ellipse((x, y), w, h, facecolor=color, edgecolor='white',
                             linewidth=1, zorder=2, alpha=0.9))
        ax.text(x, y, text, ha='center', va='center', fontsize=7.5,
                color='white', fontweight='bold', multialignment='center', zorder=3)

    def assoc(ax1, ay1, ux, uy, color=C_LIGHT):
        ax.annotate('', xy=(ux, uy), xytext=(ax1, ay1),
                    arrowprops=dict(arrowstyle='-', color=color, lw=1.2))

    # ── Left Actors ──
    actor(75, 590, 'Anonymous\nUser',    C_LIGHT)
    actor(75, 450, 'Student\n(User)',    C_BLUE)
    actor(75, 290, 'Donor',             C_RED)

    # ── Right Actors ──
    actor(1025, 590, 'Faculty\nAdvisor',  C_PURPLE)
    actor(1025, 430, 'Club\nPresident',   C_GREEN)
    actor(1025, 270, 'Super\nAdmin',      C_GOLD)

    # ── Use Cases ──
    ucs = [
        # Public
        (390, 700, 240, 36, 'Browse Blood Requests',          C_MID),
        (390, 650, 240, 36, 'View Donor Directory',            C_MID),
        (390, 600, 200, 36, 'Check Blood Eligibility',         C_MID),
        (390, 550, 200, 36, 'View Blood Type Education',       C_MID),
        # Student
        (390, 490, 200, 36, 'Register / Login',                C_BLUE),
        (390, 440, 200, 36, 'Submit Blood Request',            C_BLUE),
        (390, 390, 200, 36, 'View Notifications',              C_BLUE),
        (390, 340, 200, 36, 'Edit Profile',                    C_BLUE),
        # Donor
        (680, 680, 200, 36, 'Register as Donor',              C_RED),
        (680, 630, 200, 36, 'Log Donation History',            C_RED),
        (680, 580, 200, 36, 'Respond to Blood Request',        C_RED),
        (680, 530, 200, 36, 'Toggle Availability Status',      C_RED),
        (680, 480, 200, 36, 'Earn Achievement Badges',         C_RED),
        (680, 430, 200, 36, 'View Leaderboard',                C_RED),
        (680, 380, 200, 36, 'Register for Drive',              C_RED),
        # Admin
        (680, 310, 200, 36, 'Verify Donations',               C_PURPLE),
        (680, 260, 200, 36, 'Moderate Blood Requests',        C_PURPLE),
        (680, 210, 200, 36, 'Approve Broadcasts',             C_PURPLE),
        # President
        (390, 265, 200, 36, 'Create Donation Drive',          C_GREEN),
        (390, 215, 200, 36, 'Submit Emergency Broadcast',     C_GREEN),
        # SuperAdmin
        (390, 145, 200, 36, 'Manage User Roles',              C_GOLD),
        (680, 145, 200, 36, 'Access Django Admin Panel',      C_GOLD),
    ]

    for (ux, uy, uw, uh, txt, col) in ucs:
        usecase(ux, uy, uw, uh, txt, col)

    # Associations
    assocs = [
        # Anonymous → public
        (75,580, 270,700), (75,580, 270,650), (75,580, 290,600), (75,580, 290,550),
        # Student →
        (75,460, 290,490), (75,460, 290,440), (75,460, 290,390), (75,460, 290,340),
        # Donor →
        (75,295, 580,680), (75,295, 580,630), (75,295, 580,580),
        (75,295, 580,530), (75,295, 580,480), (75,295, 580,430), (75,295, 580,380),
        # Advisor →
        (1025,590, 780,310), (1025,590, 780,260), (1025,590, 780,210),
        # President →
        (1025,430, 490,265), (1025,430, 490,215),
        # SuperAdmin →
        (1025,270, 490,145), (1025,270, 780,145),
    ]
    for (ax1,ay1,ux,uy) in assocs:
        assoc(ax1,ay1,ux,uy)

    # Inheritance arrows (Student extends Anonymous, Donor extends Student)
    def extend(x1,y1,x2,y2,lbl):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='-|>', color=C_MID, lw=1.5))
        ax.text((x1+x2)/2-25,(y1+y2)/2, f'«extends»', fontsize=6.5,
                color=C_MID, fontstyle='italic')
    extend(75,460, 75,540, '')
    extend(75,290, 75,410, '')

    ax.text(W/2, 25, 'Arrows show association. «extends» shows inheritance of actor permissions.',
            ha='center', fontsize=7.5, color=C_LIGHT)

    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '02_use_case.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 02_use_case.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. DFD LEVEL 0 — CONTEXT DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
def diagram_dfd0():
    W, H = 900, 580
    fig, ax = fig_setup(W, H)
    ax.text(W/2, H-18, "DFD Level 0 — Context Diagram",
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.05, xmax=0.95)

    def entity(x, y, w, h, name, color=C_DARK):
        ax.add_patch(FancyBboxPatch((x,y), w, h,
                     boxstyle="round,pad=2,rounding_size=4",
                     facecolor=color, edgecolor='white', lw=1.5, zorder=2))
        ax.text(x+w/2, y+h/2, name, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=3,
                multialignment='center')

    def process(cx, cy, r, name):
        circle = plt.Circle((cx,cy), r, facecolor=C_RED, edgecolor='white', lw=2.5, zorder=2)
        ax.add_patch(circle)
        ax.text(cx, cy+8, '0.0', ha='center', va='center', fontsize=8,
                color='white', alpha=0.6, zorder=3)
        ax.text(cx, cy-8, name, ha='center', va='center', fontsize=9,
                fontweight='bold', color='white', zorder=3, multialignment='center')

    def flow(x1,y1,x2,y2, label, color=C_MID):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                   mutation_scale=15))
        mx,my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+8, label, ha='center', va='bottom', fontsize=7.5,
                color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=2', facecolor=C_BG, edgecolor='none', alpha=0.85))

    # Central process
    process(450, 285, 95, 'UAP-\nBloodConnect\nSystem')

    # External entities
    entities = [
        (35,  440, 130, 55, 'Student /\nUser',      C_BLUE),
        (35,  270, 130, 55, 'Donor',                 C_RED),
        (35,  100, 130, 55, 'Faculty\nAdvisor',      C_PURPLE),
        (735, 440, 130, 55, 'Club\nPresident',       C_GREEN),
        (735, 270, 130, 55, 'Super\nAdmin',          C_GOLD),
        (735, 100, 130, 55, 'Django\nAdmin',         C_MID),
    ]
    for args in entities:
        entity(*args)

    # Data flows
    flows = [
        # Student
        (165,470, 360,330, 'Blood Requests\nRegistration Data', C_BLUE),
        (355,250, 165,450, 'Notifications\nRequest Status', C_BLUE),
        # Donor
        (165,295, 358,295, 'Donation Records\nAvailability Status', C_RED),
        (358,275, 165,275, 'Badges, Eligibility\nLeaderboard Data', C_RED),
        # Faculty Advisor
        (165,120, 360,220, 'Verification Decisions\nModeration Actions', C_PURPLE),
        (355,195, 165,110, 'Pending Queues\nDashboard Data', C_PURPLE),
        # Club President
        (735,465, 545,330, 'Drive Details\nBroadcast Requests', C_GREEN),
        (545,260, 735,445, 'Approval Status\nDrive Analytics', C_GREEN),
        # Super Admin
        (735,295, 545,300, 'Role Assignments', C_GOLD),
        (545,280, 735,280, 'User List', C_GOLD),
        # Django Admin
        (735,120, 545,220, 'Direct DB Access', C_MID),
    ]
    for (x1,y1,x2,y2,lbl,col) in flows:
        flow(x1,y1,x2,y2,lbl,col)

    ax.text(W/2, 28, 'External entities interact with the central UAP-BloodConnect system via data flows.',
            ha='center', fontsize=8, color=C_LIGHT)

    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '03_dfd_level0.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 03_dfd_level0.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. DFD LEVEL 1
# ══════════════════════════════════════════════════════════════════════════════
def diagram_dfd1():
    W, H = 1150, 760
    fig, ax = fig_setup(W, H)
    ax.text(W/2, H-18, "DFD Level 1 — Main System Processes",
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.05, xmax=0.95)

    def process(cx, cy, r, pid, name, color=C_RED):
        c = plt.Circle((cx,cy), r, facecolor=color, edgecolor='white', lw=2, zorder=3)
        ax.add_patch(c)
        ax.text(cx, cy+10, pid, ha='center', va='center', fontsize=8,
                color='white', alpha=0.7, zorder=4)
        ax.text(cx, cy-6, name, ha='center', va='center', fontsize=8,
                fontweight='bold', color='white', zorder=4, multialignment='center')

    def store(x, y, w, label, color=C_TEAL):
        ax.add_patch(mpatches.FancyBboxPatch((x,y), w, 28,
                     boxstyle="round,pad=1", facecolor=color,
                     edgecolor='white', lw=1.5, zorder=2))
        ax.plot([x,x], [y,y+28], color='white', lw=1.5, zorder=3)
        ax.plot([x+20,x+20], [y,y+28], color='white', lw=1.5, zorder=3)
        ax.text(x+w/2+8, y+14, label, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white', zorder=3)

    def entity(x,y,w,h,name,color=C_SLATE):
        ax.add_patch(FancyBboxPatch((x,y),w,h,
                     boxstyle="round,pad=2,rounding_size=4",
                     facecolor=color, edgecolor='white', lw=1.5, zorder=2))
        ax.text(x+w/2, y+h/2, name, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='white', zorder=3,
                multialignment='center')

    def flow(x1,y1,x2,y2,lbl,col=C_MID, offset=(0,8)):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=col, lw=1.8, mutation_scale=12))
        mx,my = (x1+x2)/2+offset[0], (y1+y2)/2+offset[1]
        ax.text(mx, my, lbl, ha='center', va='bottom', fontsize=6.5, color=col,
                bbox=dict(boxstyle='round,pad=1.5', facecolor=C_BG, edgecolor='none', alpha=0.9))

    # Processes
    process(230, 620, 58, '1.0', 'User\nManagement',    C_BLUE)
    process(560, 620, 58, '2.0', 'Request\nManagement', C_RED)
    process(890, 620, 58, '3.0', 'Donation\nManagement',C_GREEN)
    process(230, 340, 58, '4.0', 'Notification\nSystem', C_PURPLE)
    process(560, 340, 58, '5.0', 'Achievement\nEngine',  C_GOLD)
    process(890, 340, 58, '6.0', 'Drive\nManagement',    C_ORANGE)

    # Data stores
    store(85,  185, 190, 'D1  Users / Profiles',    C_BLUE)
    store(385, 185, 200, 'D2  Blood Requests',       C_RED)
    store(685, 185, 200, 'D3  Donation History',     C_GREEN)
    store(385, 100, 200, 'D4  Notifications',        C_PURPLE)
    store(685, 100, 200, 'D5  Achievements',         C_GOLD)
    store(85,  100, 190, 'D6  Donation Drives',      C_ORANGE)

    # Entities
    entity(35, 630, 100, 40, 'Student\n/ User',  C_BLUE)
    entity(35, 420, 100, 40, 'Donor',            C_RED)
    entity(35, 280, 100, 40, 'Faculty\nAdvisor', C_PURPLE)
    entity(1010,630,100, 40, 'Club\nPresident',  C_GREEN)
    entity(1010,420,100, 40, 'Super\nAdmin',     C_GOLD)

    # Data flows
    flows = [
        (135,648, 172,625, 'Register\nLogin',         C_BLUE, (0,6)),
        (172,615, 135,645, 'Auth Token\nProfile',     C_BLUE, (0,-14)),
        (288,623, 502,622, 'Submit Request',           C_RED,  (0,8)),
        (502,617, 288,617, 'Request Status',           C_RED,  (0,-8)),
        (618,623, 832,623, 'Submit Donation',          C_GREEN,(0,8)),
        (832,618, 618,618, 'Verification\nStatus',    C_GREEN,(0,-8)),
        (135,440, 172,630, 'Donor Data',               C_RED,  (-8,0)),
        (172,620, 135,440, 'Eligibility',              C_RED,  (8,0)),
        (135,295, 172,350, 'Moderation\nDecision',    C_PURPLE,(0,6)),
        (172,335, 135,285, 'Pending Queue',           C_PURPLE,(0,-6)),
        (1010,648, 948,628,'Drive Info',              C_GREEN, (0,8)),
        (948,618, 1010,638,'Drive Status',            C_GREEN, (0,-8)),
        # Internal
        (288,610, 288,398, 'New Request\nEvent',      C_PURPLE,(-8,0)),
        (618,582, 502,398, 'Donation\nApproved',      C_GOLD,  (0,8)),
        (502,582, 560,368, 'Check\nMilestones',       C_GOLD,  (8,0)),
        (618,582, 832,398, 'Drive Data',              C_ORANGE,(8,0)),
        # To data stores
        (230,562, 180,213, 'User Record',             C_BLUE,  (-12,0)),
        (560,562, 490,213, 'Request Record',          C_RED,   (0,0)),
        (890,562, 790,213, 'Donation Record',         C_GREEN, (0,0)),
        (230,382, 230,213, 'Notification\nRecord',   C_PURPLE,(8,0)),
        (560,382, 590,128, 'Badge Record',            C_GOLD,  (8,0)),
        (890,382, 240,128, 'Drive Record',            C_ORANGE,(0,0)),
    ]
    for args in flows:
        flow(*args)

    ax.text(W/2, 28, 'Each process transforms data flows between external entities and internal data stores.',
            ha='center', fontsize=8, color=C_LIGHT)
    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '04_dfd_level1.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 04_dfd_level1.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. ER DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
def diagram_er():
    W, H = 1300, 900
    fig, ax = fig_setup(W, H)
    ax.text(W/2, H-18, "Entity-Relationship Diagram — UAP-BloodConnect",
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.03, xmax=0.97)

    def entity_box(x, y, title, attrs, color=C_SLATE, w=185, attr_h=18):
        h = 30 + len(attrs) * attr_h
        # Header
        ax.add_patch(FancyBboxPatch((x,y+h-30), w, 30,
                     boxstyle="round,pad=1,rounding_size=6",
                     facecolor=color, edgecolor=color, lw=0, zorder=2))
        ax.text(x+w/2, y+h-15, title, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=3)
        # Body
        ax.add_patch(FancyBboxPatch((x,y), w, h-30,
                     boxstyle="round,pad=1,rounding_size=3",
                     facecolor='#F1F5F9', edgecolor=color, lw=1.5, zorder=2))
        for i, (aname, atype, is_pk, is_fk) in enumerate(attrs):
            ay = y + (h-30) - (i+1)*attr_h + 2
            prefix = '[PK] ' if is_pk else ('[FK] ' if is_fk else '       ')
            fw = 'bold' if is_pk else 'normal'
            fs_style = 'normal' if not is_fk else 'italic'
            col = C_RED if is_pk else (C_BLUE if is_fk else C_DARK)
            ax.text(x+8, ay+attr_h/2, f"{prefix}{aname}", ha='left', va='center',
                    fontsize=7, fontweight=fw, fontstyle=fs_style, color=col, zorder=3)
            ax.text(x+w-6, ay+attr_h/2, atype, ha='right', va='center',
                    fontsize=6.5, color=C_LIGHT, zorder=3)
            if i < len(attrs)-1:
                ax.plot([x+4,x+w-4], [ay,ay], color='#CBD5E1', lw=0.5, zorder=3)
        return (x, y, w, h)

    def rel_line(x1,y1,x2,y2, label, card='1:N', color=C_MID):
        ax.plot([x1,x2],[y1,y2], color=color, lw=1.5, zorder=1, alpha=0.7)
        mx,my = (x1+x2)/2, (y1+y2)/2
        ax.add_patch(FancyBboxPatch((mx-28,my-8),56,16,
                     boxstyle="round,pad=1",
                     facecolor=C_BG, edgecolor=color, lw=1, alpha=0.95, zorder=4))
        ax.text(mx, my, f'{label}\n{card}', ha='center', va='center',
                fontsize=6, color=color, fontweight='bold', zorder=5,
                multialignment='center')

    # ── Entity definitions ──
    # CustomUser
    cu = entity_box(30, 680, 'CustomUser', [
        ('id',         'PK',       True,  False),
        ('username',   'varchar',  False, False),
        ('email',      'varchar',  False, False),
        ('uap_id',     'varchar',  False, False),
        ('role',       'varchar',  False, False),
        ('first_name', 'varchar',  False, False),
        ('last_name',  'varchar',  False, False),
    ], C_BLUE)

    # UserProfile
    up = entity_box(270, 680, 'UserProfile', [
        ('id',              'PK',  True,  False),
        ('user_id',         'FK',  False, True),
        ('profile_picture', 'img', False, False),
        ('date_of_birth',   'date',False, False),
        ('blood_group_id',  'FK',  False, True),
        ('bio',             'text',False, False),
    ], C_BLUE)

    # BloodGroup
    bg = entity_box(560, 780, 'BloodGroup', [
        ('id',         'PK',     True,  False),
        ('blood_type', 'varchar',False, False),
    ], C_RED, w=155)

    # Donor
    do = entity_box(560, 580, 'Donor', [
        ('id',                 'PK',     True,  False),
        ('user_id',            'FK',     False, True),
        ('blood_group_id',     'FK',     False, True),
        ('location',           'varchar',False, False),
        ('availability_status','varchar',False, False),
        ('total_donations',    'int',    False, False),
        ('last_donation_date', 'date',   False, False),
        ('emergency_response', 'bool',   False, False),
    ], C_RED)

    # DonationHistory
    dh = entity_box(560, 310, 'DonationHistory', [
        ('id',                  'PK',     True,  False),
        ('donor_id',            'FK',     False, True),
        ('donation_date',       'date',   False, False),
        ('hospital',            'varchar',False, False),
        ('units_donated',       'int',    False, False),
        ('verification_status', 'varchar',False, False),
        ('verified_by_id',      'FK',     False, True),
        ('rejection_reason',    'text',   False, False),
    ], '#065F46')

    # Achievement
    ach = entity_box(800, 310, 'Achievement', [
        ('id',          'PK',     True,  False),
        ('donor_id',    'FK',     False, True),
        ('title',       'varchar',False, False),
        ('description', 'text',   False, False),
        ('badge_type',  'varchar',False, False),
        ('achieved_at', 'datetime',False,False),
    ], C_GOLD, w=170)

    # BloodRequest
    br = entity_box(800, 580, 'BloodRequest', [
        ('id',               'PK',     True,  False),
        ('requester_id',     'FK',     False, True),
        ('patient_name',     'varchar',False, False),
        ('blood_group_id',   'FK',     False, True),
        ('urgency',          'varchar',False, False),
        ('status',           'varchar',False, False),
        ('units_required',   'int',    False, False),
        ('location',         'varchar',False, False),
        ('needed_by_date',   'datetime',False,False),
        ('moderation_status','varchar',False, False),
        ('moderated_by_id',  'FK',     False, True),
    ], '#7C3AED')

    # RequestResponse
    rr = entity_box(1060, 580, 'RequestResponse', [
        ('id',              'PK',      True,  False),
        ('blood_request_id','FK',      False, True),
        ('donor_id',        'FK',      False, True),
        ('message',         'text',    False, False),
        ('status',          'varchar', False, False),
        ('responded_at',    'datetime',False, False),
    ], C_PURPLE, w=170)

    # DonationDrive
    dd = entity_box(800, 130, 'DonationDrive', [
        ('id',              'PK',     True,  False),
        ('title',           'varchar',False, False),
        ('date',            'date',   False, False),
        ('venue',           'varchar',False, False),
        ('target_units',    'int',    False, False),
        ('is_approved',     'bool',   False, False),
        ('approved_by_id',  'FK',     False, True),
        ('created_by_id',   'FK',     False, True),
        ('status',          'varchar',False, False),
    ], C_ORANGE)

    # DriveRegistration
    dr_reg = entity_box(1060, 130, 'DriveRegistration', [
        ('id',           'PK',      True,  False),
        ('drive_id',     'FK',      False, True),
        ('donor_id',     'FK',      False, True),
        ('attended',     'bool',    False, False),
        ('registered_at','datetime',False, False),
    ], C_ORANGE, w=170)

    # Notification
    notif = entity_box(30, 400, 'Notification', [
        ('id',                'PK',     True,  False),
        ('user_id',           'FK',     False, True),
        ('notification_type', 'varchar',False, False),
        ('title',             'varchar',False, False),
        ('message',           'text',   False, False),
        ('action_url',        'varchar',False, False),
        ('is_read',           'bool',   False, False),
        ('created_at',        'datetime',False,False),
    ], C_TEAL)

    # EmergencyBroadcast
    eb = entity_box(270, 400, 'EmergencyBroadcast', [
        ('id',           'PK',     True,  False),
        ('title',        'varchar',False, False),
        ('message',      'text',   False, False),
        ('created_by_id','FK',     False, True),
        ('approved_by_id','FK',    False, True),
        ('status',       'varchar',False, False),
        ('sent_at',      'datetime',False,False),
    ], '#BE185D', w=200)

    # Feedback
    fb = entity_box(30, 130, 'Feedback', [
        ('id',         'PK',     True,  False),
        ('name',       'varchar',False, False),
        ('email',      'varchar',False, False),
        ('rating',     'int',    False, False),
        ('message',    'text',   False, False),
        ('created_at', 'datetime',False,False),
    ], C_LIGHT, w=170)

    # ── Relationships ──
    rels = [
        (215,745, 270,745, 'has', '1:1', C_BLUE),
        (215,730, 560,700, 'places', '1:N', C_BLUE),
        (215,720, 560,645, 'is', '1:1', C_RED),
        (745,670, 800,680, 'responds', '1:N', C_PURPLE),
        (745,640, 800,640, 'receives', '1:N', '#7C3AED'),
        (745,600, 800,220, 'organizes', '1:N', C_ORANGE),
        (745,590, 1060,190, 'registers', 'N:M', C_ORANGE),
        (745,580, 1060,640, 'responds', 'N:M', C_PURPLE),
        (745,555, 800,390, 'logs', '1:N', '#065F46'),
        (745,545, 800,400, 'earns', '1:N', C_GOLD),
        (215,700, 270,480, 'notifies', '1:N', C_TEAL),
        (715,790, 800,790, 'has type', 'N:1', C_RED),
        (455,795, 560,795, 'type', 'N:1', C_BLUE),
    ]
    for args in rels:
        rel_line(*args)

    # Legend
    lx, ly = 30, 60
    ax.text(lx, ly+12, 'Legend:', fontsize=8, fontweight='bold', color=C_DARK)
    ax.text(lx+8, ly-4,  '[PK]  Primary Key', fontsize=7, color=C_RED, fontweight='bold')
    ax.text(lx+8, ly-18, '[FK]  Foreign Key',  fontsize=7, color=C_BLUE, fontstyle='italic')

    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '05_er_diagram.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 05_er_diagram.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. SEQUENCE DIAGRAM — Blood Request Creation & Donor Notification
# ══════════════════════════════════════════════════════════════════════════════
def diagram_sequence():
    W, H = 1050, 700
    fig, ax = fig_setup(W, H)
    ax.text(W/2, H-18, "Sequence Diagram — Blood Request Creation & Donor Notification",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.04, xmax=0.96)

    participants = [
        (90,  'User\n(Browser)',    C_BLUE),
        (250, 'Django\nRouter',     C_MID),
        (420, 'RequestView\n(View)',C_RED),
        (590, 'BloodRequest\n(Model)',C_GREEN),
        (760, 'Notification\nService',C_PURPLE),
        (930, 'Donor\n(Model)',     C_ORANGE),
    ]

    TOP = H - 60
    BOT = 55

    for (x, name, color) in participants:
        box(ax, x-52, TOP-10, 104, 38, name, fc=color, fs=8)
        ax.plot([x,x],[TOP-10, BOT], color=C_LIGHT, lw=1.2,
                linestyle='dashed', zorder=1)

    def msg(y, x1, x2, text, ret=False, color=C_DARK, note=None):
        col = color if not ret else C_LIGHT
        ls = 'dashed' if ret else 'solid'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle='->', color=col, lw=1.8,
                                   mutation_scale=12,
                                   linestyle=ls))
        lx = (x1+x2)/2
        ax.text(lx, y+6, text, ha='center', va='bottom', fontsize=8,
                color=col, fontweight='bold' if not ret else 'normal',
                bbox=dict(boxstyle='round,pad=1.5', facecolor=C_BG,
                          edgecolor='none', alpha=0.9), zorder=5)
        if note:
            ax.add_patch(FancyBboxPatch((x2+8, y-12), 130, 28,
                         boxstyle="round,pad=2", facecolor='#FEFCE8',
                         edgecolor=C_GOLD, lw=1, alpha=0.9, zorder=4))
            ax.text(x2+73, y+2, note, ha='center', va='center',
                    fontsize=7, color='#92400E', zorder=5)

    def activation(x, y1, y2, color=C_RED):
        ax.add_patch(FancyBboxPatch((x-6, y2), 12, y1-y2,
                     boxstyle="round,pad=1", facecolor=color,
                     alpha=0.25, edgecolor=color, lw=1, zorder=2))

    def label(y, text):
        ax.text(42, y, text, ha='left', va='center', fontsize=7.5,
                color=C_LIGHT, fontstyle='italic')
        ax.axhline(y, color='#E2E8F0', lw=0.5, xmin=0.03, xmax=0.97, zorder=0)

    # ── Messages ──
    label(620, '1. User fills request form')
    msg(610, 90, 250, 'POST /requests/create/\n(form data)')

    label(560, '2. Route to view')
    msg(548, 250, 420, 'request_list(request)')

    label(510, '3. Validate form')
    activation(420, 610, 475)
    msg(498, 420, 420, '', note='form.is_valid()\n→ True')

    label(460, '4. Create BloodRequest')
    msg(448, 420, 590, 'BloodRequest.objects.create()')
    msg(430, 590, 420, 'blood_request object', ret=True, color=C_GREEN)

    label(400, '5. Find matching donors')
    msg(388, 420, 760, 'notify_matching_donors(request)')
    msg(372, 760, 930, 'Donor.objects.filter(\nblood_group=..., available)')
    msg(352, 930, 760, '[ donor1, donor2, ... ]', ret=True, color=C_ORANGE)

    label(315, '6. Create notifications (loop)')
    ax.add_patch(FancyBboxPatch((740, 295), 220, 45,
                 boxstyle="round,pad=2", facecolor='none',
                 edgecolor=C_PURPLE, lw=1.5, linestyle='dashed', zorder=1))
    ax.text(850, 342, 'loop  [for each donor]', fontsize=7, color=C_PURPLE,
            ha='center', fontstyle='italic')
    msg(318, 760, 590, 'Notification.objects.create()')

    label(268, '7. Return success response')
    msg(255, 420, 250, 'redirect(request_detail)', ret=True, color=C_RED)
    msg(235, 250, 90,  'HTTP 302 → Detail Page', ret=True, color=C_BLUE)

    label(195, '8. User sees confirmation')
    msg(182, 90, 250, 'GET /requests/{id}/')
    msg(162, 250, 90,  'HTTP 200 — Request Detail', ret=True, color=C_BLUE)

    ax.text(W/2, 28, 'Solid arrows = synchronous calls. Dashed arrows = return values.',
            ha='center', fontsize=8, color=C_LIGHT)

    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '06_sequence.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 06_sequence.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. ACTIVITY DIAGRAM — Donation Verification Workflow
# ══════════════════════════════════════════════════════════════════════════════
def diagram_activity():
    W, H = 820, 900
    fig, ax = fig_setup(W, H)
    ax.text(W/2, H-18, "Activity Diagram — Donation Verification Workflow",
            ha='center', va='center', fontsize=13, fontweight='bold', color=C_DARK)
    ax.axhline(H-36, color=C_RED, lw=2, xmin=0.05, xmax=0.95)

    cx = W / 2

    def start_end(cx, cy, r=18, kind='start'):
        if kind == 'start':
            ax.add_patch(plt.Circle((cx,cy), r, facecolor=C_DARK, zorder=3))
        else:
            ax.add_patch(plt.Circle((cx,cy), r, facecolor=C_DARK, edgecolor=C_DARK, lw=3, zorder=3))
            ax.add_patch(plt.Circle((cx,cy), r-7, facecolor=C_BG, zorder=4))

    def activity(cx, cy, w, h, text, color=C_SLATE):
        ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                     boxstyle="round,pad=3,rounding_size=12",
                     facecolor=color, edgecolor='white', lw=1.5, zorder=2))
        ax.text(cx, cy, text, ha='center', va='center', fontsize=8.5,
                fontweight='bold', color='white', zorder=3, multialignment='center')

    def decision(cx, cy, s, text):
        diamond = plt.Polygon([(cx,cy+s),(cx+s,cy),(cx,cy-s),(cx-s,cy)],
                               facecolor=C_GOLD, edgecolor='white', lw=2, zorder=2)
        ax.add_patch(diamond)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=8,
                fontweight='bold', color=C_DARK, zorder=3, multialignment='center')

    def down_arrow(x1,y1,x2,y2, label=None, color=C_MID):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2, mutation_scale=14))
        if label:
            ax.text((x1+x2)/2+6, (y1+y2)/2, label, fontsize=8, color=color, fontweight='bold')

    def fork_join(cx, cy, w=300):
        ax.add_patch(FancyBboxPatch((cx-w/2, cy-5), w, 10,
                     boxstyle="square,pad=0", facecolor=C_DARK, zorder=3))

    # ── Swimlanes ──
    ax.add_patch(FancyBboxPatch((20, 50), (W/2-30), H-95,
                 boxstyle="round,pad=2", facecolor=C_RED,
                 edgecolor=C_RED, lw=0, alpha=0.05, zorder=0))
    ax.add_patch(FancyBboxPatch((W/2+10, 50), W/2-30, H-95,
                 boxstyle="round,pad=2", facecolor=C_PURPLE,
                 edgecolor=C_PURPLE, lw=0, alpha=0.05, zorder=0))
    ax.text(W/4, H-48, 'Donor', ha='center', fontsize=10, fontweight='bold', color=C_RED)
    ax.text(3*W/4, H-48, 'Faculty Advisor / System', ha='center', fontsize=10,
            fontweight='bold', color=C_PURPLE)
    ax.axvline(W/2, color=C_LIGHT, lw=1, linestyle='dashed', ymin=0.06, ymax=0.95, zorder=1)

    # ── Flow ──
    start_end(cx, H-70, kind='start')
    down_arrow(cx, H-88, cx, H-128)

    activity(W/4, H-160, 240, 40, 'Fill Donation\nLog Form', C_RED)
    down_arrow(W/4, H-180, W/4, H-215)

    activity(W/4, H-245, 240, 40, 'Submit Form\nPOST /donors/add-donation/', C_RED)
    down_arrow(W/4, H-265, cx, H-300)

    activity(cx, H-330, 280, 40, 'DonationHistory.verification_status\n= "pending"', '#065F46')
    down_arrow(cx, H-350, cx, H-385)

    activity(cx, H-415, 260, 40, 'System creates Notification\nfor Faculty Advisor', C_PURPLE)
    down_arrow(cx, H-435, cx, H-470)

    activity(3*W/4, H-500, 240, 40, 'Advisor reviews\nDonation Record', C_PURPLE)
    down_arrow(3*W/4, H-520, 3*W/4, H-555)

    decision(3*W/4, H-580, 32, 'Approve?')

    # YES branch
    down_arrow(3*W/4, H-612, 3*W/4, H-645, 'YES', C_GREEN)
    activity(3*W/4, H-675, 220, 40, 'Set status = "verified"\nRecord verified_by, verified_at', C_GREEN)
    down_arrow(3*W/4, H-695, cx, H-720)
    activity(cx, H-750, 260, 40, 'Increment donor.total_donations\nCheck achievement milestones', '#065F46')
    down_arrow(cx, H-770, cx, H-800)
    decision(cx, H-820, 26, 'New\nBadge?')
    down_arrow(cx-26, H-820, W/4, H-820, 'YES', C_GOLD)
    activity(W/4, H-820, 200, 36, 'Achievement.objects.create()\nNotify donor', C_GOLD)
    down_arrow(W/4-58, H-820, W/4-80, H-840)
    down_arrow(cx, H-846, cx, H-872, 'NO →')

    # NO branch
    ax.annotate('', xy=(cx-100, H-580), xytext=(3*W/4-32, H-580),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2, mutation_scale=14))
    ax.text(cx+20, H-575, 'NO', fontsize=8, color=C_RED, fontweight='bold')
    activity(cx-155, H-580, 220, 40, 'Set status = "rejected"\nStore rejection_reason', C_RED)
    down_arrow(cx-155, H-600, cx-155, H-635)
    activity(cx-155, H-665, 220, 40, 'Rollback total_donations\nNotify donor of rejection', C_ORANGE)
    ax.annotate('', xy=(cx-165, H-860), xytext=(cx-155, H-685),
                arrowprops=dict(arrowstyle='->', color=C_ORANGE, lw=2, mutation_scale=14))

    start_end(cx, H-875, kind='end')

    ax.text(W/2, 30, 'Red swimlane = Donor actions.  Purple swimlane = Advisor/System actions.',
            ha='center', fontsize=8, color=C_LIGHT)

    plt.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, '07_activity.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 07_activity.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. GANTT CHART
# ══════════════════════════════════════════════════════════════════════════════
def diagram_gantt():
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    tasks = [
        # Phase 1
        ('Phase 1: Planning & Setup',         None,           0,   3,  C_MID,   True),
        ('  Requirements Gathering',           'Shahariar',    0,   2,  C_BLUE,  False),
        ('  Technology Stack Selection',       'All',          1,   2,  C_BLUE,  False),
        ('  Initial Django Project Setup',     'Shahariar',    2,   3,  C_BLUE,  False),
        # Phase 2
        ('Phase 2: Core Backend',              None,           3,   8,  C_MID,   True),
        ('  Custom User Model & Auth',         'Shahariar',    3,   5,  C_RED,   False),
        ('  Donor & BloodGroup Models',        'Moshiur',      3,   5,  C_GREEN, False),
        ('  Blood Request Models',             'Rajash',       4,   6,  C_PURPLE,False),
        ('  Forms & Validators',               'All',          5,   7,  C_RED,   False),
        ('  Basic CRUD Views & URLs',          'Moshiur',      5,   8,  C_GREEN, False),
        # Phase 3
        ('Phase 3: Advanced Features',         None,           7,   14, C_MID,   True),
        ('  9-Role RBAC System',               'Shahariar',    7,   10, C_RED,   False),
        ('  Notification System',              'Moshiur',      8,   11, C_GREEN, False),
        ('  Achievement Engine',               'Moshiur',      9,   12, C_GOLD,  False),
        ('  Donation Drive Module',            'Shahariar',    10,  13, C_ORANGE,False),
        ('  Emergency Broadcast System',       'Shahariar',    11,  14, C_RED,   False),
        ('  Eligibility Checker',              'Rajash',       10,  12, C_PURPLE,False),
        # Phase 4
        ('Phase 4: UI/UX & Animations',        None,           13,  18, C_MID,   True),
        ('  Three.js 3D Homepage',             'Shahariar',    13,  15, C_RED,   False),
        ('  Global Dark Theme (base.html)',    'Shahariar',    14,  16, C_BLUE,  False),
        ('  Dashboard & Profile Redesign',     'Shahariar',    14,  17, C_BLUE,  False),
        ('  Auth Pages (Login/Register)',      'Rajash',       15,  16, C_PURPLE,False),
        ('  Request & Directory Pages',        'Rajash',       15,  17, C_PURPLE,False),
        ('  Advisor & President Dashboards',   'Shahariar',    16,  18, C_RED,   False),
        # Phase 5
        ('Phase 5: Testing & Documentation',   None,           17,  20, C_MID,   True),
        ('  System & Integration Testing',     'All',          17,  19, C_GREEN, False),
        ('  README & GitHub Setup',            'Shahariar',    18,  19, C_BLUE,  False),
        ('  Diagrams & Documentation',         'All',          19,  20, C_GOLD,  False),
        ('  Final Review & Deployment',        'All',          19,  20, C_RED,   False),
    ]

    labels = [t[0] for t in tasks]
    n = len(tasks)
    ax.set_xlim(0, 20)
    ax.set_ylim(-0.5, n - 0.5)
    ax.invert_yaxis()

    months = ['Jan 2025','Feb 2025','Mar 2025','Apr 2025','May 2025',
              'Jun 2025','','','','','Jul 2025']
    month_pos = [0, 2, 5, 9, 13, 17, 20]
    month_lbl = ['Jan','Feb','Mar','Apr','May','Jun']
    for pos, lbl in zip(month_pos[:6], month_lbl):
        ax.axvline(pos, color='#CBD5E1', lw=0.8, linestyle='--', zorder=0)
        ax.text(pos, -0.7, lbl+'\n2025', ha='center', va='top',
                fontsize=8, color=C_MID, fontweight='bold')

    ax.set_xticks([])
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=8)
    ax.tick_params(axis='y', length=0, pad=4)

    # Grid
    for i in range(n):
        ax.axhline(i, color='#F1F5F9', lw=0.7, zorder=0)

    for i, (name, assignee, start, end, color, is_phase) in enumerate(tasks):
        if is_phase:
            ax.add_patch(FancyBboxPatch((start, i-0.38), end-start, 0.75,
                         boxstyle="round,pad=0.5", facecolor=color,
                         alpha=0.18, edgecolor=color, lw=1.5, zorder=1))
            ax.text((start+end)/2, i, name.strip(), ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color=color, zorder=2)
        else:
            ax.add_patch(FancyBboxPatch((start+0.05, i-0.3), end-start-0.1, 0.6,
                         boxstyle="round,pad=0.5", facecolor=color,
                         alpha=0.75, edgecolor='white', lw=0.8, zorder=2))
            if end - start > 1.5:
                ax.text((start+end)/2, i, assignee or '', ha='center', va='center',
                        fontsize=7, fontweight='bold', color='white', zorder=3)

    # Today marker
    ax.axvline(19.5, color=C_RED, lw=2, linestyle='-', zorder=5, alpha=0.8)
    ax.text(19.5, -0.45, 'NOW', ha='center', va='top', fontsize=8,
            color=C_RED, fontweight='bold', zorder=6)

    # Legend
    legend_items = [('Shahariar', C_RED), ('Moshiur', C_GREEN),
                    ('Rajash', C_PURPLE), ('All Team', C_GOLD)]
    for j, (name, col) in enumerate(legend_items):
        ax.add_patch(FancyBboxPatch((0.3 + j*3.5, n+0.15), 0.5, 0.5,
                     boxstyle="round,pad=1", facecolor=col, alpha=0.8,
                     edgecolor='white', lw=0.8))
        ax.text(1.1 + j*3.5, n+0.4, name, fontsize=8, color=C_DARK, va='center')

    ax.set_xlim(0, 20)
    ax.set_ylim(n+0.8, -0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.tick_params(colors=C_MID)
    for label_tick in ax.get_yticklabels():
        label_tick.set_color(C_DARK)
        if label_tick.get_text().startswith('Phase'):
            label_tick.set_fontweight('bold')
            label_tick.set_color(C_RED)

    ax.set_title('UAP-BloodConnect — Project Gantt Chart',
                 fontsize=14, fontweight='bold', color=C_DARK, pad=12)

    plt.tight_layout(pad=0.5)
    fig.savefig(os.path.join(OUT, '08_gantt.png'), dpi=DPI, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print("OK 08_gantt.png")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating UAP-BloodConnect diagrams...")
    print(f"Output: {OUT}\n")
    diagram_architecture()
    diagram_usecase()
    diagram_dfd0()
    diagram_dfd1()
    diagram_er()
    diagram_sequence()
    diagram_activity()
    diagram_gantt()
    print(f"\nALL DONE — 8 diagrams saved to {OUT}")
