const radarData = [
    { 
      metric: 'Stream Views', 
      A: 145, // YouTube Gaming
      B: 130, // Twitch
      CompA: 160, // Competitor YouTube
      CompB: 150  // Competitor Twitch
    },
    { 
      metric: 'Social Shares', 
      A: 110,
      B: 140,
      CompA: 125,
      CompB: 145
    },
    { 
      metric: 'Community Posts', 
      A: 95,
      B: 125,
      CompA: 105,
      CompB: 130
    },
    { 
      metric: 'Player Reviews', 
      A: 120,
      B: 105,
      CompA: 130,
      CompB: 110
    },
    { 
      metric: 'Discord Activity', 
      A: 130,
      B: 115,
      CompA: 140,
      CompB: 125
    }
  ];
  
  // Time Patterns Data (Daily Gaming Activity)
  const timePatternData = [
    { 
      time: '00:00', 
      engagement: 2200,    // Active players
      viral: 3500,         // Stream viewers
      competitorEngagement: 2400,
      competitorViral: 3800
    },
    { 
      time: '04:00', 
      engagement: 1800,
      viral: 2800,
      competitorEngagement: 2000,
      competitorViral: 3000
    },
    { 
      time: '08:00', 
      engagement: 3500,
      viral: 5500,
      competitorEngagement: 3800,
      competitorViral: 5800
    },
    { 
      time: '12:00', 
      engagement: 4200,
      viral: 6800,
      competitorEngagement: 4500,
      competitorViral: 7200
    },
    { 
      time: '16:00', 
      engagement: 5000,
      viral: 8500,
      competitorEngagement: 5400,
      competitorViral: 9000
    },
    { 
      time: '20:00', 
      engagement: 4800,
      viral: 7800,
      competitorEngagement: 5200,
      competitorViral: 8200
    }
  ];
  
  // Platform Performance Data (Monthly Gaming Metrics)
  const platformData = [
    { 
      date: '2024-01', 
      youtube: 8500,      // YouTube Gaming views (K)
      twitch: 6200,       // Twitch viewers (K)
      steam: 4800,        // Steam activity (K)
      competitorYoutube: 9000,
      competitorTwitch: 6800
    },
    { 
      date: '2024-02', 
      youtube: 9200,
      twitch: 7000,
      steam: 5200,
      competitorYoutube: 9800,
      competitorTwitch: 7500
    },
    { 
      date: '2024-03', 
      youtube: 11000,
      twitch: 8500,
      steam: 6000,
      competitorYoutube: 11500,
      competitorTwitch: 9000
    },
    { 
      date: '2024-04', 
      youtube: 10500,
      twitch: 8000,
      steam: 5800,
      competitorYoutube: 11000,
      competitorTwitch: 8500
    },
    { 
      date: '2024-05', 
      youtube: 12000,
      twitch: 9500,
      steam: 7000,
      competitorYoutube: 12500,
      competitorTwitch: 10000
    }
  ];
  
  // CTA Funnel Data (Player Conversion Funnel)
  const funnelData = [
    { 
      stage: 'Game Page Views', 
      value: 1000000,
      competitorValue: 900000
    },
    { 
      stage: 'Demo Downloads', 
      value: 500000,
      competitorValue: 450000
    },
    { 
      stage: 'Full Game Purchase', 
      value: 200000,
      competitorValue: 180000
    },
    { 
      stage: 'Active Players', 
      value: 150000,
      competitorValue: 130000
    },
    { 
      stage: 'Community Members', 
      value: 80000,
      competitorValue: 70000
    }
  ];
  
  // ROI Comparison Data (Gaming Marketing ROI)
  const roiData = [
    { 
      month: 'Jan', 
      cost: 800000,         // Marketing spend
      revenue: 1500000,     // Game sales + IAP
      profit: 700000,
      competitorCost: 900000,
      competitorRevenue: 1600000,
      competitorProfit: 700000
    },
    { 
      month: 'Feb', 
      cost: 850000,
      revenue: 1700000,
      profit: 850000,
      competitorCost: 950000,
      competitorRevenue: 1800000,
      competitorProfit: 850000
    },
    { 
      month: 'Mar', 
      cost: 900000,
      revenue: 2000000,
      profit: 1100000,
      competitorCost: 1000000,
      competitorRevenue: 2200000,
      competitorProfit: 1200000
    },
    { 
      month: 'Apr', 
      cost: 1000000,
      revenue: 2500000,
      profit: 1500000,
      competitorCost: 1100000,
      competitorRevenue: 2700000,
      competitorProfit: 1600000
    },
    { 
      month: 'May', 
      cost: 1200000,
      revenue: 3000000,
      profit: 1800000,
      competitorCost: 1300000,
      competitorRevenue: 3200000,
      competitorProfit: 1900000
    }
  ];