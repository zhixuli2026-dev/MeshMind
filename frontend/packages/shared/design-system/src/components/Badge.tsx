import React from 'react';

type BadgeVariant = 'law' | 'rule' | 'best_practice' | 'event' | 'default';

const colors: Record<BadgeVariant, string> = {
  law: 'var(--color-law)', rule: '#5856d6', best_practice: 'var(--color-success)',
  event: 'var(--color-warning)', default: 'var(--color-text-secondary)',
};

export const Badge: React.FC<{ variant?: BadgeVariant; children: React.ReactNode }> = ({
  variant = 'default', children,
}) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center',
    padding: '2px 10px', fontSize: 12, fontWeight: 600,
    borderRadius: 100, color: colors[variant],
    background: `${colors[variant]}14`, letterSpacing: '0.02em',
  }}>
    {children}
  </span>
);
