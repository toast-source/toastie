import React, { useState, useRef, useEffect } from 'react';
import { Upload, Play, Pause } from 'lucide-react';

interface Frame {
  frame: { x: number; y: number; w: number; h: number };
  duration: number;
}

interface Meta {
  size: { w: number; h: number };
  frameTags: { name: string; from: number; to: number; direction: string }[];
}

interface AsepriteData {
  frames: Frame[];
  meta: Meta;
}

const App = () => {
  const [spriteSheet, setSpriteSheet] = useState<string | null>(null);
  const [animationData, setAnimationData] = useState<AsepriteData | null>(null);
  const [currentTag, setCurrentTag] = useState<string>('');
  const [currentFrameIdx, setCurrentFrameIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timerRef = useRef<number | null>(null);

  // 파일 업로드 처리
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'image' | 'json') => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      if (type === 'image') {
        setSpriteSheet(result);
      } else {
        const json = JSON.parse(result);
        setAnimationData(json);
        if (json.meta.frameTags.length > 0) {
          setCurrentTag(json.meta.frameTags[0].name);
        }
      }
    };
    
    if (type === 'image') reader.readAsDataURL(file);
    else reader.readAsText(file);
  };

  // 애니메이션 루프
  useEffect(() => {
    if (!isPlaying || !animationData || !currentTag) return;

    const tag = animationData.meta.frameTags.find(t => t.name === currentTag);
    if (!tag) return;

    const animate = () => {
      setCurrentFrameIdx(prev => {
        let next = prev + 1;
        if (next > tag.to) next = tag.from;
        return next;
      });

      const frameDuration = animationData.frames[currentFrameIdx]?.duration || 100;
      timerRef.current = window.setTimeout(animate, frameDuration);
    };

    timerRef.current = window.setTimeout(animate, animationData.frames[currentFrameIdx]?.duration || 100);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [isPlaying, animationData, currentTag, currentFrameIdx]);

  // 캔버스 그리기
  useEffect(() => {
    if (!canvasRef.current || !spriteSheet || !animationData) return;

    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.src = spriteSheet;
    img.onload = () => {
      const frameData = animationData.frames[currentFrameIdx].frame;
      ctx.clearRect(0, 0, canvasRef.current!.width, canvasRef.current!.height);
      ctx.imageSmoothingEnabled = false; // 도트 느낌 유지
      ctx.drawImage(
        img,
        frameData.x, frameData.y, frameData.w, frameData.h,
        0, 0, canvasRef.current!.width, canvasRef.current!.height
      );
    };
  }, [currentFrameIdx, spriteSheet, animationData]);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Aseprite Viewer</h1>
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
        <div>
          <label>Spritesheet (PNG): </label>
          <input type="file" accept="image/png" onChange={(e) => handleFileUpload(e, 'image')} />
        </div>
        <div>
          <label>Data (JSON): </label>
          <input type="file" accept="application/json" onChange={(e) => handleFileUpload(e, 'json')} />
        </div>
      </div>

      {animationData && (
        <div style={{ marginBottom: '20px' }}>
          <h3>Tags</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            {animationData.meta.frameTags.map(tag => (
              <button 
                key={tag.name}
                onClick={() => {
                  setCurrentTag(tag.name);
                  setCurrentFrameIdx(tag.from);
                }}
                style={{
                  padding: '8px 16px',
                  backgroundColor: currentTag === tag.name ? '#007bff' : '#f0f0f0',
                  color: currentTag === tag.name ? 'white' : 'black',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <canvas 
          ref={canvasRef} 
          width={128} 
          height={128} 
          style={{ border: '2px solid #ccc', backgroundColor: '#333', marginBottom: '10px', imageRendering: 'pixelated' }}
        />
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => setIsPlaying(!isPlaying)}>
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
