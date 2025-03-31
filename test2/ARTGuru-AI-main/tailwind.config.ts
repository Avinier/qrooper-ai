import type { Config } from "tailwindcss";
export default {
  content: ["./app/**/{**,.client,.server}/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors : {
        lilac: '#E98AF0',
        portage: '#8A8FF0',
        sulu: '#8AF096',
        khaki: '#ECF08A',
        tacao: '#F0B28A',
        spray: '#8AE4F0',
        grey: '#1A1C2C',
        background : '#FCFAF3'
      },
      fontFamily: {
        heading: ['Tiempos-Heading', 'Georgia', 'serif'],
        subheading: ['Tiempos-Regular', 'Georgia', 'serif'],
        text: ['Sohne', 'system-ui', 'sans-serif'],
      },
      keyframes: {
                glow: {
                  '0%': { backgroundPosition: '0% 50%' },
                  '100%': { backgroundPosition: '200% 50%' },
                },
              },
              animation: {
                glow: 'glow 0.5s linear infinite',
              },
    },
  },
  plugins: [],
} satisfies Config;