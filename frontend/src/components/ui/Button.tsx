import { ButtonHTMLAttributes } from 'react';
import { theme } from '@/utils/theme';
import { motion } from 'framer-motion';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outlined';
  loading?: boolean;
}

export default function Button({ 
  children, 
  variant = 'primary', 
  loading = false,
  className = '',
  ...props 
}: ButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`
        ${theme.components.button.base}
        ${theme.components.button[variant]}
        ${loading ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      disabled={loading}
      {...props}
    >
      {loading ? (
        <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
      ) : children}
    </motion.button>
  );
} 