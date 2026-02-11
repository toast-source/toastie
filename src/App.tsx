import React, { useState, useRef, useEffect } from 'react';
import pako from 'pako';

const App: React.FC = () => {
  const [sprite, setSprite] = useState<any>(null);
  const [log, setLog] = useState<string>('Ready');
  const [tagInfo, setTagInfo] = useState<string>('None');
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const keys = useRef<Record<string, boolean>>({});
  
  const engine = useRef({
    x: 400, y: 300, vx: 0, vy: 0,
    grounded: false, facing: 1,
    frame: 0, anim: 0, active: false
  });

  const parseAse = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLog(`Parsing: ${file.name}`);
    
    try {
      const buf = await file.arrayBuffer();
      const view = new DataView(buf);
      const bytes = new Uint8Array(buf);
      
      const w = view.getUint16(8, true);
      const h = view.getUint16(10, true);
      const numFrames = view.getUint16(4, true);
      const depth = view.getUint16(12, true);
      
      let offset = 128;
      const frames: HTMLCanvasElement[] = [];
      const tags: any[] = [];
      const palette = new Uint8Array(256 * 4);

      for (let f = 0; f < numFrames; f++) {
        const frameSize = view.getUint32(offset, true);
        let chunkCount = view.getUint16(offset + 6, true);
        if (chunkCount === 0xFFFF) chunkCount = view.getUint32(offset + 12, true);
        
        const canvas = document.createElement('canvas');
        canvas.width = w; canvas.height = h;
        const ctx = canvas.getContext('2d')!;

        let chunkOffset = offset + 16;
        for (let c = 0; c < chunkCount; c++) {
          if (chunkOffset + 6 > buf.byteLength) break;
          const chunkSize = view.getUint32(chunkOffset, true);
          const chunkType = view.getUint16(chunkOffset + 4, true);

          if (chunkType === 0x2019) { // Palette (Corrected Offset: 26)
            const firstIdx = view.getUint32(chunkOffset + 10, true);
            const lastIdx = view.getUint32(chunkOffset + 14, true);
            let ptr = chunkOffset + 26; 
            for (let i = firstIdx; i <= lastIdx; i++) {
              if (ptr + 6 > buf.byteLength) break;
              const flags = view.getUint16(ptr, true);
              palette[i * 4] = view.getUint8(ptr + 2);
              palette[i * 4 + 1] = view.getUint8(ptr + 3);
              palette[i * 4 + 2] = view.getUint8(ptr + 4);
              palette[i * 4 + 3] = view.getUint8(ptr + 5);
              ptr += 6;
              if (flags & 1) ptr += 2 + view.getUint16(ptr, true);
            }
          } 
          else if (chunkType === 0x2005) { // Cel
            const cx = view.getInt16(chunkOffset + 8, true);
            const cy = view.getInt16(chunkOffset + 10, true);
            const opacity = view.getUint8(chunkOffset + 12);
            if (view.getUint16(chunkOffset + 14, true) === 2) {
              const cw = view.getUint16(chunkOffset + 22, true);
              const ch = view.getUint16(chunkOffset + 24, true);
              const raw = pako.inflate(bytes.subarray(chunkOffset + 26, chunkOffset + chunkSize));
              const id = ctx.createImageData(cw, ch);
              for (let i = 0; i < cw * ch; i++) {
                if (depth === 32) {
                  id.data[i*4]=raw[i*4]; id.data[i*4+1]=raw[i*4+1]; id.data[i*4+2]=raw[i*4+2];
                  id.data[i*4+3]=(raw[i*4+3] * opacity) / 255;
                } else if (depth === 8) {
                  const idx = raw[i];
                  id.data[i*4]=palette[idx*4]; id.data[i*4+1]=palette[idx*4+1]; id.data[i*4+2]=palette[idx*4+2];
                  id.data[i*4+3]=(palette[idx*4+3] * opacity) / 255;
                }
              }
              ctx.putImageData(id, cx, cy);
            }
          } 
          else if (chunkType === 0x2018) { // Tags
            const count = view.getUint16(chunkOffset + 6, true);
            let tPtr = chunkOffset + 16;
            for (let i = 0; i < count; i++) {
              if (tPtr + 19 > buf.byteLength) break;
              const from = view.getUint16(tPtr, true);
              const to = view.getUint16(tPtr + 2, true);
              const nameLen = view.getUint16(tPtr + 17, true);
              const name = new TextDecoder().decode(bytes.subarray(tPtr + 19, tPtr + 19 + nameLen));
              tags.push({ name, from, to });
              tPtr += 19 + nameLen;
            }
          }
          chunkOffset += chunkSize;
        }
        frames.push(canvas);
        offset += frameSize;
      }
      
      engine.current.x = 400; engine.current.y = 100;
      engine.current.vx = 0; engine.current.vy = 0;
      engine.current.active = true;
      
      setSprite({ frames, tags, w, h });
      setLog(`Ready: ${frames.length} frames.`);
    } catch (err: any) {
      setLog(`Error: ${err.message}`);
    }
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { keys.current[e.code] = e.type === 'keydown'; };
    window.addEventListener('keydown', onKey);
    window.addEventListener('keyup', onKey);

    let raf: number;
    const tick = () => {
      const e = engine.current;
      const ctx = canvasRef.current?.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#050505'; ctx.fillRect(0, 0, 800, 500);
        ctx.fillStyle = '#111'; ctx.fillRect(0, 400, 800, 100);

        if (sprite && e.active) {
          e.vx *= 0.82; e.vy += 0.85;
          if (keys.current['ArrowRight']) { e.vx = 5; e.facing = 1; }
          if (keys.current['ArrowLeft']) { e.vx = -5; e.facing = -1; }
          if ((keys.current['Space'] || keys.current['ArrowUp']) && e.grounded) { e.vy = -16; e.grounded = false; }
          
          e.x += e.vx; e.y += e.vy;
          const scale = 4;
          if (e.y + sprite.h * scale > 400) { e.y = 400 - sprite.h * scale; e.vy = 0; e.grounded = true; }
          
          if (e.x < 0) e.x = 0;
          if (e.x > 800 - sprite.w * scale) e.x = 800 - sprite.w * scale;

          const state = !e.grounded ? 'jump' : (Math.abs(e.vx) > 0.5 ? 'move' : 'idle');
          const tag = sprite.tags.find((t:any) => t.name.toLowerCase() === state) || 
                      (sprite.tags[0] || { from: 0, to: sprite.frames.length - 1 });
          
          setTagInfo(tag.name);

          e.anim++;
          if (e.anim > 6) {
            e.frame++;
            if (e.frame > tag.to || e.frame < tag.from) e.frame = tag.from;
            e.anim = 0;
          }

          ctx.save(); ctx.imageSmoothingEnabled = false;
          if (e.facing === -1) {
            ctx.translate(e.x + sprite.w * scale, e.y); ctx.scale(-1, 1);
            ctx.drawImage(sprite.frames[e.frame], 0, 0, sprite.w * scale, sprite.h * scale);
          } else {
            ctx.drawImage(sprite.frames[e.frame], e.x, e.y, sprite.w * scale, sprite.h * scale);
          }
          ctx.restore();
        }
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('keyup', onKey);
      cancelAnimationFrame(raf);
    };
  }, [sprite]);

  return (
    <div style={{ backgroundColor: '#000', color: '#fff', minHeight: '100vh', padding: '20px', fontFamily: 'monospace' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h2 style={{ color: '#3b82f6', margin: 0 }}>ASE-PLAYER PRO</h2>
          <label style={{ background: '#fff', color: '#000', padding: '6px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            UPLOAD FILE
            <input type="file" onChange={parseAse} style={{ display: 'none' }} />
          </label>
        </div>
        <div style={{ color: '#444', marginBottom: '10px', fontSize: '12px' }}>{log}</div>
        <canvas ref={canvasRef} width={800} height={500} style={{ width: '100%', border: '1px solid #222' }} />
        <div style={{ marginTop: '15px', display: 'flex', gap: '30px', fontSize: '12px', color: '#666' }}>
          <div>POS: {Math.round(engine.current.x)}, {Math.round(engine.current.y)}</div>
          <div>TAG: <span style={{color:'#3b82f6'}}>{tagInfo}</span></div>
          <div>GROUND: {engine.current.grounded ? 'YES' : 'NO'}</div>
        </div>
      </div>
    </div>
  );
};

export default App;
