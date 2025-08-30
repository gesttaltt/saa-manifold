import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';

// Lazy load components for better performance
const Dashboard = lazy(() => import('@components/pages/Dashboard').then(module => ({ default: module.Dashboard })));
const Analysis = lazy(() => import('@components/pages/Analysis').then(module => ({ default: module.Analysis })));
const Visualization = lazy(() => import('@components/pages/Visualization').then(module => ({ default: module.Visualization })));
const DataExplorer = lazy(() => import('@components/pages/DataExplorer').then(module => ({ default: module.DataExplorer })));
const History = lazy(() => import('@components/pages/History').then(module => ({ default: module.History })));
const Settings = lazy(() => import('@components/pages/Settings').then(module => ({ default: module.Settings })));
const Help = lazy(() => import('@components/pages/Help').then(module => ({ default: module.Help })));

// New AI-enhanced components
const AIAssistant = lazy(() => import('@components/ai/AIAssistant'));
const CollaborativeSession = lazy(() => import('@components/collaboration/CollaborativeSession'));
const AdvancedVisualization = lazy(() => import('@components/visualization/AdvancedVisualization'));
const MLInsights = lazy(() => import('@components/ml/MLInsights'));
const RealTimeMonitoring = lazy(() => import('@components/monitoring/RealTimeMonitoring'));

// Loading component
const LoadingFallback: React.FC = () => (
  <Box
    sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '50vh',
    }}
  >
    <CircularProgress size={60} />
  </Box>
);

// Route configuration with metadata
interface RouteConfig {
  path: string;
  component: React.ComponentType;
  title: string;
  description: string;
  requiresAuth?: boolean;
  requiresGPU?: boolean;
  aiEnhanced?: boolean;
  collaborationEnabled?: boolean;
}

const routeConfigs: RouteConfig[] = [
  {
    path: '/',
    component: Dashboard,
    title: 'Dashboard',
    description: 'Overview and quick actions',
  },
  {
    path: '/analysis',
    component: Analysis,
    title: 'SAA Analysis',
    description: 'Create and configure SAA analyses',
    requiresAuth: true,
    aiEnhanced: true,
  },
  {
    path: '/analysis/:id',
    component: Analysis,
    title: 'Analysis Details',
    description: 'View specific analysis results',
    requiresAuth: true,
  },
  {
    path: '/visualization',
    component: Visualization,
    title: '3D Visualization',
    description: 'Interactive 3D manifold exploration',
    requiresGPU: true,
    aiEnhanced: true,
  },
  {
    path: '/visualization/advanced',
    component: AdvancedVisualization,
    title: 'Advanced Visualization',
    description: 'Multi-modal and AR/VR visualization',
    requiresGPU: true,
    aiEnhanced: true,
    collaborationEnabled: true,
  },
  {
    path: '/data',
    component: DataExplorer,
    title: 'Data Explorer',
    description: 'Browse and analyze flux data sources',
    aiEnhanced: true,
  },
  {
    path: '/history',
    component: History,
    title: 'Analysis History',
    description: 'Previous analyses and trends',
    aiEnhanced: true,
  },
  {
    path: '/ml-insights',
    component: MLInsights,
    title: 'ML Insights',
    description: 'Machine learning discoveries and patterns',
    requiresAuth: true,
    aiEnhanced: true,
  },
  {
    path: '/monitoring',
    component: RealTimeMonitoring,
    title: 'Real-time Monitoring',
    description: 'Live SAA monitoring and alerts',
    requiresAuth: true,
  },
  {
    path: '/collaborate/:sessionId',
    component: CollaborativeSession,
    title: 'Collaborative Session',
    description: 'Multi-user analysis session',
    requiresAuth: true,
    collaborationEnabled: true,
  },
  {
    path: '/ai',
    component: AIAssistant,
    title: 'AI Assistant',
    description: 'Natural language SAA analysis',
    requiresAuth: true,
    aiEnhanced: true,
  },
  {
    path: '/settings',
    component: Settings,
    title: 'Settings',
    description: 'Application preferences and configuration',
  },
  {
    path: '/help',
    component: Help,
    title: 'Help & Documentation',
    description: 'User guides and API documentation',
  },
];

interface EnhancedAppRoutesProps {
  userCapabilities: {
    hasGPU: boolean;
    hasWebGL2: boolean;
    hasWebGPU: boolean;
    isAuthenticated: boolean;
    expertiseLevel: 'novice' | 'intermediate' | 'expert';
  };
}

export const EnhancedAppRoutes: React.FC<EnhancedAppRoutesProps> = ({ 
  userCapabilities 
}) => {
  // Filter routes based on user capabilities
  const availableRoutes = routeConfigs.filter(route => {
    if (route.requiresAuth && !userCapabilities.isAuthenticated) {
      return false;
    }
    if (route.requiresGPU && !userCapabilities.hasGPU) {
      return false;
    }
    return true;
  });

  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {availableRoutes.map(({ path, component: Component }) => (
          <Route
            key={path}
            path={path}
            element={<Component />}
          />
        ))}
        
        {/* Redirect routes */}
        <Route path="/viz" element={<Navigate to="/visualization" replace />} />
        <Route path="/analyze" element={<Navigate to="/analysis" replace />} />
        
        {/* 404 fallback */}
        <Route
          path="*"
          element={
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: 'calc(100vh - 200px)',
                textAlign: 'center',
              }}
            >
              <h1>404 - Page Not Found</h1>
              <p>The page you're looking for doesn't exist or you don't have permission to access it.</p>
            </Box>
          }
        />
      </Routes>
    </Suspense>
  );
};

// Export route configurations for navigation components
export { routeConfigs };
export type { RouteConfig };