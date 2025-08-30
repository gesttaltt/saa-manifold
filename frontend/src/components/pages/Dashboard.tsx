import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Stack,
  Alert,
  IconButton,
} from '@mui/material';
import {
  Science,
  Visibility,
  TrendingUp,
  Warning,
  Refresh,
  PlayArrow,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

import { useSAAAnalysis } from '@hooks/useSAAAnalysis';
import apiService from '@services/api.service';
import { DataSource, AnalysisResult } from '@types/saa.types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { currentAnalysis, isAnalyzing, progress } = useSAAAnalysis();
  
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisResult[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load data sources, health, and recent analyses concurrently
      const [sources, health, analyses] = await Promise.all([
        apiService.getDataSources(),
        apiService.getHealth(),
        apiService.getHistoricalAnalyses({ limit: 5 })
      ]);
      
      setDataSources(sources);
      setSystemHealth(health);
      setRecentAnalyses(analyses);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'unhealthy': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
          Loading dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          SAA Research Dashboard
        </Typography>
        <IconButton onClick={loadDashboardData} color="primary">
          <Refresh />
        </IconButton>
      </Box>

      {/* Current Analysis Status */}
      {isAnalyzing && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ width: '100%' }}>
            <Typography variant="body2" gutterBottom>
              Analysis in progress... {Math.round(progress)}% complete
            </Typography>
            <LinearProgress variant="determinate" value={progress} />
          </Box>
        </Alert>
      )}

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Science color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                New Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Start SAA region analysis
              </Typography>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => navigate('/analysis')}
                fullWidth
              >
                Start Analysis
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Visibility color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                3D Visualization
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Explore manifold data
              </Typography>
              <Button
                variant="outlined"
                onClick={() => navigate('/visualization')}
                fullWidth
                disabled={!currentAnalysis}
              >
                View 3D
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                Historical Trends
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                View past analyses
              </Typography>
              <Button
                variant="outlined"
                onClick={() => navigate('/history')}
                fullWidth
              >
                View History
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Warning color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Monitor health
              </Typography>
              <Chip
                label={systemHealth?.status || 'Unknown'}
                color={getStatusColor(systemHealth?.status)}
                variant="filled"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Overview */}
      <Grid container spacing={3}>
        {/* Data Sources Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Sources
              </Typography>
              <Stack spacing={1}>
                {dataSources.map((source) => (
                  <Box
                    key={source.id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 1,
                      bgcolor: 'background.default',
                      borderRadius: 1,
                    }}
                  >
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {source.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {source.description}
                      </Typography>
                    </Box>
                    <Chip
                      label={source.available ? 'Available' : 'Offline'}
                      color={source.available ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Analyses */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Analyses
              </Typography>
              {recentAnalyses.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No recent analyses found
                </Typography>
              ) : (
                <Stack spacing={1}>
                  {recentAnalyses.slice(0, 5).map((analysis) => (
                    <Box
                      key={analysis.analysisId}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        p: 1,
                        bgcolor: 'background.default',
                        borderRadius: 1,
                        cursor: 'pointer',
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                      onClick={() => navigate(`/analysis/${analysis.analysisId}`)}
                    >
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          Analysis {analysis.analysisId.slice(0, 8)}...
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {analysis.result?.anomalies.length || 0} anomalies found
                        </Typography>
                      </Box>
                      <Chip
                        label={analysis.status}
                        color={getStatusColor(analysis.status)}
                        size="small"
                      />
                    </Box>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Current Analysis Summary */}
        {currentAnalysis && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Latest Analysis Results
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {currentAnalysis.result?.anomalies.length || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Anomalies Detected
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {currentAnalysis.result?.metadata.totalPoints.toLocaleString() || '0'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Data Points
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {currentAnalysis.processingTimeSeconds?.toFixed(1) || '0'}s
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Processing Time
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Button
                        variant="contained"
                        startIcon={<Visibility />}
                        onClick={() => navigate('/visualization')}
                        fullWidth
                      >
                        View 3D
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* System Health Details */}
        {systemHealth && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Health
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body1" fontWeight="medium">
                        Database
                      </Typography>
                      <Chip
                        label={systemHealth.services?.database || 'Unknown'}
                        color={getStatusColor(systemHealth.services?.database)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body1" fontWeight="medium">
                        Cache
                      </Typography>
                      <Chip
                        label={systemHealth.services?.cache || 'Unknown'}
                        color={getStatusColor(systemHealth.services?.cache)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body1" fontWeight="medium">
                        API
                      </Typography>
                      <Chip
                        label={systemHealth.status || 'Unknown'}
                        color={getStatusColor(systemHealth.status)}
                        size="small"
                      />
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};