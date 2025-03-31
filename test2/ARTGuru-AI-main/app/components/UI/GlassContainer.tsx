import React, { useState } from 'react';

const GlassContainer = ({ children, className = '', isInteractive = true }) => {
  const [isFocused, setIsFocused] = useState(false);

  const glassStyles = `
    relative
    backdrop-blur-xl
    bg-white/15
    rounded-xl
    border
    border-white/30
    transition-all
    duration-300
    before:absolute
    before:inset-0
    before:backdrop-blur-xl
    before:bg-white/5
    before:rounded-xl
    before:-z-10
    ${isInteractive ? (
      isFocused 
        ? 'shadow-[0_0_25px_rgba(255,255,255,0.6)] border-white/50' 
        : 'hover:border-white/40 hover:bg-white/20'
    ) : ''}
    ${className}
  `;

  return (
    <div
      className={glassStyles}
      onMouseEnter={() => isInteractive && setIsFocused(true)}
      onMouseLeave={() => isInteractive && setIsFocused(false)}
    >
      {children}
    </div>
  );
};

export default GlassContainer;