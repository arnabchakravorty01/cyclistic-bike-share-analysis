from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, PathPatch
from matplotlib.path import Path as MplPath
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe

ROOT = Path('/mnt/data/cyclistic_capstone_portfolio')
T = ROOT/'outputs'/'summary_tables'
F = ROOT/'outputs'/'figures'
F.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Brand system: urban mobility / premium analytics
# ---------------------------------------------------------------------
MIDNIGHT = '#071522'
NAVY = '#0B2239'
NAVY_2 = '#0D2E4E'
SLATE = '#152D43'
PANEL = '#10283D'
PANEL_2 = '#13324B'
WHITE = '#F8FBFF'
TEXT = '#ECF5FF'
MUTED = '#93A9BC'
GRID = '#29475F'
MEM = '#4DA3FF'
MEM_2 = '#2E75EA'
CAS = '#FF735D'
CAS_2 = '#FF9B63'
TEAL = '#23D6C5'
LIME = '#B5E85C'
PURPLE = '#8E72FF'
PINK = '#EE77B7'
GOLD = '#FFCE6A'
LIGHT_BG = '#F4F8FC'
LIGHT_PANEL = '#FFFFFF'
LIGHT_INK = '#10243B'
LIGHT_MUTED = '#657A8F'
LIGHT_GRID = '#DDE7F0'

# Fonts
mpl.rcParams['font.family'] = 'Inter'
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['savefig.bbox'] = 'tight'

# ---------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------
mix = pd.read_csv(T/'membership_mix.csv').set_index('member_casual')
dur = pd.read_csv(T/'duration_summary.csv').set_index('member_casual')
day = pd.read_csv(T/'day_type_usage.csv')
monthly = pd.read_csv(T/'monthly_usage.csv')
hourly = pd.read_csv(T/'hourly_usage.csv')
same = pd.read_csv(T/'same_station_usage.csv').set_index('member_casual')
season = pd.read_csv(T/'seasonal_usage.csv')
hot = pd.read_csv(T/'high_casual_share_stations.csv').head(10)
weekday = pd.read_csv(T/'weekday_usage.csv')
heat = pd.read_csv(T/'day_hour_heatmap.csv')

total_rides = int(mix['rides'].sum())
member_share = float(mix.loc['member','share'])
casual_share = float(mix.loc['casual','share'])
member_median = float(dur.loc['member','median_duration_min'])
casual_median = float(dur.loc['casual','median_duration_min'])
ratio_duration = casual_median/member_median
week = day[day.day_type=='Weekend'].set_index('member_casual')['share']
member_week = float(week['member']); casual_week = float(week['casual'])
ratio_week = casual_week/member_week
summer = season[season.season=='Summer'].set_index('member_casual')['rides']
season_totals = season.groupby('member_casual')['rides'].sum()
member_summer = float(summer['member']/season_totals['member'])
casual_summer = float(summer['casual']/season_totals['casual'])
member_same = float(same.loc['member','same_station_share']); casual_same=float(same.loc['casual','same_station_share'])
ratio_same = casual_same/member_same

# weekday commute shares computed from weekday ride counts by hour
h = hourly.copy()
h['segment_total'] = h.groupby('member_casual')['rides'].transform('sum')
h['share'] = h['rides']/h['segment_total']
# specific weekday metric from README; keep exact vetted values
member_commute = 0.585
casual_commute = 0.374

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def gradient_background(ax, top=MIDNIGHT, bottom=NAVY_2, horizontal=False):
    arr = np.linspace(0,1,512)
    arr = np.vstack([arr,arr]) if not horizontal else np.vstack([arr,arr]).T
    cmap = LinearSegmentedColormap.from_list('bg',[top,bottom])
    ax.imshow(arr, aspect='auto', cmap=cmap, extent=[0,1,0,1], transform=ax.transAxes, zorder=-100)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

def rounded(fig, x,y,w,h, fc, ec=None, radius=.02, lw=1, alpha=1, shadow=False, z=1):
    if shadow:
        fig.patches.append(FancyBboxPatch((x+.003,y-.004),w,h,
            boxstyle=f'round,pad=0.005,rounding_size={radius}', transform=fig.transFigure,
            facecolor='#000000', edgecolor='none', alpha=.16, zorder=z))
    p=FancyBboxPatch((x,y),w,h, boxstyle=f'round,pad=0.005,rounding_size={radius}',
        transform=fig.transFigure, facecolor=fc, edgecolor=ec or fc, linewidth=lw, alpha=alpha, zorder=z+.1)
    fig.patches.append(p)
    return p

def add_route_motif(ax, alpha=.22):
    # abstract mobility route: arcs + nodes, all decorative
    verts=[(0.03,.18),(0.18,.1),(0.22,.32),(0.36,.28),(0.44,.52),(0.60,.45),(0.68,.72),(0.82,.66),(0.98,.82)]
    codes=[MplPath.MOVETO]+[MplPath.CURVE3]*(len(verts)-1)
    path=MplPath(verts,codes)
    patch=PathPatch(path,transform=ax.transAxes,fill=False,edgecolor=TEAL,lw=2.5,alpha=alpha)
    ax.add_patch(patch)
    for x,y in [verts[0],verts[2],verts[4],verts[6],verts[-1]]:
        ax.add_patch(Circle((x,y),.012,transform=ax.transAxes,facecolor=MIDNIGHT,edgecolor=TEAL,lw=1.8,alpha=alpha+.18))

def draw_bike_icon(ax, x=.5, y=.5, scale=1, color=WHITE, alpha=1):
    # compact stylized bike glyph drawn with primitives
    r=.055*scale
    ax.add_patch(Circle((x-.07*scale,y-.03*scale),r,transform=ax.transAxes,fill=False,edgecolor=color,lw=2.2,alpha=alpha))
    ax.add_patch(Circle((x+.08*scale,y-.03*scale),r,transform=ax.transAxes,fill=False,edgecolor=color,lw=2.2,alpha=alpha))
    ax.plot([x-.07*scale,x-.01*scale,x+.03*scale,x+.08*scale],[y-.03*scale,y+.045*scale,y-.03*scale,y-.03*scale],
            transform=ax.transAxes,color=color,lw=2.1,alpha=alpha)
    ax.plot([x-.01*scale,x+.045*scale],[y+.045*scale,y+.045*scale],transform=ax.transAxes,color=color,lw=2.1,alpha=alpha)
    ax.plot([x+.03*scale,x+.055*scale],[y-.03*scale,y+.07*scale],transform=ax.transAxes,color=color,lw=2.1,alpha=alpha)
    ax.plot([x+.045*scale,x+.075*scale],[y+.045*scale,y+.085*scale],transform=ax.transAxes,color=color,lw=2.1,alpha=alpha)

def style_dark_axis(ax, grid='y'):
    ax.set_facecolor('none')
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, labelcolor=MUTED)
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=.8, alpha=.62)
        ax.set_axisbelow(True)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)

def style_light_axis(ax, grid='y'):
    ax.set_facecolor('none')
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, labelcolor=LIGHT_MUTED)
    if grid:
        ax.grid(axis=grid, color=LIGHT_GRID, linewidth=.85, alpha=.9)
        ax.set_axisbelow(True)
    ax.xaxis.label.set_color(LIGHT_MUTED); ax.yaxis.label.set_color(LIGHT_MUTED)

def title_block(fig, x, y, eyebrow, title, subtitle=None, light=False):
    # Keep a deliberate vertical rhythm so long titles never collide with subtitles.
    # All coordinates use top alignment to make spacing stable across renderers.
    ink = LIGHT_INK if light else TEXT; muted = LIGHT_MUTED if light else MUTED
    fig.text(x, y, eyebrow.upper(), fontsize=8.2, fontweight='bold', color=TEAL, va='top')
    fig.text(x, y-.030, title, fontsize=21, fontweight='bold', color=ink, va='top')
    if subtitle:
        fig.text(x, y-.105, subtitle, fontsize=9.2, color=muted, va='top')

def save(fig,name,dpi=180):
    fig.savefig(F/name,dpi=dpi,facecolor=fig.get_facecolor(),bbox_inches='tight',pad_inches=.05)
    plt.close(fig)

# ---------------------------------------------------------------------
# Hero banner
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(16,5.5),dpi=160,facecolor=MIDNIGHT)
ax=fig.add_axes([0,0,1,1]); gradient_background(ax,'#06121E','#0B3150',horizontal=True); add_route_motif(ax,.28)
# large soft glow
for r,a,c in [(.33,.06,MEM),(.22,.07,TEAL),(.13,.11,PURPLE)]:
    ax.add_patch(Circle((.89,.48),r,transform=ax.transAxes,facecolor=c,edgecolor='none',alpha=a))
# brand mark
rounded(fig,.055,.77,.055,.145,WHITE,radius=.018,shadow=True)
logo_ax=fig.add_axes([.058,.785,.049,.115], zorder=6); logo_ax.axis('off'); draw_bike_icon(logo_ax,.5,.5,.72,MEM,1)
fig.text(.125,.855,'CYCLISTIC · PORTFOLIO CASE STUDY',color=TEAL,fontsize=9.5,fontweight='bold',va='center')
fig.text(.055,.67,'Turning ride behavior\ninto membership growth',color=WHITE,fontsize=34,fontweight='bold',va='center',linespacing=.96,
         path_effects=[pe.withStroke(linewidth=.5,foreground=WHITE)])
fig.text(.058,.43,'3.82M trips · full-year customer behavior analysis · Python + SQL + executive storytelling',color='#C7D8E7',fontsize=11.2)
# metrics row
metrics=[('76.9%','member share'),('2.6×','longer casual median'),('2.3×','more weekend-led'),('7.3×','more same-station')]
for i,(v,l) in enumerate(metrics):
    x=.058+i*.19
    rounded(fig,x,.11,.165,.19,'#0E2B42',ec='#224962',radius=.018,lw=.9,alpha=.94)
    fig.text(x+.018,.225,v,color=WHITE,fontsize=19,fontweight='bold')
    fig.text(x+.018,.15,l,color=MUTED,fontsize=8.6)
# right statement
fig.text(.80,.405,'BUSINESS QUESTION',color=GOLD,fontsize=8.4,fontweight='bold')
fig.text(.80,.35,'Where should Cyclistic\nfocus conversion effort?',color=WHITE,fontsize=13.2,fontweight='bold',linespacing=1.15)
save(fig,'00_readme_hero.png',200)

# ---------------------------------------------------------------------
# 01 Membership mix - composition with narrative
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(10,5.4),dpi=160,facecolor=LIGHT_BG)
ax=fig.add_axes([0,0,1,1]); ax.axis('off')
title_block(fig,.06,.91,'Customer mix','A large installed base - and a meaningful conversion pool',
            'Annual members dominate usage, but casual riders still contribute 880K+ trips.',light=True)
# big 100% bar
barax=fig.add_axes([.08,.47,.84,.16]); barax.axis('off')
barax.add_patch(FancyBboxPatch((0,.31),1,.38,boxstyle='round,pad=0,rounding_size=.14',facecolor='#E5EDF5',edgecolor='none'))
barax.add_patch(FancyBboxPatch((0,.31),member_share,.38,boxstyle='round,pad=0,rounding_size=.14',facecolor=MEM_2,edgecolor='none'))
# cover inner right rounding to keep split clean
barax.add_patch(Rectangle((member_share-.035,.31),.035,.38,facecolor=MEM_2,edgecolor='none'))
barax.add_patch(FancyBboxPatch((member_share,.31),casual_share,.38,boxstyle='round,pad=0,rounding_size=.14',facecolor=CAS,edgecolor='none'))
barax.add_patch(Rectangle((member_share,.31),.035,.38,facecolor=CAS,edgecolor='none'))
barax.text(member_share/2,.5,'76.9%\nANNUAL MEMBERS',ha='center',va='center',color=WHITE,fontsize=17,fontweight='bold')
barax.text(member_share+casual_share/2,.5,'23.1%\nCASUAL',ha='center',va='center',color=WHITE,fontsize=13,fontweight='bold')
barax.set_xlim(0,1);barax.set_ylim(0,1)
# bottom cards
for x,v,lab,col in [(.08,'2.94M','member rides',MEM_2),(.39,'880.6K','casual rides',CAS),(.70,'3.82M','rides analyzed',TEAL)]:
    rounded(fig,x,.13,.22,.19,WHITE,ec='#DFE7EF',radius=.02,shadow=True)
    fig.text(x+.025,.235,v,fontsize=20,fontweight='bold',color=LIGHT_INK)
    fig.text(x+.025,.17,lab.upper(),fontsize=8.5,fontweight='bold',color=col)
save(fig,'01_membership_mix.png')

# ---------------------------------------------------------------------
# 02 Median duration - lollipop gap
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(10,5.4),dpi=160,facecolor=LIGHT_BG)
axbg=fig.add_axes([0,0,1,1]); axbg.axis('off')
title_block(fig,.06,.91,'Behavior gap','Casual trips are not just longer - they are 2.6× longer',
            'Median duration is used because a small number of extreme rides distort the mean.',light=True)
ax=fig.add_axes([.11,.24,.78,.45]); style_light_axis(ax,'x')
vals=[member_median,casual_median]; labels=['Annual members','Casual riders']; cols=[MEM_2,CAS]
y=[1,0]
ax.hlines(y,0,vals,color=cols,linewidth=9,alpha=.16)
ax.scatter(vals,y,s=900,c=cols,zorder=5,edgecolors='white',linewidths=5)
for yy,v,c in zip(y,vals,cols):
    ax.text(v,yy,f'{v:.1f}',ha='center',va='center',color='white',fontsize=13,fontweight='bold',zorder=6)
ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=11,fontweight='bold',color=LIGHT_INK)
ax.set_xlim(0,30); ax.set_xticks([0,5,10,15,20,25,30]); ax.set_xlabel('Median ride duration (minutes)',fontsize=9)
# ratio callout
rounded(fig,.68,.66,.22,.13,'#FFF1ED',ec='#FFD5CC',radius=.02)
fig.text(.70,.735,'2.6× LONGER',color=CAS,fontsize=13,fontweight='bold')
fig.text(.70,.695,'casual median trip',color=LIGHT_MUTED,fontsize=8.5)
save(fig,'02_median_duration.png')

# ---------------------------------------------------------------------
# 03 Weekend share - 100% stacked bars
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(10,5.4),dpi=160,facecolor=LIGHT_BG)
axbg=fig.add_axes([0,0,1,1]); axbg.axis('off')
title_block(fig,.06,.91,'Usage context','Casual demand shifts decisively toward the weekend',
            'Weekend concentration is 2.3× higher for casual riders than members.',light=True)
ax=fig.add_axes([.12,.27,.78,.36]); ax.axis('off')
rows=[('Annual members',member_week,MEM_2),('Casual riders',casual_week,CAS)]
for i,(lab,wk,col) in enumerate(rows):
    yy=.72-i*.46
    ax.text(0,yy+.12,lab,fontsize=11,fontweight='bold',color=LIGHT_INK,va='center')
    # weekday segment
    ax.add_patch(FancyBboxPatch((.26,yy),.68*(1-wk),.20,boxstyle='round,pad=0,rounding_size=.08',facecolor='#DDE6EF',edgecolor='none'))
    # weekend segment
    start=.26+.68*(1-wk)
    ax.add_patch(FancyBboxPatch((start,yy),.68*wk,.20,boxstyle='round,pad=0,rounding_size=.08',facecolor=col,edgecolor='none'))
    ax.add_patch(Rectangle((start,yy),min(.05,.68*wk),.20,facecolor=col,edgecolor='none'))
    ax.text(.26+.68*(1-wk)/2,yy+.1,f'{1-wk:.1%}\nweekday',ha='center',va='center',fontsize=9,color=LIGHT_MUTED,fontweight='bold')
    ax.text(start+.68*wk/2,yy+.1,f'{wk:.1%}\nweekend',ha='center',va='center',fontsize=9,color='white',fontweight='bold')
ax.set_xlim(0,1);ax.set_ylim(0,1)
rounded(fig,.69,.65,.21,.14,'#FFF1ED',ec='#FFD5CC',radius=.02)
fig.text(.71,.73,'2.3× HIGHER',color=CAS,fontsize=13,fontweight='bold')
fig.text(.71,.687,'casual weekend concentration',color=LIGHT_MUTED,fontsize=8.2)
save(fig,'03_weekend_share.png')

# ---------------------------------------------------------------------
# 04 Monthly usage - premium trend chart
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(11,6.2),dpi=160,facecolor=MIDNIGHT)
axbg=fig.add_axes([0,0,1,1]); gradient_background(axbg,'#06131F','#0A263E',horizontal=True); add_route_motif(axbg,.10)
fig.text(.055,.91,'SEASONALITY',fontsize=8.5,fontweight='bold',color=TEAL)
fig.text(.055,.855,'Summer is the growth window',fontsize=23,fontweight='bold',color=WHITE)
fig.text(.055,.81,'Casual demand expands dramatically in warm months, then contracts faster than member demand.',fontsize=9.6,color=MUTED)
ax=fig.add_axes([.08,.18,.84,.52]); style_dark_axis(ax,'y')
months=np.arange(1,13)
for typ,label,col in [('member','Annual members',MEM),('casual','Casual riders',CAS)]:
    d=monthly[monthly.member_casual==typ].sort_values('month')
    yy=d.rides.values/1000
    ax.plot(months,yy,color=col,lw=3.1,marker='o',markersize=6,markeredgecolor=MIDNIGHT,markeredgewidth=1.8,label=label,zorder=4)
    ax.fill_between(months,yy,0,color=col,alpha=.08,zorder=1)
ax.axvspan(5.5,8.5,color=GOLD,alpha=.07,zorder=0)
ax.text(7,405,'SUMMER SURGE',color=GOLD,fontsize=8,fontweight='bold',ha='center')
ax.set_xlim(.7,12.3);ax.set_ylim(0,430)
ax.set_xticks(months);ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
ax.set_yticks([0,100,200,300,400]);ax.set_yticklabels(['0','100K','200K','300K','400K'])
ax.legend(frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(0,1.08),labelcolor=TEXT)
ax.annotate('August peak',xy=(8,405),xytext=(9.2,405),color=TEXT,fontweight='bold',fontsize=9,
            arrowprops=dict(arrowstyle='->',color=MUTED,lw=1.1))
# footer callout
rounded(fig,.65,.05,.28,.095,'#10314A',ec='#275169',radius=.018)
fig.text(.67,.105,'56.0%',fontsize=18,fontweight='bold',color=CAS)
fig.text(.748,.105,'of casual rides occur Jun-Aug',fontsize=9.1,color=TEXT,va='center')
save(fig,'04_monthly_usage.png')

# ---------------------------------------------------------------------
# 05 Hourly profile - narrative line chart
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(11,6.2),dpi=160,facecolor=MIDNIGHT)
axbg=fig.add_axes([0,0,1,1]); gradient_background(axbg,'#071522','#0C2940',horizontal=True)
fig.text(.055,.91,'TIME-OF-DAY SIGNAL',fontsize=8.5,fontweight='bold',color=TEAL)
fig.text(.055,.855,'Members cluster around commute windows',fontsize=23,fontweight='bold',color=WHITE)
fig.text(.055,.81,'Casual riders build gradually through midday; member demand forms sharp morning and evening peaks.',fontsize=9.6,color=MUTED)
ax=fig.add_axes([.08,.18,.84,.52]); style_dark_axis(ax,'y')
for typ,label,col in [('member','Annual members',MEM),('casual','Casual riders',CAS)]:
    d=h[h.member_casual==typ].sort_values('hour')
    ax.plot(d.hour,d.share*100,color=col,lw=3,label=label,zorder=4)
    ax.fill_between(d.hour,d.share*100,0,color=col,alpha=.07,zorder=1)
for a,b in [(7,9),(16,18)]: ax.axvspan(a,b,color=MEM,alpha=.08,zorder=0)
ax.text(8,13.9,'AM PEAK',color=MEM,fontsize=8,fontweight='bold',ha='center')
ax.text(17,13.9,'PM PEAK',color=MEM,fontsize=8,fontweight='bold',ha='center')
ax.set_xlim(0,23);ax.set_ylim(0,15)
ax.set_xticks([0,3,6,9,12,15,18,21,23]);ax.set_xlabel('Hour of day')
ax.set_yticks([0,3,6,9,12,15]);ax.set_yticklabels([f'{x}%' for x in [0,3,6,9,12,15]])
ax.legend(frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(0,1.08),labelcolor=TEXT)
rounded(fig,.64,.05,.29,.095,'#10314A',ec='#275169',radius=.018)
fig.text(.66,.105,'58.5%',fontsize=18,fontweight='bold',color=MEM)
fig.text(.744,.105,'member weekday rides in commute windows',fontsize=8.6,color=TEXT,va='center')
save(fig,'05_hourly_profile.png')

# ---------------------------------------------------------------------
# 06 Same-station share - dramatic gap
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(10,5.4),dpi=160,facecolor=LIGHT_BG)
axbg=fig.add_axes([0,0,1,1]); axbg.axis('off')
title_block(fig,.06,.91,'Route behavior','Round-trip behavior is a defining casual signal',
            'Returning to the same station is 7.3× more common among casual riders.',light=True)
ax=fig.add_axes([.12,.25,.76,.36]); style_light_axis(ax,'x')
vals=[member_same*100,casual_same*100]; yy=[1,0]; cols=[MEM_2,CAS]
ax.hlines(yy,0,vals,color=cols,lw=10,alpha=.18)
ax.scatter(vals,yy,s=950,c=cols,edgecolors='white',linewidths=5,zorder=5)
for yv,v,c in zip(yy,vals,cols): ax.text(v,yv,f'{v:.1f}%',ha='center',va='center',color='white',fontsize=12,fontweight='bold',zorder=6)
ax.set_yticks(yy);ax.set_yticklabels(['Annual members','Casual riders'],fontsize=11,fontweight='bold',color=LIGHT_INK)
ax.set_xlim(0,13);ax.set_xticks([0,2,4,6,8,10,12]);ax.set_xticklabels([f'{x}%' for x in [0,2,4,6,8,10,12]])
rounded(fig,.68,.66,.22,.13,'#FFF1ED',ec='#FFD5CC',radius=.02)
fig.text(.70,.735,'7.3× MORE LIKELY',color=CAS,fontsize=12.5,fontweight='bold')
fig.text(.70,.695,'to return to the same station',color=LIGHT_MUTED,fontsize=8.2)
save(fig,'06_same_station_share.png')

# ---------------------------------------------------------------------
# 07 hotspots - ranked opportunity list with volume dots
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(11,7),dpi=160,facecolor=MIDNIGHT)
axbg=fig.add_axes([0,0,1,1]); gradient_background(axbg,'#06131F','#0B2B43',horizontal=True)
fig.text(.055,.92,'GEO OPPORTUNITY',fontsize=8.5,fontweight='bold',color=TEAL)
fig.text(.055,.865,'Casual demand clusters around destination stations',fontsize=22,fontweight='bold',color=WHITE)
fig.text(.055,.82,'High-volume stations with the strongest casual share create natural test markets for conversion campaigns.',fontsize=9.5,color=MUTED)
ax=fig.add_axes([.33,.16,.60,.56]); style_dark_axis(ax,'x')
d=hot.iloc[:8].sort_values('casual_share')
y=np.arange(len(d))
# background bars and actual bars
ax.barh(y,np.ones(len(d))*100,color='#18384F',height=.52)
ax.barh(y,d.casual_share*100,color=CAS,height=.52)
ax.scatter(d.casual_share*100,y,s=np.sqrt(d.total_rides)*3.0,color=GOLD,edgecolor=MIDNIGHT,lw=1.2,zorder=5,alpha=.95)
for i,(share,total) in enumerate(zip(d.casual_share*100,d.total_rides)):
    ax.text(share+1.2,i,f'{share:.0f}%',va='center',color=WHITE,fontsize=9,fontweight='bold')
ax.set_yticks(y);ax.set_yticklabels(d.start_station_name,fontsize=9.2,color=TEXT)
ax.set_xlim(0,88);ax.set_xticks([0,20,40,60,80]);ax.set_xticklabels(['0%','20%','40%','60%','80%'])
ax.set_xlabel('Casual share of starts',fontsize=9)
# compact reading key placed below the plot so it never covers station labels
fig.text(.055,.105,'HOW TO READ',fontsize=8.0,fontweight='bold',color=TEAL)
fig.text(.055,.075,'Bar = casual share  ·  Gold bubble = relative annual station volume',fontsize=8.2,color=MUTED)
fig.text(.055,.048,'Top signal: Lake Shore Dr & Monroe St · 79% casual',fontsize=8.2,color=WHITE,fontweight='bold')
save(fig,'07_casual_hotspots.png')

# ---------------------------------------------------------------------
# 08 heatmaps - consistent premium style
# ---------------------------------------------------------------------
# infer columns
# expected: member_casual, day_of_week_name or weekday, hour, rides/share
for segment,col,name in [('member',MEM,'08_heatmap_member.png'),('casual',CAS,'08_heatmap_casual.png')]:
    seg=heat[heat.member_casual==segment].copy()
    day_col = 'day_name' if 'day_name' in seg.columns else ('day_of_week_name' if 'day_of_week_name' in seg.columns else ('day_of_week' if 'day_of_week' in seg.columns else ('weekday' if 'weekday' in seg.columns else None)))
    val_col = 'share' if 'share' in seg.columns else ('rides' if 'rides' in seg.columns else seg.columns[-1])
    if day_col is None:
        # fallback build weekday name from numeric weekday
        day_col='weekday_name'
        seg[day_col]=seg['weekday'].map({0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'})
    days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    p=seg.pivot_table(index=day_col,columns='hour',values=val_col,aggfunc='sum').reindex(days)
    # normalize within segment if using rides
    if val_col=='rides': p=p/p.values.sum()*100
    fig=plt.figure(figsize=(11,5.4),dpi=160,facecolor=MIDNIGHT)
    axbg=fig.add_axes([0,0,1,1]); gradient_background(axbg,'#06131F','#0B2A42',horizontal=True)
    fig.text(.055,.90,'WEEKLY RHYTHM',fontsize=8.5,fontweight='bold',color=TEAL)
    fig.text(.055,.84,f'{segment.title()} demand by day and hour',fontsize=21,fontweight='bold',color=WHITE)
    sub = 'Sharp weekday peaks reveal recurring-use behavior.' if segment=='member' else 'Weekend and midday intensity reveal leisure-oriented demand.'
    fig.text(.055,.79,sub,fontsize=9.4,color=MUTED)
    ax=fig.add_axes([.10,.17,.82,.50])
    cmap=LinearSegmentedColormap.from_list('hm',[PANEL_2,col])
    im=ax.imshow(p.values,aspect='auto',cmap=cmap)
    ax.set_yticks(range(7));ax.set_yticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],color=TEXT,fontweight='bold')
    ax.set_xticks([0,3,6,9,12,15,18,21,23]);ax.set_xticklabels([0,3,6,9,12,15,18,21,23],color=MUTED)
    ax.tick_params(length=0)
    for sp in ax.spines.values():sp.set_visible(False)
    ax.set_xlabel('Hour of day',color=MUTED)
    cb=fig.colorbar(im,ax=ax,fraction=.018,pad=.02);cb.outline.set_visible(False);cb.ax.tick_params(colors=MUTED,length=0,labelsize=8)
    save(fig,name)

# ---------------------------------------------------------------------
# 09 Executive dashboard - full overhaul
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(16,9),dpi=180,facecolor=MIDNIGHT)
bg=fig.add_axes([0,0,1,1]); gradient_background(bg,'#06121E','#0A2B45',horizontal=True); add_route_motif(bg,.075)

# Navigation / brand
rounded(fig,.018,.923,.964,.058,'#0D263B',ec='#21445D',radius=.017,alpha=.96)
logoax=fig.add_axes([.031,.934,.033,.035]);logoax.axis('off');draw_bike_icon(logoax,.5,.5,.72,TEAL)
fig.text(.072,.952,'CYCLISTIC',fontsize=11,fontweight='bold',color=WHITE,va='center')
fig.text(.141,.952,'MEMBERSHIP GROWTH INTELLIGENCE',fontsize=8.4,fontweight='bold',color=MUTED,va='center')
for x,w,txt,fc in [(.74,.11,'2019 FULL YEAR','#173852'),(.86,.105,'3.82M TRIPS','#244D67')]:
    rounded(fig,x,.934,w,.036,fc,ec=fc,radius=.012)
    fig.text(x+w/2,.952,txt,ha='center',va='center',fontsize=7.8,fontweight='bold',color=TEXT)

# Headline: top-aligned blocks keep the eyebrow, title, and opportunity copy separated.
fig.text(.035,.888,'CUSTOMER BEHAVIOR · CONVERSION STRATEGY',fontsize=8.6,fontweight='bold',color=TEAL,va='top')
fig.text(.035,.855,'Casual riders behave differently.\nThat difference reveals where to convert.',fontsize=24.5,fontweight='bold',color=WHITE,linespacing=.98,va='top')
fig.text(.605,.858,'THE OPPORTUNITY',fontsize=8.2,fontweight='bold',color=GOLD,va='top')
fig.text(.605,.828,'Target leisure-heavy moments and locations\nwith a membership message built for context.',fontsize=10.8,color=TEXT,linespacing=1.15,va='top')

# KPI cards
card_y=.675; gap=.012; left=.035; right=.965; n=5; w=(right-left-gap*(n-1))/n; hcard=.098
cards=[
    ('76.9%','MEMBER SHARE','Current base',MEM),
    ('25.8 min','CASUAL MEDIAN','2.6× member',CAS),
    ('43.0%','CASUAL WEEKEND','2.3× member',PURPLE),
    ('56.0%','CASUAL SUMMER','seasonal surge',PINK),
    ('11.9%','SAME-STATION','7.3× member',TEAL),
]
for i,(v,label,sub,col) in enumerate(cards):
    x=left+i*(w+gap)
    rounded(fig,x,card_y,w,hcard,'#0F2A40',ec='#254B63',radius=.018,shadow=True)
    # accent stripe
    fig.patches.append(FancyBboxPatch((x+.009,card_y+.016),.008,hcard-.032,boxstyle='round,pad=0,rounding_size=.004',transform=fig.transFigure,facecolor=col,edgecolor='none',zorder=4))
    fig.text(x+.032,card_y+.062,v,fontsize=18.5,fontweight='bold',color=WHITE)
    fig.text(x+.032,card_y+.034,label,fontsize=7.8,fontweight='bold',color=MUTED)
    fig.text(x+w-.012,card_y+.069,sub.upper(),fontsize=6.8,fontweight='bold',color=col,ha='right')

# Panel coords
# Monthly trend
rounded(fig,.035,.35,.505,.285,'#0D263B',ec='#22465D',radius=.021,shadow=True)
fig.text(.055,.602,'WHEN DEMAND EXPANDS',fontsize=7.6,fontweight='bold',color=TEAL)
fig.text(.055,.572,'Summer creates the conversion window',fontsize=13.4,fontweight='bold',color=WHITE)
fig.text(.055,.548,'Annual trips by month · thousands',fontsize=7.8,color=MUTED)
ax=fig.add_axes([.06,.395,.455,.135], zorder=6);style_dark_axis(ax,'y')
for typ,label,col in [('member','Member',MEM),('casual','Casual',CAS)]:
    d=monthly[monthly.member_casual==typ].sort_values('month')
    yy=d.rides.values/1000
    ax.plot(d.month,yy,color=col,lw=2.6,marker='o',ms=4,label=label,zorder=5)
    ax.fill_between(d.month,yy,0,color=col,alpha=.07)
ax.axvspan(5.5,8.5,color=GOLD,alpha=.055)
ax.set_xlim(.7,12.3);ax.set_ylim(0,430);ax.set_xticks(range(1,13));ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
ax.set_yticks([0,200,400]);ax.set_yticklabels(['0','200K','400K'])
ax.legend(frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(0,1.16),fontsize=7.5,labelcolor=TEXT)

# behavior gap panel right top
rounded(fig,.555,.35,.410,.285,'#0D263B',ec='#22465D',radius=.021,shadow=True)
fig.text(.575,.602,'THE BEHAVIOR GAP',fontsize=7.6,fontweight='bold',color=TEAL)
fig.text(.575,.572,'Casual usage is leisure-shaped',fontsize=13.4,fontweight='bold',color=WHITE)
metrics=[('Median ride',member_median,casual_median,30,'min'),('Weekend',member_week*100,casual_week*100,50,'%'),('Summer',member_summer*100,casual_summer*100,65,'%'),('Same-station',member_same*100,casual_same*100,13,'%')]
ax=fig.add_axes([.58,.39,.36,.155], zorder=6);ax.axis('off')
ax.text(.51,1.02,'MEMBER',color=MEM,fontsize=7.2,fontweight='bold',ha='center',transform=ax.transAxes)
ax.text(.84,1.02,'CASUAL',color=CAS,fontsize=7.2,fontweight='bold',ha='center',transform=ax.transAxes)
for i,(lab,m,c,maxv,unit) in enumerate(metrics):
    yy=.82-i*.24
    ax.text(0,yy,lab,color=TEXT,fontsize=7.8,fontweight='bold',va='center',transform=ax.transAxes)
    for xx,val,col in [(.38,m,MEM),(.70,c,CAS)]:
        ax.add_patch(FancyBboxPatch((xx,yy-.035),.22,.07,boxstyle='round,pad=0,rounding_size=.025',transform=ax.transAxes,facecolor='#183B54',edgecolor='none'))
        ax.add_patch(FancyBboxPatch((xx,yy-.035),.22*min(val/maxv,1),.07,boxstyle='round,pad=0,rounding_size=.025',transform=ax.transAxes,facecolor=col,edgecolor='none'))
        ax.text(xx+.11,yy+.07,f'{val:.1f}{unit}',ha='center',va='bottom',fontsize=6.8,color=MUTED,transform=ax.transAxes)

# bottom left hourly profile
rounded(fig,.035,.105,.445,.215,'#0D263B',ec='#22465D',radius=.021,shadow=True)
fig.text(.055,.285,'WHEN RIDERS START',fontsize=7.6,fontweight='bold',color=TEAL)
fig.text(.055,.258,'Members spike. Casual demand spreads.',fontsize=12.2,fontweight='bold',color=WHITE)
ax=fig.add_axes([.06,.135,.39,.10], zorder=6);style_dark_axis(ax,'y')
for typ,col in [('member',MEM),('casual',CAS)]:
    d=h[h.member_casual==typ].sort_values('hour');ax.plot(d.hour,d.share*100,color=col,lw=2.3)
for a,b in [(7,9),(16,18)]:ax.axvspan(a,b,color=MEM,alpha=.07)
ax.set_xlim(0,23);ax.set_ylim(0,15);ax.set_xticks([0,6,12,18,23]);ax.set_yticks([0,5,10,15]);ax.set_yticklabels(['0','5%','10%','15%'])

# bottom right hotspots
rounded(fig,.495,.105,.470,.215,'#0D263B',ec='#22465D',radius=.021,shadow=True)
fig.text(.515,.285,'WHERE CASUAL RIDERS CLUSTER',fontsize=7.6,fontweight='bold',color=TEAL)
fig.text(.515,.258,'Five high-volume conversion test markets',fontsize=12.2,fontweight='bold',color=WHITE)
ax=fig.add_axes([.67,.135,.26,.105], zorder=6);style_dark_axis(ax,'x')
d=hot.head(5).sort_values('casual_share')
y=np.arange(len(d));ax.barh(y,d.casual_share*100,color=CAS,height=.52)
for i,v in enumerate(d.casual_share*100):ax.text(v+1,i,f'{v:.0f}%',va='center',color=WHITE,fontsize=7,fontweight='bold')
ax.set_yticks(y);ax.set_yticklabels([s.replace('Lake Shore Dr & ','Lake Shore · ').replace('Streeter Dr & ','Streeter · ') for s in d.start_station_name],fontsize=6.8,color=TEXT)
ax.set_xlim(0,85);ax.set_xticks([0,40,80]);ax.set_xticklabels(['0%','40%','80%'])

# Marketing playbook footer
fig.text(.035,.072,'MARKETING PLAYBOOK',fontsize=8,fontweight='bold',color=GOLD)
plays=[
    ('01','GEO-TARGET','High-casual lakefront & destination stations',MEM),
    ('02','TIME IT','Weekends · summer · midday/afternoon',TEAL),
    ('03','TEST THE MESSAGE','Leisure value vs recurring-use convenience',PURPLE),
]
for i,(num,title,desc,col) in enumerate(plays):
    x=.19+i*.255
    fig.add_artist(Circle((x,.067),.013,transform=fig.transFigure,facecolor=col,edgecolor='none',zorder=5))
    fig.text(x,.067,num,ha='center',va='center',fontsize=6.4,fontweight='bold',color=WHITE)
    fig.text(x+.02,.075,title,fontsize=7.4,fontweight='bold',color=TEXT)
    fig.text(x+.02,.052,desc,fontsize=6.5,color=MUTED)

fig.text(.035,.018,'Observed behavior ≠ proven intent. Recommendations are testable hypotheses for privacy-safe experiments.',fontsize=6.8,color='#7890A4')
save(fig,'09_executive_dashboard.png',200)

# ---------------------------------------------------------------------
# 10 insight storyboard for README
# ---------------------------------------------------------------------
fig=plt.figure(figsize=(16,8),dpi=160,facecolor=MIDNIGHT)
bg=fig.add_axes([0,0,1,1]);gradient_background(bg,'#06121E','#0B2A43',horizontal=True)
fig.text(.05,.91,'THE STORY IN FOUR SIGNALS',color=TEAL,fontsize=9,fontweight='bold')
fig.text(.05,.855,'Who uses Cyclistic differently - and why it matters',color=WHITE,fontsize=25,fontweight='bold')
fig.text(.05,.81,'Each signal points to a more targeted membership-conversion strategy.',color=MUTED,fontsize=10)
blocks=[
    (.05,.49,.43,.25,'01','LONGER RIDES',f'{casual_median:.1f} min',f'{ratio_duration:.1f}× member median','Casual trips suggest more experiential use.',CAS),
    (.52,.49,.43,.25,'02','WEEKEND LED',f'{casual_week:.1%}',f'{ratio_week:.1f}× member concentration','Campaign timing should follow casual demand.',PURPLE),
    (.05,.16,.43,.25,'03','SEASONAL',f'{casual_summer:.1%}','of casual trips in summer','Warm months are the acquisition window.',PINK),
    (.52,.16,.43,.25,'04','ROUND-TRIP SIGNAL',f'{casual_same:.1%}',f'{ratio_same:.1f}× member rate','Destination stations become test markets.',TEAL),
]
for x,y,w,h,num,lab,val,sub,desc,col in blocks:
    rounded(fig,x,y,w,h,'#0F2A40',ec='#264A61',radius=.022,shadow=True)
    fig.add_artist(Circle((x+.045,y+h-.055),.021,transform=fig.transFigure,facecolor=col,edgecolor='none',zorder=5))
    fig.text(x+.045,y+h-.055,num,ha='center',va='center',fontsize=7.5,fontweight='bold',color=WHITE)
    fig.text(x+.08,y+h-.047,lab,fontsize=8.5,fontweight='bold',color=MUTED,va='center')
    fig.text(x+.035,y+.11,val,fontsize=28,fontweight='bold',color=WHITE)
    fig.text(x+.22,y+.125,sub,fontsize=10,fontweight='bold',color=col)
    fig.text(x+.035,y+.05,desc,fontsize=8.7,color=MUTED)
save(fig,'10_insight_storyboard.png',190)

print('visual refresh complete')
