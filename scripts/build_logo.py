"""Build the original vector logo and PNG plugin icons. Requires Pillow only for export."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'


def build():
    ASSETS.mkdir(exist_ok=True)
    # Shared geometry: a dashboard connected to a second node through a teal bridge.
    shapes=[
        ('rect',(0,0,512,512),104,'#0f172a',None,0),
        ('rect',(78,162,376,414),32,None,'#e2e8f0',18),
        ('rect',(124,296,166,368),10,'#38bdf8',None,0),
        ('rect',(192,256,234,368),10,'#2dd4bf',None,0),
        ('rect',(260,212,302,368),10,'#a5b4fc',None,0),
        ('line',(302,162,302,118,406,118,406,200),0,None,'#2dd4bf',22),
        ('ellipse',(278,94,326,142),0,'#2dd4bf','#0f172a',10),
        ('rect',(370,184,442,256),20,'#2dd4bf','#0f172a',10),
    ]
    scale=4
    image=Image.new('RGBA',(512*scale,512*scale),(0,0,0,0));draw=ImageDraw.Draw(image)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-labelledby="title desc">',
         '<title id="title">Looker Report Helper</title>',
         '<desc id="desc">A dashboard with three bars connected to a teal node, representing the bridge between an agent and a report.</desc>']
    for kind,box,radius,fill,stroke,width in shapes:
        coords=tuple(v*scale for v in box)
        style=f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"'
        if kind=='rect':
            x1,y1,x2,y2=box
            draw.rounded_rectangle(coords,radius*scale,fill=fill,outline=stroke,width=width*scale)
            svg.append(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="{radius}" {style}/>')
        elif kind=='ellipse':
            draw.ellipse(coords,fill=fill,outline=stroke,width=width*scale)
            x1,y1,x2,y2=box
            svg.append(f'<ellipse cx="{(x1+x2)/2:g}" cy="{(y1+y2)/2:g}" rx="{(x2-x1)/2:g}" ry="{(y2-y1)/2:g}" {style}/>')
        else:
            draw.line(coords,fill=stroke,width=width*scale,joint='curve')
            svg.append('<polyline points="'+' '.join(f'{box[i]},{box[i+1]}' for i in range(0,len(box),2))+f'" {style} stroke-linejoin="round"/>')
    svg.append('</svg>')
    (ASSETS/'logo.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
    for filename,size in [('logo.png',512),('icon.png',128)]:
        image.resize((size,size),Image.Resampling.LANCZOS).save(ASSETS/filename)
    print('Built logo.svg, logo.png and icon.png from shared geometry.')


if __name__=='__main__':
    build()
