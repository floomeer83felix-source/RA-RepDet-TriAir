from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent / 'figures'
OUT.mkdir(exist_ok=True)

# Fig 1: architecture schematic
fig, ax = plt.subplots(figsize=(12, 4.6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.5)
ax.axis('off')

def box(x,y,w,h,label,fc,ec='#333333', fs=9):
    p = FancyBboxPatch((x,y),w,h, boxstyle='round,pad=0.03,rounding_size=0.08',
                       linewidth=1.1, edgecolor=ec, facecolor=fc)
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=fs,wrap=True)
    return p

def arrow(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,
                                 linewidth=1.15,color='#333333'))

box(0.2, 3.8, 1.4, 0.7, 'RGB\n3 channels', '#dceeff')
box(0.2, 2.5, 1.4, 0.7, 'Thermal\n1 channel', '#ffe5d1')
box(0.2, 1.2, 1.4, 0.7, 'Event\n1 channel', '#e3f3df')
box(2.0,3.8,1.4,0.7,'RGB stem\n3x3 conv-BN-SiLU','#dceeff')
box(2.0,2.5,1.4,0.7,'Thermal stem\n3x3 conv-BN-SiLU','#ffe5d1')
box(2.0,1.2,1.4,0.7,'Event stem\n3x3 conv-BN-SiLU','#e3f3df')
for yy in [4.15,2.85,1.55]: arrow(1.6,yy,2.0,yy)
box(4.0,2.05,1.7,1.45,'GAP +\nreliability MLP\nsoftmax weights', '#f5ebff')
for yy in [4.15,2.85,1.55]: arrow(3.4,yy,4.0,2.78)
box(6.2,2.05,1.55,1.45,'Weighted\nfeature fusion', '#f5ebff')
arrow(5.7,2.78,6.2,2.78)
box(8.15,2.05,1.3,1.45,'3-channel\nprojection', '#f0f0f0')
arrow(7.75,2.78,8.15,2.78)
box(9.9,2.05,1.6,1.45,'RepViT + FPN\n+ FCOS', '#e8edf6')
arrow(9.45,2.78,9.9,2.78)
arrow(11.5,2.78,11.9,2.78)
ax.text(11.95,2.78,'Vehicle\ndetections',ha='left',va='center',fontsize=9)
box(3.9,0.25,4.8,0.9,'Training only: independent modality dropout with p=0.15; if all streams are dropped, one stream is restored at random.', '#fff7cc', fs=8.5)
ax.text(0.15,5.05,'Five-channel TriAir sample',fontsize=10,fontweight='bold')
ax.text(7.6,4.95,'Full modalities at ordinary inference',fontsize=9,fontstyle='italic')
fig.tight_layout()
fig.savefig(OUT/'fig1_method.pdf', bbox_inches='tight')
plt.close(fig)

# Fig 2: audit/split protocol
fig, ax = plt.subplots(figsize=(11.6, 4.3))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.2)
ax.axis('off')

def b2(x,y,w,h,label,fc,fs=9):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.03,rounding_size=0.08',linewidth=1.1,edgecolor='#333333',facecolor=fc)
    ax.add_patch(p); ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=fs,wrap=True); return p

def a2(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,linewidth=1.1,color='#333333'))

b2(0.2,2.05,1.65,1.05,'Frozen pre-validation\ntrain + validation\nuniverse: 9,652', '#e8edf6')
a2(1.85,2.58,2.35,2.58)
b2(2.35,2.05,2.15,1.05,'Candidate graph\nexact RGB / pHash / dHash\n+ human-adjudicated\nadjacent observations', '#f5ebff')
a2(4.5,2.58,5.0,2.58)
b2(5.0,2.05,1.7,1.05,'Deterministic\ncomponent assignment\n(no performance input)', '#fff7cc')
a2(6.7,2.58,7.2,2.58)
b2(7.2,3.1,1.55,0.85,'Train\n7,439 images', '#dceeff')
b2(7.2,1.25,1.55,0.85,'Validation\n2,213 images', '#e3f3df')
a2(8.75,3.52,9.25,3.52); a2(8.75,1.67,9.25,1.67)
b2(9.25,2.05,2.2,1.05,'Post-assignment audit\nzero cross-partition\noriginal / human /\nextended graph edges', '#f0f0f0')
ax.text(0.2,4.65,'Component-disjoint validation protocol',fontsize=11,fontweight='bold')
ax.text(0.2,0.35,'Guard partition is archival and excluded from model selection, performance reporting, and test claims.',fontsize=8.8)
fig.tight_layout()
fig.savefig(OUT/'fig2_protocol.pdf', bbox_inches='tight')
plt.close(fig)

metrics = ['AP50','AP75','F1']
early = np.array([0.9408409,0.8207659,0.8944584])
rel = np.array([0.9585693,0.8759667,0.9132822])
early_sd = np.array([0.0047081,0.0203270,0.0078256])
rel_sd = np.array([0.0002081,0.0192475,0.0016391])
x=np.arange(len(metrics)); width=.34
fig,ax=plt.subplots(figsize=(7.8,4.2))
ax.bar(x-width/2,early,width,yerr=early_sd,capsize=4,label='Matched early fusion')
ax.bar(x+width/2,rel,width,yerr=rel_sd,capsize=4,label='Reliability-aware p=0.15')
ax.set_xticks(x,metrics)
ax.set_ylim(.75,.99)
ax.set_ylabel('Two-run mean metric')
ax.grid(axis='y',alpha=.25)
ax.legend(frameon=False,fontsize=9,loc='upper left')
fig.tight_layout()
fig.savefig(OUT/'fig3_core_results.pdf', bbox_inches='tight')
plt.close(fig)

conditions=['All\nmodal','RGB\nremoved','Thermal\nremoved','Event\nremoved']
early_ap=np.array([.9408409,.7378747,.3648492,.9338786])
rel_ap=np.array([.9585693,.8984863,.7030294,.9581662])
x=np.arange(4); width=.34
fig,ax=plt.subplots(figsize=(8.0,4.2))
ax.bar(x-width/2,early_ap,width,label='Matched early fusion')
ax.bar(x+width/2,rel_ap,width,label='Reliability-aware p=0.15')
ax.set_ylim(0,1.0); ax.set_ylabel('AP50'); ax.set_xticks(x,conditions)
ax.grid(axis='y',alpha=.25)
ax.legend(frameon=False,fontsize=9,loc='upper left')
fig.tight_layout()
fig.savefig(OUT/'fig4_channel_removal.pdf', bbox_inches='tight')
plt.close(fig)

methods = ['Scratch\nEqual', 'TriAir Init\nEqual', 'TriAir Init\nReliability']
means = np.array([0.220, 0.233, 0.250])
stds = np.array([0.007, 0.006, 0.008])
x = np.arange(len(methods))
fig, ax = plt.subplots(figsize=(7.6, 4.2))
ax.bar(x, means, yerr=stds, capsize=5)
ax.set_xticks(x, methods)
ax.set_ylabel('COCO AP@[0.50:0.95]')
ax.set_ylim(0.20, 0.265)
ax.grid(axis='y', alpha=.25)
for i, value in enumerate(means):
    ax.text(i, value + stds[i] + 0.0012, f'{value:.3f}', ha='center', va='bottom', fontsize=9)
fig.tight_layout()
fig.savefig(OUT/'fig5_mmuav_transfer.pdf', bbox_inches='tight')
plt.close(fig)
