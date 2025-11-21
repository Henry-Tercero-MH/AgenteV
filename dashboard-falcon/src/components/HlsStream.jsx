import React, { useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import Hls from 'hls.js';

const HlsStream = forwardRef(function HlsStream({ src }, ref) {
  const videoRef = useRef(null);
  const HLS_URL = src || '/hls/stream.m3u8';

  useImperativeHandle(ref, () => ({
    getVideoElement: () => videoRef.current
  }));

  useEffect(() => {
    if (videoRef.current) {
      if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(HLS_URL);
        hls.attachMedia(videoRef.current);
        return () => {
          hls.destroy();
        };
      } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
        videoRef.current.src = HLS_URL;
      }
    }
  }, [HLS_URL]);

  return (
    <div className="rounded-lg shadow-lg bg-black p-2 flex flex-col items-center">
      <h3 className="text-lg font-bold text-white mb-2">Vista en Vivo - Canal 2 (HLS)</h3>
      <video
        ref={videoRef}
        controls
        autoPlay
        style={{ width: '100%', maxWidth: 640, borderRadius: 8 }}
      />
    </div>
  );
});

export default HlsStream;
