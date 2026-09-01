import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Circle, PathPatch
from matplotlib.path import Path as MPath
import matplotlib as mpl
from pathlib import Path as FSPath
mpl.rcParams['font.family']='Inter'
F=FSPath(__file__).resolve().parents[1] / 'outputs' / 'figures'
MID='#06121E'; DEEP='#0B3150'; WHITE='#F8FBFF'; TEAL='#23D6C5'; MEM='#4DA3FF'; CAS='#FF735D'; PUR='#8E72FF'; MUT='#9BB0C2'; GOLD='#FFCE6A'
fig=plt.figure(figsize=(14.14,10),dpi=180,facecolor=MID)
ax=fig.add_axes([0,0,1,1]); arr=np.vstack([np.linspace(0,1,800)]*2); cmap=LinearSegmentedColormap.from_list('g',[MID,DEEP]); ax.imshow(arr,aspect='auto',cmap=cmap,extent=[0,1,0,1]); ax.axis('off')
# route motif
verts=[(.58,.12),(.70,.20),(.67,.37),(.82,.45),(.78,.66),(.91,.74),(1.05,.84)]
codes=[MPath.MOVETO]+[MPath.CURVE3]*(len(verts)-1)
ax.add_patch(PathPatch(MPath(verts,codes),transform=ax.transAxes,fill=False,edgecolor=TEAL,lw=3,alpha=.34))
for x,y in [verts[0],verts[2],verts[4],verts[5]]:
    ax.add_patch(Circle((x,y),.014,transform=ax.transAxes,facecolor=MID,edgecolor=TEAL,lw=2.2,alpha=.55))
# glow circles
for r,a,c in [(.29,.055,MEM),(.20,.06,TEAL),(.12,.08,PUR)]:ax.add_patch(Circle((.87,.58),r,transform=ax.transAxes,facecolor=c,edgecolor='none',alpha=a))
# top brand
fig.text(.065,.90,'CYCLISTIC',color=WHITE,fontsize=15,fontweight='bold')
fig.text(.164,.901,'DATA ANALYTICS PORTFOLIO',color=TEAL,fontsize=9.5,fontweight='bold')
# main title
fig.text(.065,.72,'Turning ride behavior\ninto membership growth',color=WHITE,fontsize=39,fontweight='bold',linespacing=.98)
fig.text(.068,.575,'End-to-end customer behavior analysis · 3.82M trips · January-December 2019',color=MUT,fontsize=12)
# business question card
fig.patches.append(FancyBboxPatch((.065,.40),.53,.115,boxstyle='round,pad=.004,rounding_size=.018',transform=fig.transFigure,facecolor='#0E2A40',edgecolor='#27526B',lw=1.2))
fig.text(.088,.476,'BUSINESS QUESTION',color=GOLD,fontsize=8.5,fontweight='bold')
fig.text(.088,.434,'How do annual members and casual riders use Cyclistic differently -\nand where should conversion effort be concentrated?',color=WHITE,fontsize=13,fontweight='bold',linespacing=1.2)
# 4 metric cards
cards=[('76.9%','member share',MEM),('2.6×','longer casual median',CAS),('2.3×','more weekend-led',PUR),('7.3×','more same-station',TEAL)]
for i,(v,l,c) in enumerate(cards):
    x=.065+i*.214
    fig.patches.append(FancyBboxPatch((x,.15),.19,.16,boxstyle='round,pad=.005,rounding_size=.02',transform=fig.transFigure,facecolor='#0E2A40',edgecolor='#265068',lw=1.1))
    fig.patches.append(FancyBboxPatch((x+.012,.176),.008,.108,boxstyle='round,pad=0,rounding_size=.004',transform=fig.transFigure,facecolor=c,edgecolor='none'))
    fig.text(x+.033,.235,v,color=WHITE,fontsize=23,fontweight='bold')
    fig.text(x+.033,.185,l.upper(),color=MUT,fontsize=8.1,fontweight='bold')
fig.text(.065,.07,'Python · Pandas · NumPy · SQL · data quality · behavioral analytics · executive storytelling',color='#7891A5',fontsize=8.6)
fig.savefig(F/'00_report_cover.png',dpi=180,bbox_inches='tight',pad_inches=0,facecolor=fig.get_facecolor())
plt.close(fig)
