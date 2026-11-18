#!/usr/bin/env python3
"""Build simple, readable ASTR paper from committed V17 Markdown.
Output is an editable Word manuscript. PDF export handled by workflow.
Scientific numbers are drawn from the frozen GitHub research results.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SRC = Path("NOV18_FINAL_PAPER_V17_PLAIN_ENGLISH_DRAFT.md")
OUT = Path("build/ASTR_V17_Plain_English_Final_Paper.docx")
FIGDIR = Path("build/figures")

def add_inline(p, text):
    # Our source uses a small, controlled subset of Markdown. Preserve citation
    # numbers and figure names, and avoid third-party Markdown conversion drift.
    bits = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text)
    for bit in bits:
        if not bit:
            continue
        if bit.startswith("**") and bit.endswith("**"):
            r=p.add_run(bit[2:-2]);r.bold=True
        elif bit.startswith("*") and bit.endswith("*"):
            r=p.add_run(bit[1:-1]);r.italic=True
        else:
            p.add_run(bit)

def set_cell_shading(cell, fill="F2F2F2"):
    tcPr=cell._tc.get_or_add_tcPr()
    shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill);tcPr.append(shd)

def set_cell_margin(cell, top=85, start=100, bottom=85, end=100):
    tc=cell._tc;tcPr=tc.get_or_add_tcPr();mar=tcPr.first_child_found_in('w:tcMar')
    if mar is None: mar=OxmlElement('w:tcMar');tcPr.append(mar)
    for tag,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        element=mar.find(qn('w:'+tag))
        if element is None: element=OxmlElement('w:'+tag);mar.append(element)
        element.set(qn('w:w'),str(val));element.set(qn('w:type'),'dxa')

def make_figures():
    FIGDIR.mkdir(parents=True,exist_ok=True)
    # Compare the actual Q8-based forecast windows against the retrospective NASA
    # period comparison. These are NOT independent sensitivity estimates.
    quarters=[9,10,11,12,13]
    original=[492.504880,137.937071,89.140443,-111.743365,-97.244761]
    nasa=[513.649670,511.766557,528.151415,512.788576,557.876066]
    fig,ax=plt.subplots(figsize=(7.1,3.1))
    ax.plot(quarters,original,marker='o',linewidth=1.6,label='Original Q8 period')
    ax.plot(quarters,nasa,marker='s',linewidth=1.6,label='NASA period (checked afterward)')
    ax.axhline(0,linewidth=.6)
    ax.set(xticks=quarters,xlabel='Later Kepler observing quarter',
           ylabel='Mean brightness dip (parts per million)')
    ax.legend(frameon=False,fontsize=8)
    ax.grid(axis='y',alpha=.18)
    fig.tight_layout()
    fig.savefig(FIGDIR/'future_transit_windows.png',dpi=180);plt.close(fig)

    methods=['Signal strength alone','Logistic regression','Random forest']
    values=[52.32,77.27,81.59]
    fig,ax=plt.subplots(figsize=(7.1,2.3))
    bars=ax.barh(methods,values)
    ax.set_xlim(0,100)
    ax.set_xlabel('Agreement with NASA historical labels (%)')
    ax.invert_yaxis()
    for b,v in zip(bars,values):
        ax.text(v+1,b.get_y()+b.get_height()/2,f'{v:.1f}%',va='center',fontsize=8)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGDIR/'ml_label_agreement.png',dpi=180);plt.close(fig)

    n=[0,6,12,18,24,30,36]
    drift=[i*abs(13.7223682-13.7133429855)*24 for i in n]
    fig,ax=plt.subplots(figsize=(7.1,2.6))
    ax.plot(n,drift,marker='o',linewidth=1.6)
    ax.set(xlabel='Number of orbits since the starting transit',
           ylabel='Difference between two clock predictions (hours)')
    ax.grid(alpha=.18)
    fig.tight_layout()
    fig.savefig(FIGDIR/'period_drift_hours.png',dpi=180);plt.close(fig)

def caption(doc,txt):
    p=doc.add_paragraph(style='Caption');add_inline(p,txt)
    p.paragraph_format.keep_with_next=False

def insert_fig(doc,name,cap):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(2)
    r=p.add_run();r.add_picture(str(FIGDIR/name),width=Inches(5.9))
    caption(doc,cap)

def setup(doc):
    sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=Inches(.72);sec.bottom_margin=Inches(.68)
    sec.left_margin=Inches(.92);sec.right_margin=Inches(.92)
    styles=doc.styles
    st=styles['Normal'];st.font.name='Times New Roman';st.font.size=Pt(10.8)
    st.paragraph_format.space_after=Pt(5);st.paragraph_format.line_spacing=1.12
    for nm,sz,bef,aft in [('Title',16,0,7),('Heading 1',12.6,12,5),
                           ('Heading 2',11.3,9,3),('Caption',9.2,3,7)]:
        s=styles[nm];s.font.name='Times New Roman';s.font.size=Pt(sz);s.font.color.rgb=RGBColor(0,0,0)
        s.font.bold=(nm!='Caption')
        s.paragraph_format.space_before=Pt(bef);s.paragraph_format.space_after=Pt(aft)
        s.paragraph_format.keep_with_next=(nm!='Caption')
    styles['Caption'].font.italic=True
    foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    f=foot.add_run('');f.font.name='Times New Roman';f.font.size=Pt(9)
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)
    return doc

def parse_doc(doc, lines):
    i=0;inside_refs=False;inside_check=False
    n_body_words=0;did_period=False;did_ml=False;did_future=False
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line.startswith('# '):
            p=doc.add_paragraph(style='Title');add_inline(p,line[2:]);i+=1;continue
        if line.startswith('## '):
            heading=line[3:]
            if heading=='References':
                inside_refs=True
            if heading=='Project Elements Checklist Form':
                inside_check=True
                doc.add_page_break()
            p=doc.add_paragraph(style='Heading 1');add_inline(p,heading)
            i+=1;continue
        if line.startswith('### '):
            p=doc.add_paragraph(style='Heading 2');add_inline(p,line[4:]);i+=1;continue
        if line.startswith('|'):
            tablelines=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                tablelines.append(lines[i].strip());i+=1
            rows=[[c.strip() for c in l.strip('|').split('|')] for l in tablelines]
            rows=[r for r in rows if not all(re.match(r'^:?[-]+:?$',c) for c in r)]
            if not rows:continue
            table=doc.add_table(rows=len(rows),cols=len(rows[0]))
            table.alignment=WD_TABLE_ALIGNMENT.CENTER
            table.style='Table Grid'
            for ri,row in enumerate(rows):
                for ci,txt in enumerate(row):
                    c=table.cell(ri,ci);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    set_cell_margin(c)
                    c.text=''
                    p=c.paragraphs[0];p.paragraph_format.space_after=Pt(0)
                    add_inline(p,txt)
                    for run in p.runs:
                        run.font.name='Times New Roman';run.font.size=Pt(9.0)
                        if ri==0:run.bold=True
                    if ri==0:set_cell_shading(c)
            for row in table.rows:
                trPr=row._tr.get_or_add_trPr()
                cant=OxmlElement('w:cantSplit');trPr.append(cant)
            if not did_future and not inside_refs and len(rows)==6 and 'Quarter 9' in tablelines[2]:
                insert_fig(doc,'future_transit_windows.png',
                    'Figure 2. The same Q8 prediction starts losing the dips. The NASA-period line is a later explanatory comparison, not a second blind test.')
                did_future=True
            continue
        if line.startswith('**') and line.endswith('**') and not line.startswith('**a)') and len(line)<160:
            p=doc.add_paragraph();add_inline(p,line)
            p.paragraph_format.space_after=Pt(5)
            i+=1;continue
        # Combine wrapped Markdown paragraphs (source paragraphs separated by blanks).
        chunk=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):
            chunk.append(lines[i].strip());i+=1
        txt=' '.join(chunk)
        p=doc.add_paragraph()
        add_inline(p,txt)
        if inside_refs:
            p.paragraph_format.space_after=Pt(4)
            for run in p.runs:run.font.size=Pt(9)
        elif inside_check:
            p.paragraph_format.space_after=Pt(5)
        else:
            n_body_words+=len(re.findall(r'\b[\w-]+\b',re.sub(r'\*','',txt)))
        if not did_period and 'After thirty orbits' in txt:
            insert_fig(doc,'period_drift_hours.png',
                'Figure 1. A small period error grows each time the planet completes another orbit. This line is a calculation, not a new observation.')
            did_period=True
        if not did_ml and 'These are meaningful differences' in txt:
            insert_fig(doc,'ml_label_agreement.png',
                'Figure 3. On 1,619 held-out Kepler signals, the random forest agreed more often with NASA\'s earlier screening labels. The labels are not independent proof of planets.')
            did_ml=True
    return n_body_words

def main():
    md=SRC.read_text(encoding='utf-8')
    make_figures()
    doc=setup(Document())
    words=parse_doc(doc,md.splitlines())
    if words<2500:
        raise SystemExit(f'Main body too short: {words} words')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    doc.save(OUT)
    print('Wrote',OUT,'main-body words (approx)',words)
    print('Figures',len(doc.inline_shapes),'Tables',len(doc.tables))

if __name__=='__main__':
    main()
