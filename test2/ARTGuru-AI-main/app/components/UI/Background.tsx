import React, { ReactNode } from 'react';
import '../../styles/background.css'

interface BackgroundProps {
  className?: string;
  children: ReactNode;
}

const Background: React.FC<BackgroundProps> = ({ 
  className = '', 
  children 
}) => {
  return (
    <div className={`gradient-bg ${className}`}>
      {children}
    </div>
  );
};

export default Background;