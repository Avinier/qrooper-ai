import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SearchInput from '~/components/UI/SearchInput';
import AnimatedBackground from '~/components/UI/AnimatedBackground';
import DashboardOverview from '~/components/Dashboard/DashboardOverview';
import AnalyticsDashboard from '~/components/Dashboard/AnalyticsDashboard';
import ProfileLogo from '~/components/UI/ProfileLogo';

const Index = () => {
  const [isSearching, setIsSearching] = React.useState(false);
  const [searchCompleted, setSearchCompleted] = React.useState(false);
  const [items, setItems] = React.useState([]);

  const handleSearchComplete = (results) => {
    setItems(results.items);
    setSearchCompleted(true);
    setIsSearching(false);
  };

  return (
    <AnimatedBackground className="min-h-screen items-center justify-center">
      <AnimatePresence mode="wait">
        <ProfileLogo/>
        {!searchCompleted && (
          <motion.div
            className="mx-auto pt-40"
            initial={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.5 }}
            key="header"
          >
            <motion.h1
              className="font-subheading text-5xl pb-3 text-gray-800 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              ARTGuru.AI
            </motion.h1>
            <motion.h3
              className="font-subheading text-xl font-light text-gray-600 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              Seamlessly research, generate, and analyse your marketing idea
            </motion.h3>
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence mode="wait">
        <motion.div
          className={`${searchCompleted ? 'pt-10' : 'mt-12'}`}
          transition={{ duration: 0.5 }}
          key="search-input"
        >
          <SearchInput
            onSearchStart={() => setIsSearching(true)}
            onSearchComplete={handleSearchComplete}
            searchCompleted={searchCompleted}
          />
        </motion.div>
      </AnimatePresence>
      <AnimatePresence>
        {searchCompleted && (
          <motion.div
            className="mt-8"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            key="welcome-message"
          >
            <DashboardOverview items={items} />
          </motion.div>
        )}
      </AnimatePresence>
    </AnimatedBackground>
  );
};

export default Index;