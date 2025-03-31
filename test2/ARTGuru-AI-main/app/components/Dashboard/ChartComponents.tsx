import {  useEffect } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, 
         PolarRadiusAxis, Radar} from 'recharts';

// Utility functions for generating random numbers
const randomInRange = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomDecimal = (min, max) => Number((Math.random() * (max - min) + min).toFixed(1));

// 1. Performance Radar Data
const generateRadarData = () => ([
  { metric: 'Engagement', A: randomInRange(80, 140), B: randomInRange(80, 140), CompA: randomInRange(90, 150), CompB: randomInRange(90, 150) },
  { metric: 'Reach', A: randomInRange(80, 140), B: randomInRange(80, 140), CompA: randomInRange(90, 150), CompB: randomInRange(90, 150) },
  { metric: 'Clicks', A: randomInRange(80, 140), B: randomInRange(80, 140), CompA: randomInRange(90, 150), CompB: randomInRange(90, 150) },
  { metric: 'Conversions', A: randomInRange(80, 140), B: randomInRange(80, 140), CompA: randomInRange(90, 150), CompB: randomInRange(90, 150) },
  { metric: 'Shares', A: randomInRange(80, 140), B: randomInRange(80, 140), CompA: randomInRange(90, 150), CompB: randomInRange(90, 150) }
]);

// 2. Time Patterns Data
const generateTimePatternData = () => ([
  { time: '00:00', engagement: randomInRange(1000, 3500), viral: randomInRange(2000, 7000), competitorEngagement: randomInRange(1200, 3700), competitorViral: randomInRange(2200, 7200) },
  { time: '04:00', engagement: randomInRange(1000, 3500), viral: randomInRange(2000, 7000), competitorEngagement: randomInRange(1200, 3700), competitorViral: randomInRange(2200, 7200) },
  { time: '08:00', engagement: randomInRange(1000, 3500), viral: randomInRange(2000, 7000), competitorEngagement: randomInRange(1200, 3700), competitorViral: randomInRange(2200, 7200) },
  { time: '12:00', engagement: randomInRange(1000, 3500), viral: randomInRange(2000, 7000), competitorEngagement: randomInRange(1200, 3700), competitorViral: randomInRange(2200, 7200) },
  { time: '16:00', engagement: randomInRange(1000, 3500), viral: randomInRange(2000, 7000), competitorEngagement: randomInRange(1200, 3700), competitorViral: randomInRange(2200, 7200) },
  { time: '20:00', engagement: randomInRange(1000, 3500), viral: randomInRange(2000, 7000), competitorEngagement: randomInRange(1200, 3700), competitorViral: randomInRange(2200, 7200) }
]);

// 3. Platform Performance Data
const generatePlatformData = () => ([
  { date: '2024-01', youtube: randomInRange(1500, 4500), instagram: randomInRange(1000, 10000), reddit: randomInRange(1800, 2500), competitorYoutube: randomInRange(1700, 4700), competitorInstagram: randomInRange(1200, 10200) },
  { date: '2024-02', youtube: randomInRange(1500, 4500), instagram: randomInRange(1000, 10000), reddit: randomInRange(1800, 2500), competitorYoutube: randomInRange(1700, 4700), competitorInstagram: randomInRange(1200, 10200) },
  { date: '2024-03', youtube: randomInRange(1500, 4500), instagram: randomInRange(1000, 10000), reddit: randomInRange(1800, 2500), competitorYoutube: randomInRange(1700, 4700), competitorInstagram: randomInRange(1200, 10200) },
  { date: '2024-04', youtube: randomInRange(1500, 4500), instagram: randomInRange(1000, 10000), reddit: randomInRange(1800, 2500), competitorYoutube: randomInRange(1700, 4700), competitorInstagram: randomInRange(1200, 10200) },
  { date: '2024-05', youtube: randomInRange(1500, 4500), instagram: randomInRange(1000, 10000), reddit: randomInRange(1800, 2500), competitorYoutube: randomInRange(1700, 4700), competitorInstagram: randomInRange(1200, 10200) }
]);

// 4. CTA Funnel Data
const generateFunnelData = () => {
  const baseValue = randomInRange(800, 1200);
  const dropRate = 0.7; // Each stage reduces by ~30%
  return [
    { stage: 'Impressions', value: baseValue, competitorValue: Math.round(baseValue * 0.8) },
    { stage: 'Clicks', value: Math.round(baseValue * dropRate), competitorValue: Math.round(baseValue * dropRate * 0.8) },
    { stage: 'Sign-ups', value: Math.round(baseValue * dropRate * dropRate), competitorValue: Math.round(baseValue * dropRate * dropRate * 0.8) },
    { stage: 'Purchases', value: Math.round(baseValue * Math.pow(dropRate, 3)), competitorValue: Math.round(baseValue * Math.pow(dropRate, 3) * 0.8) },
    { stage: 'Retention', value: Math.round(baseValue * Math.pow(dropRate, 4)), competitorValue: Math.round(baseValue * Math.pow(dropRate, 4) * 0.8) }
  ];
};

// 5. ROI Comparison Data
const generateROIData = () => ([
  { month: 'Jan', ...generateMonthlyROI() },
  { month: 'Feb', ...generateMonthlyROI() },
  { month: 'Mar', ...generateMonthlyROI() },
  { month: 'Apr', ...generateMonthlyROI() },
  { month: 'May', ...generateMonthlyROI() }
]);

// Helper function for ROI data generation
const generateMonthlyROI = () => {
  const cost = randomInRange(300, 600);
  const revenue = cost + randomInRange(100, 400);
  const profit = revenue - cost;
  const competitorCost = cost + randomInRange(-50, 50);
  const competitorRevenue = competitorCost + randomInRange(50, 350);
  const competitorProfit = competitorRevenue - competitorCost;
  return {
    cost,
    revenue,
    profit,
    competitorCost,
    competitorRevenue,
    competitorProfit
  };
};

export const PerformanceRadar = ({ showCompetitor = false }) => {
  const [activeRadar, setActiveRadar] = useState(null);
  const [data, setData] = useState([]);

  useEffect(() => {
    setData(generateRadarData());
  }, []);

  const handleMouseEnter = (platform) => {
    setActiveRadar(platform);
  };

  const handleMouseLeave = () => {
    setActiveRadar(null);
  };

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: '#666', fontSize: 14 }}
          />
          <PolarRadiusAxis angle={30} domain={[0, 150]} />
          
          <Tooltip 
            animationDuration={200}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              borderRadius: '6px',
              padding: '8px',
              border: '1px solid #ccc'
            }}
          />
          
          <Legend
            wrapperStyle={{
              paddingTop: '20px'
            }}
            onMouseEnter={(entry) => handleMouseEnter(entry.dataKey)}
            onMouseLeave={handleMouseLeave}
          />

          <Radar
            name="YouTube"
            dataKey="A"
            stroke="#F0B28A"
            fill="#F0B28A"
            fillOpacity={activeRadar && activeRadar !== 'A' ? 0.2 : 0.6}
            strokeWidth={activeRadar === 'A' ? 3 : 1}
            onMouseEnter={() => handleMouseEnter('A')}
            onMouseLeave={handleMouseLeave}
            animationBegin={0}
            animationDuration={500}
            animationEasing="linear"
          />

          <Radar
            name="Instagram"
            dataKey="B"
            stroke="#8A8FF0"
            fill="#8A8FF0"
            fillOpacity={activeRadar && activeRadar !== 'B' ? 0.2 : 0.6}
            strokeWidth={activeRadar === 'B' ? 3 : 1}
            onMouseEnter={() => handleMouseEnter('B')}
            onMouseLeave={handleMouseLeave}
            animationBegin={0}
            animationDuration={500}
            animationEasing="linear"
          />

          {showCompetitor && (
            <>
              <Radar
                name="Competitor YouTube"
                dataKey="CompA"
                stroke="#FF4D4D"
                fill="#FF4D4D"
                fillOpacity={activeRadar && activeRadar !== 'CompA' ? 0.2 : 0.6}
                strokeWidth={activeRadar === 'CompA' ? 3 : 1}
                onMouseEnter={() => handleMouseEnter('CompA')}
                onMouseLeave={handleMouseLeave}
                animationBegin={0}
                animationDuration={500}
                animationEasing="linear"
              />
              
              <Radar
                name="Competitor Instagram"
                dataKey="CompB"
                stroke="#FF8080"
                fill="#FF8080"
                fillOpacity={activeRadar && activeRadar !== 'CompB' ? 0.2 : 0.6}
                strokeWidth={activeRadar === 'CompB' ? 3 : 1}
                onMouseEnter={() => handleMouseEnter('CompB')}
                onMouseLeave={handleMouseLeave}
                animationBegin={0}
                animationDuration={500}
                animationEasing="linear"
              />
            </>
          )}
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

    import React, { useState } from 'react';
    import {
      ResponsiveContainer,
      ComposedChart,
      LineChart,
      Area,
      Scatter,
      Line,
      XAxis,
      YAxis,
      CartesianGrid,
      Tooltip,
      Legend,
      TooltipProps
    } from 'recharts';
    import { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent';
    
    // Types for data structures
    interface TimePatternData {
      time: string;
      engagement: number;
      viral: number;
      competitorEngagement?: number;
      competitorViral?: number;
    }
    
    // Custom Tooltip Component
    const CustomTooltip = ({
      active,
      payload,
      label
    }: TooltipProps<ValueType, NameType>) => {
      if (active && payload && payload.length) {
        return (
          <div className="bg-white/90 rounded-lg p-4 shadow-lg border border-gray-200">
            <p className="font-bold text-gray-700">{label}</p>
            {payload.map((entry, index) => (
              <div 
                key={`tooltip-${index}`} 
                className="text-sm flex justify-between items-center"
                style={{ color: entry.color }}
              >
                <span className="mr-2">{entry.name}:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat().format(entry.value as number)}
                </span>
              </div>
            ))}
          </div>
        );
      }
      return null;
    };
    
    interface TimePatternProps {
      showCompetitor?: boolean;
    }
    
    export const TimePatterns: React.FC<TimePatternProps> = ({ showCompetitor = false }) => {
      const [activeType, setActiveType] = useState<string | null>(null);
      const [data, setData] = useState<TimePatternData[]>([]);
    
      useEffect(() => {
        setData(generateTimePatternData());
      }, []);
    
      const handleMouseEnter = (type: string) => {
        setActiveType(type);
      };
    
      const handleMouseLeave = () => {
        setActiveType(null);
      };
    
      return (
        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <defs>
                <linearGradient id="engagementGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#E98AF0" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#E98AF0" stopOpacity={0.2}/>
                </linearGradient>
                <linearGradient id="competitorEngagementGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF0000" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#FF0000" stopOpacity={0.2}/>
                </linearGradient>
              </defs>
              
              <CartesianGrid strokeDasharray="3 3" opacity={0.8} />
              <XAxis 
                dataKey="time" 
                tick={{ fill: '#666' }} 
                axisLine={{ stroke: '#999' }} 
              />
              <YAxis 
                tick={{ fill: '#666' }} 
                axisLine={{ stroke: '#999' }} 
              />
              
              <Tooltip content={<CustomTooltip />} />
              
              <Legend 
                onMouseEnter={(e) => handleMouseEnter(e.dataKey)}
                onMouseLeave={handleMouseLeave}
              />
              
              <Area 
                type="monotone" 
                dataKey="engagement" 
                name="Engagement"
                fill="url(#engagementGradient)"
                stroke="#E98AF0"
                strokeWidth={activeType === 'engagement' ? 3 : 1}
                fillOpacity={activeType === 'viral' ? 0.3 : 1}
                animationBegin={0}
                animationDuration={800}
                animationEasing="ease-in-out"
                isAnimationActive={true}
              />
              
              {showCompetitor && (
                <Area 
                  type="monotone" 
                  dataKey="competitorEngagement" 
                  name="Competitor Engagement"
                  fill="url(#competitorEngagementGradient)"
                  stroke="#FF0000"
                  strokeWidth={activeType === 'competitorEngagement' ? 3 : 1}
                  fillOpacity={activeType === 'viral' ? 0.3 : 0.6}
                  animationBegin={0}
                  animationDuration={800}
                  animationEasing="ease-in-out"
                  isAnimationActive={true}
                />
              )}
              
              <Scatter 
                dataKey="viral" 
                name="Viral"
                fill="#8A8FF0"
                stroke="#8A8FF0"
                strokeWidth={activeType === 'viral' ? 2 : 0}
                r={activeType === 'viral' ? 8 : 6}
                fillOpacity={activeType === 'engagement' ? 0.3 : 0.8}
                animationBegin={800}
                animationDuration={400}
                isAnimationActive={true}
              />
              
              {showCompetitor && (
                <Scatter 
                  dataKey="competitorViral" 
                  name="Competitor Viral"
                  fill="#FF0000"
                  stroke="#FF0000"
                  strokeWidth={activeType === 'competitorViral' ? 2 : 0}
                  r={activeType === 'competitorViral' ? 8 : 6}
                  fillOpacity={activeType === 'engagement' ? 0.3 : 0.8}
                  animationBegin={800}
                  animationDuration={400}
                  isAnimationActive={true}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      );
    };

    interface PlatformData {
      date: string;
      youtube: number;
      instagram: number;
      reddit: number;
      competitorYoutube?: number;
      competitorInstagram?: number;
    }
    
    interface PlatformPerformanceProps {
      showCompetitor?: boolean;
    }
    
    export const PlatformPerformance: React.FC<PlatformPerformanceProps> = ({ 
      showCompetitor = false 
    }) => {
      const [activePlatform, setActivePlatform] = useState<string | null>(null);
      const [data, setData] = useState<PlatformData[]>([]);
    
      useEffect(() => {
        setData(generatePlatformData());
      }, []);
    
      const handleMouseEnter = (platform: string) => {
        setActivePlatform(platform);
      };
    
      const handleMouseLeave = () => {
        setActivePlatform(null);
      };
    
      return (
        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.7} />
              
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#666' }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return date.toLocaleDateString('default', { month: 'short' });
                }}
              />
              
              <YAxis 
                tick={{ fill: '#666' }} 
                width={40}
              />
              
              <Tooltip 
                animationDuration={200}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  borderRadius: '6px',
                  padding: '8px',
                  border: '1px solid #ccc'
                }}
                formatter={(value: number) => new Intl.NumberFormat().format(value)}
              />
              
              <Legend 
                onMouseEnter={(e) => handleMouseEnter(e.dataKey)}
                onMouseLeave={handleMouseLeave}
                wrapperStyle={{
                  paddingTop: '12px'
                }}
              />
              
              <Line 
                type="monotone" 
                dataKey="youtube" 
                name="YouTube"
                stroke="#F0B28A"
                strokeWidth={activePlatform === 'youtube' ? 3 : 1.5}
                dot={{ r: activePlatform === 'youtube' ? 5 : 3 }}
                opacity={!activePlatform || activePlatform === 'youtube' ? 1 : 0.3}
                animationBegin={0}
                animationDuration={600}
                animationEasing="ease-in-out"
              />
              
              {showCompetitor && (
                <Line 
                  type="monotone" 
                  dataKey="competitorYoutube" 
                  name="Competitor YouTube"
                  stroke="#FF0000"
                  strokeWidth={activePlatform === 'competitorYoutube' ? 3 : 1.5}
                  dot={{ r: activePlatform === 'competitorYoutube' ? 5 : 3 }}
                  opacity={!activePlatform || activePlatform === 'competitorYoutube' ? 1 : 0.3}
                  animationBegin={0}
                  animationDuration={600}
                  animationEasing="ease-in-out"
                />
              )}
              
              <Line 
                type="monotone" 
                dataKey="instagram" 
                name="Instagram"
                stroke="#8A8FF0"
                strokeWidth={activePlatform === 'instagram' ? 3 : 1.5}
                dot={{ r: activePlatform === 'instagram' ? 5 : 3 }}
                opacity={!activePlatform || activePlatform === 'instagram' ? 1 : 0.3}
                animationBegin={200}
                animationDuration={600}
                animationEasing="ease-in-out"
              />
              
              {showCompetitor && (
                <Line 
                  type="monotone" 
                  dataKey="competitorInstagram" 
                  name="Competitor Instagram"
                  stroke="#FF6666"
                  strokeWidth={activePlatform === 'competitorInstagram' ? 3 : 1.5}
                  dot={{ r: activePlatform === 'competitorInstagram' ? 5 : 3 }}
                  opacity={!activePlatform || activePlatform === 'competitorInstagram' ? 1 : 0.3}
                  animationBegin={200}
                  animationDuration={600}
                  animationEasing="ease-in-out"
                />
              )}
              
              <Line 
                type="monotone" 
                dataKey="reddit" 
                name="Reddit"
                stroke="#E98AF0"
                strokeWidth={activePlatform === 'reddit' ? 3 : 1.5}
                dot={{ r: activePlatform === 'reddit' ? 5 : 3 }}
                opacity={!activePlatform || activePlatform === 'reddit' ? 1 : 0.3}
                animationBegin={400}
                animationDuration={600}
                animationEasing="ease-in-out"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    };

import { BarChart, Bar } from 'recharts';

interface FunnelData {
  stage: string;
  value: number;
  competitorValue?: number;
}

interface ROIData {
  month: string;
  cost: number;
  revenue: number;
  profit: number;
  competitorCost?: number;
  competitorRevenue?: number;
  competitorProfit?: number;
}

interface ComponentProps {
  showCompetitor?: boolean;
}

export const CTAFunnel: React.FC<ComponentProps> = ({ showCompetitor = false }) => {
  const [activeBar, setActiveBar] = useState<number | null>(null);
  const [data, setData] = useState<FunnelData[]>([]);

  useEffect(() => {
    setData(generateFunnelData());
  }, []);

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
        >
          <defs>
            <linearGradient id="funnelGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#F0B28A" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#F0D28A" stopOpacity={0.9} />
            </linearGradient>
            <linearGradient id="competitorGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#FF6B6B" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#FF8585" stopOpacity={0.9} />
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" opacity={0.7} />
          <XAxis type="number" tick={{ fill: '#666' }} axisLine={{ stroke: '#999' }} />
          <YAxis dataKey="stage" type="category" tick={{ fill: '#666' }} axisLine={{ stroke: '#999' }} />
          
          <Tooltip 
            cursor={{ fill: 'rgba(240,178,138,0.1)' }}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              borderRadius: '6px',
              padding: '8px',
              border: '1px solid #ccc'
            }}
          />
          
          <Legend />
          
          <Bar 
            name="Our Metrics"
            dataKey="value" 
            fill="url(#funnelGradient)"
            onMouseEnter={(data, index) => setActiveBar(index)}
            onMouseLeave={() => setActiveBar(null)}
            animationBegin={0}
            animationDuration={800}
            animationEasing="ease-out"
          />
          
          {showCompetitor && (
            <Bar 
              name="Competitor Metrics"
              dataKey="competitorValue" 
              fill="url(#competitorGradient)"
              onMouseEnter={(data, index) => setActiveBar(index)}
              onMouseLeave={() => setActiveBar(null)}
              animationBegin={200}
              animationDuration={800}
              animationEasing="ease-out"
            />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const ROIComparison: React.FC<ComponentProps> = ({ showCompetitor = false }) => {
  const [activeType, setActiveType] = useState<string | null>(null);
  const [data, setData] = useState<ROIData[]>([]);

  useEffect(() => {
    setData(generateROIData());
  }, []);

  const handleMouseEnter = (type: string) => {
    setActiveType(type);
  };

  const handleMouseLeave = () => {
    setActiveType(null);
  };

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data}>
          <defs>
            {/* Gradient definitions remain the same */}
            <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#96F0A3" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8AF096" stopOpacity={0.3}/>
            </linearGradient>
            <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F0EC8A" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#ECF08A" stopOpacity={0.2}/>
            </linearGradient>
            <linearGradient id="competitorCostGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FF6B6B" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#FF8585" stopOpacity={0.3}/>
            </linearGradient>
            <linearGradient id="competitorProfitGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FF9999" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#FFACAC" stopOpacity={0.2}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" opacity={0.7} />
          <XAxis dataKey="month" tick={{ fill: '#666' }} />
          <YAxis tick={{ fill: '#666' }} />
          
          <Tooltip 
            animationDuration={200}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              borderRadius: '6px',
              padding: '8px',
              border: '1px solid #ccc'
            }}
          />
          
          <Legend 
            onMouseEnter={(e) => handleMouseEnter(e.dataKey)}
            onMouseLeave={handleMouseLeave}
            wrapperStyle={{ paddingTop: '12px' }}
          />

          {/* Base metrics */}
          <Bar 
            name="Our Cost"
            dataKey="cost" 
            fill="url(#costGradient)"
            opacity={!activeType || activeType === 'cost' ? 1 : 0.3}
            animationBegin={0}
            animationDuration={600}
            animationEasing="ease-out"
          />
          
          <Line 
            name="Our Revenue"
            type="monotone" 
            dataKey="revenue" 
            stroke="#8A8FF0"
            strokeWidth={activeType === 'revenue' ? 3 : 1.5}
            dot={{ r: activeType === 'revenue' ? 5 : 3 }}
            opacity={!activeType || activeType === 'revenue' ? 1 : 0.3}
            animationBegin={400}
            animationDuration={600}
            animationEasing="ease-in-out"
          />
          
          <Area 
            name="Our Profit"
            type="monotone" 
            dataKey="profit" 
            fill="url(#profitGradient)"
            stroke="#ECF08A"
            strokeWidth={activeType === 'profit' ? 2 : 1}
            fillOpacity={activeType === 'profit' ? 1 : !activeType ? 0.8 : 0.3}
            animationBegin={800}
            animationDuration={600}
            animationEasing="ease-in-out"
          />

          {/* Competitor metrics */}
          {showCompetitor && (
            <>
              <Bar 
                name="Competitor Cost"
                dataKey="competitorCost" 
                fill="url(#competitorCostGradient)"
                opacity={!activeType || activeType === 'competitorCost' ? 1 : 0.3}
                animationBegin={200}
                animationDuration={600}
                animationEasing="ease-out"
              />
              
              <Line 
                name="Competitor Revenue"
                type="monotone" 
                dataKey="competitorRevenue" 
                stroke="#FF4D4D"
                strokeWidth={activeType === 'competitorRevenue' ? 3 : 1.5}
                dot={{ r: activeType === 'competitorRevenue' ? 5 : 3 }}
                opacity={!activeType || activeType === 'competitorRevenue' ? 1 : 0.3}
                animationBegin={600}
                animationDuration={600}
                animationEasing="ease-in-out"
              />
              
              <Area 
                name="Competitor Profit"
                type="monotone" 
                dataKey="competitorProfit" 
                fill="url(#competitorProfitGradient)"
                stroke="#FF6666"
                strokeWidth={activeType === 'competitorProfit' ? 2 : 1}
                fillOpacity={activeType === 'competitorProfit' ? 1 : !activeType ? 0.8 : 0.3}
                animationBegin={1000}
                animationDuration={600}
                animationEasing="ease-in-out"
              />
            </>
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
