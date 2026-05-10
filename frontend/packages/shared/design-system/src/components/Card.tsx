import React from 'react';

interface CardProps {
  children: React.ReactNode;
  padding?: 'md' | 'lg';
  style?: React.CSSProperties;
  onClick?: () => void;
}

const paddings = { md: 20, lg: 32 };

export const Card: React.FC<CardProps> = ({ children, padding = 'md', style, onClick }) => (
  <div
    style={{
      background: 'var(--color-bg-secondary)',
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-sm)',
      padding: paddings[padding],
      transition: 'box-shadow var(--transition-normal)',
      cursor: onClick ? 'pointer' : undefined,
      ...style,
    }}
    onMouseEnter={e => { if (onClick) (e.currentTarget as HTMLDivElement).style.boxShadow = 'var(--shadow-md)'; }}
    onMouseLeave={e => { if (onClick) (e.currentTarget as HTMLDivElement).style.boxShadow = 'var(--shadow-sm)'; }}
    onClick={onClick}
  >
    {children}
  </div>
);
