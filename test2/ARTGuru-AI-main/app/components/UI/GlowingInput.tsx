import React, { useState } from 'react';
import { useNavigate } from '@remix-run/react';
import { Send } from 'lucide-react';

const GlowingInput = ({ className = '', placeholder = 'Enter text...', ...props }) => {
  const [inputValue, setInputValue] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      navigate('/dashboard', { state: { input: inputValue } });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative flex items-center">
        <div className="relative w-[50%] flex items-center">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className={`
              w-[100%]
              px-6
              py-4
              bg-white
              rounded-lg
              text-gray-700
              transition-transform
              duration-200
              focus:outline-none
              font-subheading
              pr-12
              ${className}
            `}
            placeholder={placeholder}
            {...props}
          />
          <button
            type="submit"
            className="
              absolute
              right-3
              p-2
              text-gray-400
              hover:text-gray-600
              transition-colors
              duration-200
              focus:outline-none
              flex
              items-center
              justify-center
            "
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
      {/* Glow effect */}
      <div
        className="
          absolute
          top-4
          left-0
          right-0
          -z-10
          h-full
          w-[50%]
          scale-90
          transform
          blur-xl
          bg-gradient-to-r
          from-pink-500
          via-purple-500
          to-pink-500
          bg-[length:200%_200%]
          animate-glow
        "
      />
    </form>
  );
};

export default GlowingInput;