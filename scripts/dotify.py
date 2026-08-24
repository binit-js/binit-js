#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

def main():
    p=argparse.ArgumentParser(description="Generate a dot-matrix SVG portrait")
    p.add_argument("image"); p.add_argument("-o","--output",default="assets/portrait")
    p.add_argument("--cols",type=int,default=88); p.add_argument("--equalize",action="store_true")
    p.add_argument("--detail",type=float,default=.5); p.add_argument("--color",action="store_true")
    p.add_argument("--animate",action="store_true"); p.add_argument("--mode",choices=["normal","binary"],default="normal")
    p.add_argument("--circle",action="store_true"); a=p.parse_args()
    im=ImageOps.exif_transpose(Image.open(a.image).convert("RGB"))
    if a.circle:
        s=min(im.size); x=(im.width-s)//2; y=(im.height-s)//2; im=im.crop((x,y,x+s,y+s))
    rows=max(1,round(a.cols*im.height/im.width*.55)); small=im.resize((a.cols,rows),Image.Resampling.LANCZOS)
    gray=ImageOps.grayscale(small)
    if a.equalize: gray=ImageEnhance.Contrast(ImageOps.equalize(gray)).enhance(1+a.detail)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a.cols*10} {rows*10}">']
    if a.animate: parts.append('<style>.dot{opacity:0;animation:in .8s ease forwards}@keyframes in{to{opacity:1}}@media(prefers-reduced-motion:reduce){.dot{animation:none;opacity:1}}</style>')
    for y in range(rows):
        for x in range(a.cols):
            v=gray.getpixel((x,y))/255
            r=.46 if a.mode=="binary" and v<.5 else (.46*(1-v)**.72 if a.mode=="normal" else .03)
            if a.mode=="normal": r=max(r,.03)
            fill="#0285FF"
            if a.color: fill="#%02x%02x%02x"%small.getpixel((x,y))
            delay=f' style="animation-delay:{((x+y*a.cols)%70)/1000:.3f}s"' if a.animate else ''
            parts.append(f'<circle class="dot" cx="{x*10+5}" cy="{y*10+5}" r="{r:.2f}" fill="{fill}"{delay}/>')
    parts.append('</svg>')
    out=Path(a.output).with_suffix('.svg'); out.parent.mkdir(parents=True,exist_ok=True); out.write_text('\n'.join(parts),encoding='utf-8')
    print(out)
if __name__=="__main__": main()
