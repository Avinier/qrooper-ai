import React, { ReactNode } from 'react';
import '../../styles/animated-background.css'

interface AnimatedBackgroundProps {
  className?: string;
  children: ReactNode;
}

const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({ 
  className = '', 
  children 
}) => {
  return (
    <div className={`animated-gradient-bg ${className}`}>
      {children}
    </div>
  );
};

export default AnimatedBackground;