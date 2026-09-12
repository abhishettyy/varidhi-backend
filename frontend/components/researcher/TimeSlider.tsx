'use client';

import React, { useState } from 'react';
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react';

interface TimeSliderProps {
  onTimeChange?: (dayIndex: number) => void;
}

export const TimeSlider: React.FC<TimeSliderProps> = ({ onTimeChange }) => {
  const timeSteps = [
    { label: '-6D', date: '05 Sep' },
    { label: '-5D', date: '06 Sep' },
    { label: '-4D', date: '07 Sep' },
    { label: '-3D', date: '08 Sep' },
    { label: '-2D', date: '09 Sep' },
    { label: 'YEST', date: '10 Sep' },
    { label: 'TODAY', date: '11 Sep' },
    { label: '+24H', date: '12 Sep' },
    { label: '+48H', date: '13 Sep' },
  ];

  const [currentIndex, setCurrentIndex] = useState(6);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleSliderChange = (newIndex: number) => {
    setCurrentIndex(newIndex);
    if (onTimeChange) onTimeChange(newIndex);
  };

  const handleTogglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div
      style={{
        padding: '8px 18px',
        backgroundColor: '#f6f3f1',
        border: '1px solid #cecac8',
        borderRadius: '100px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        boxShadow: '0 4px 16px rgba(36, 36, 36, 0.08)',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Play / Step Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <button
          type="button"
          onClick={() => handleSliderChange(Math.max(0, currentIndex - 1))}
          style={{
            background: 'none',
            border: 'none',
            color: '#767371',
            cursor: 'pointer',
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <SkipBack size={13} />
        </button>

        <button
          type="button"
          onClick={handleTogglePlay}
          style={{
            width: 28,
            height: 28,
            borderRadius: '9999px',
            backgroundColor: '#2b59d1',
            border: 'none',
            color: '#f6f3f1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'opacity 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.9')}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
        >
          {isPlaying ? <Pause size={12} /> : <Play size={12} />}
        </button>

        <button
          type="button"
          onClick={() => handleSliderChange(Math.min(timeSteps.length - 1, currentIndex + 1))}
          style={{
            background: 'none',
            border: 'none',
            color: '#767371',
            cursor: 'pointer',
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <SkipForward size={13} />
        </button>
      </div>

      {/* Date Pill Ticks */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flex: 1 }}>
        {timeSteps.map((step, idx) => {
          const isActive = idx === currentIndex;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => handleSliderChange(idx)}
              style={{
                flex: 1,
                padding: '4px 6px',
                borderRadius: '100px',
                border: isActive ? 'none' : '1px solid #cecac8',
                backgroundColor: isActive ? '#242424' : '#ffffff',
                color: isActive ? '#f6f3f1' : '#767371',
                fontSize: '10px',
                fontWeight: 500,
                cursor: 'pointer',
                textAlign: 'center',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
                fontFamily: 'inherit',
              }}
            >
              <div>{step.label}</div>
              <div style={{ fontSize: '9px', opacity: isActive ? 0.9 : 0.6 }}>{step.date}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
