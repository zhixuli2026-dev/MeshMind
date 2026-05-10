import React from 'react';

export const Input: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = ({ style, ...props }) => (
  <input
    style={{
      width: '100%', padding: '12px 16px', fontSize: 15,
      border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)',
      background: 'var(--color-bg-secondary)', color: 'var(--color-text-primary)',
      outline: 'none', fontFamily: 'inherit',
      transition: 'border-color var(--transition-fast)',
      ...style,
    }}
    {...props}
  />
);
