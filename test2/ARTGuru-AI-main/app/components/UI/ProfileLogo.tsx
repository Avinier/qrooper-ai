import React from 'react';
import { motion } from 'framer-motion';
import { User } from 'lucide-react';

const ProfileLogo = () => {
  return (
    <motion.div
      className="fixed top-4 right-4 z-50"
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="w-16 h-16 rounded-full bg-white/40 backdrop-blur-lg shadow-md flex items-center justify-center cursor-pointer hover:bg-gray-50">
        <User className="w-10 h-10 text-gray-600" />
      </div>
    </motion.div>
  );
};

export default ProfileLogo;