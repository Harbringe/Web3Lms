import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { theme } from '@/utils/theme';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`${theme.components.card.base} ${className}`}
    >
      {children}
    </motion.div>
  );
} 