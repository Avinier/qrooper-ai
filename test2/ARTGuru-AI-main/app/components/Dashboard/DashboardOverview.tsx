import React, { useState } from 'react';
import { Link } from '@remix-run/react';
import { AlertCircle, Target, TrendingUp } from 'lucide-react';
import GlowingInput, { GlowingButton } from '../UI/GlowingInput';

const PainPointComponent = ({ data }) => {
  return (
    <div className="space-y-5 p-4 w-full">
      <div className="flex items-center gap-2 mb-4">
        <AlertCircle className="w-6 h-6 text-lilac" />
        <h3 className="text-lg font-semibold text-grey/80">Pain Points</h3>
      </div>
      <div className="flex gap-4 overflow-x-auto pb-2 w-full">
        {data.map(point => (
          <div key={point.id} 
            className="min-w-[300px] p-4 backdrop-blur-xl bg-white/10 rounded-xl border border-lilac/30 
            hover:border-lilac/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-lilac">{point.source}</span>
              <span className="px-3 py-1 bg-lilac/10 text-lilac rounded-full text-sm border border-lilac/20">
                {point.frequency}%
              </span>
            </div>
            <p className="text-grey/90">{point.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const TriggerComponent = ({ data }) => {
  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-6 h-6 text-sulu" />
        <h3 className="text-lg font-semibold text-grey/80">Emotional Triggers</h3>
      </div>
      <div className="space-y-4">
        {data.map(trigger => (
          <div key={trigger.id} className="flex items-center gap-4 p-3 backdrop-blur-xl bg-white/5 rounded-xl
            border border-sulu/20 hover:border-sulu/40 transition-all duration-300">
            <div className="w-24 text-sm font-medium text-sulu">{trigger.type}</div>
            <div className="flex-1">
              <div className="w-full bg-white/10 rounded-full h-2.5">
                <div
                  className="bg-gradient-to-r from-sulu/40 to-sulu h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${trigger.strength * 100}%` }}
                />
              </div>
            </div>
            <div className="w-32 text-sm text-grey/80">{trigger.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const StrategicComponent = ({ data }) => {
  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-6 h-6 text-portage" />
        <h3 className="text-lg font-semibold text-grey/80">Strategic Insights</h3>
      </div>
      <div className="grid grid-cols-1 gap-4">
        {data.map(insight => (
          <div key={insight.id} 
            className="p-4 backdrop-blur-xl bg-white/10 rounded-xl border border-portage/30 
            hover:border-portage/50 transition-all duration-300">
            <div className="text-sm font-medium text-portage mb-2">
              {insight.category}
            </div>
            <p className="text-grey/90">{insight.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const DashboardCard = ({ item }) => {
  const [isFocused, setIsFocused] = useState(false);
  
  const getComponent = () => {
    switch(item.type) {
      case 'painPoints':
        return <PainPointComponent data={item.data} />;
      case 'triggers':
        return <TriggerComponent data={item.data} />;
      case 'strategic':
        return <StrategicComponent data={item.data} />;
      default:
        return null;
    }
  };

  return (
    <div
      className={`
        relative
        break-inside-avoid
        ${item.height}
        backdrop-blur-xl
        bg-white/20
        rounded-xl
        border
        border-white/40
        transition-all
        duration-500
        before:absolute
        before:inset-0
        before:backdrop-blur-xl
        before:bg-white/5
        before:rounded-xl
        before:-z-10
        block
        mb-6
        overflow-hidden
        font-subheading
        ${item.width || ''}
        ${isFocused ? 'shadow-[0_0_25px_rgba(255,255,255,0.6)] border-white/60' : 'hover:border-white/50 hover:bg-white/20'}
      `}
      onMouseEnter={() => setIsFocused(true)}
      onMouseLeave={() => setIsFocused(false)}
    >
      {getComponent()}
    </div>
  );
};

const DashboardOverview = ({ items }) => {
  // const items = [
  //   {
  //     id: 1,
  //     type: 'painPoints',
  //     height: 'h-64',
  //     width: 'col-span-2',
  //     data: [
  //       { id: 1, source: 'Reddit', text: "Can't find fresh coffee beans in my area", frequency: 75 },
  //       { id: 2, source: 'Quora', text: "Tired of inconsistent coffee quality", frequency: 82 },
  //       { id: 3, source: 'Reviews', text: "Regular grocery store coffee goes stale", frequency: 68 }
  //     ]
  //   },
  //   {
  //     id: 2,
  //     type: 'strategic',
  //     height: 'h-[400px]',
  //     width: 'col-span-1',
  //     data: [
  //       { id: 1, category: 'USP', text: 'Emphasize bean freshness date on packaging' },
  //       { id: 2, category: 'Messaging', text: 'Focus on "expert-curated" selection process' },
  //       { id: 3, category: 'Target', text: 'Target urban professionals aged 25-40' },
  //       { id: 4, category: 'Channel', text: 'Leverage Instagram and LinkedIn for brand positioning' }
  //     ]
  //   },
  //   {
  //     id: 3,
  //     type: 'triggers',
  //     height: 'min-h-72',
  //     width: 'col-span-3',
  //     data: [
  //       { id: 1, type: 'Emotional', text: 'Fear of missing perfect morning coffee', strength: 0.9 },
  //       { id: 2, type: 'Practical', text: 'Desire for convenience', strength: 0.85 },
  //       { id: 3, type: 'Social', text: 'Status of being a coffee connoisseur', strength: 0.75 }
  //     ]
  //   }
  // ];

  

  return (
    <div className="
      w-[90vw]
      h-[90vh]
      mx-auto
      my-8
      border
      border-white
      rounded-lg
      backdrop-blur-xl
      bg-background/60
      shadow-[0_0_25px_rgba(255,255,255,0.6)]
      border-white/60
      overflow-auto
    ">
      <div className="p-6">
        <h1 className="text-2xl font-semibold mb-6 text-center font-subheading text-grey/80">
          Overview
        </h1>
        <div className="grid grid-cols-3 gap-6">
          {items.map(item => (
            <DashboardCard key={item.id} item={item} />
          ))}
        </div>
        <div className='w-[75%] ml-[400px] my-10'>
        <GlowingInput placeholder='Enter your social media link...'/>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;