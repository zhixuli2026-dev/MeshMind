import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

const styles = {
  base: {
    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
    fontWeight: 500, border: 'none', cursor: 'pointer',
    transition: 'all var(--transition-fast)',
    fontFamily: 'inherit',
  },
  primary: { background: 'var(--color-accent)', color: '#fff' },
  secondary: { background: 'var(--color-bg-secondary)', color: 'var(--color-text-primary)', border: '1px solid var(--color-border)' },
  ghost: { background: 'transparent', color: 'var(--color-accent)' },
  sm: { padding: '6px 14px', fontSize: 13, borderRadius: 'var(--radius-sm)' },
  md: { padding: '10px 20px', fontSize: 15, borderRadius: 'var(--radius-md)' },
  lg: { padding: '14px 28px', fontSize: 17, borderRadius: 'var(--radius-lg)' },
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary', size = 'md', loading, children, style, disabled, ...props
}) => (
  <button
    style={{
      ...styles.base, ...styles[variant], ...styles[size],
      opacity: disabled || loading ? 0.5 : 1,
      ...style,
    }}
    disabled={disabled || loading}
    {...props}
  >
    {loading && <span style={{ marginRight: 8 }}>⟳</span>}
    {children}
  </button>
);
