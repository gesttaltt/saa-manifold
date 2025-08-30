import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Stack,
} from '@mui/material';
import { Download, Settings } from '@mui/icons-material';

import { SAAManifoldViewer } from '@components/visualization/SAAManifoldViewer';
import { useSAAAnalysis } from '@hooks/useSAAAnalysis';
import { VisualizationOptions, ManifoldData } from '@types/saa.types';
import apiService from '@services/api.service';

export const Visualization: React.FC = () => {
  const { currentAnalysis } = useSAAAnalysis();
  
  const [manifoldData, setManifoldData] = useState<ManifoldData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [visualizationOptions, setVisualizationOptions] = useState<VisualizationOptions>({
    colorScheme: 'plasma',
    opacity: 0.8,
    meshResolution: 'medium',
    includeMagneticFieldLines: true,
    showAnomalyMarkers: true,
    animationSpeed: 1.0,
  });

  // Load manifold data when analysis is available
  useEffect(() => {
    if (currentAnalysis?.analysisId && currentAnalysis.status === 'completed') {
      loadManifoldData(currentAnalysis.analysisId);
    }
  }, [currentAnalysis]);

  const loadManifoldData = async (analysisId: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiService.generate3DManifold({
        analysisId,
        visualizationOptions: {
          colorScheme: visualizationOptions.colorScheme,
          opacity: visualizationOptions.opacity,
          meshResolution: visualizationOptions.meshResolution,
          includeMagneticFieldLines: visualizationOptions.includeMagneticFieldLines,
        },
      });
      
      setManifoldData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load manifold data');
    } finally {
      setLoading(false);
    }
  };

  const handleOptionsChange = (newOptions: Partial<VisualizationOptions>) => {
    setVisualizationOptions(prev => ({ ...prev, ...newOptions }));
    
    // Regenerate manifold if certain options changed
    const regenerationTriggers = ['colorScheme', 'meshResolution'];
    const shouldRegenerate = Object.keys(newOptions).some(key => 
      regenerationTriggers.includes(key)
    );
    
    if (shouldRegenerate && currentAnalysis?.analysisId) {
      loadManifoldData(currentAnalysis.analysisId);
    }
  };

  const handleExportVisualization = async (format: 'gltf' | 'obj' | 'png') => {
    if (!currentAnalysis?.analysisId) return;
    
    try {
      if (format === 'png') {
        // Export as image (handled by ViewportControls)
        return;
      }
      
      const blob = await apiService.exportVisualization({
        analysisId: currentAnalysis.analysisId,
        format,
        includeTextures: true,
      });
      
      // Download file
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `saa-manifold.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    }
  };

  // Show message if no analysis available
  if (!currentAnalysis) {
    return (
      <Box sx={{ textAlign: 'center', mt: 8 }}>
        <Typography variant="h5" gutterBottom>
          No Analysis Available
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Please run an analysis first to view the 3D manifold visualization.
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/analysis')}
          sx={{ mt: 2 }}
        >
          Start New Analysis
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ height: 'calc(100vh - 120px)' }}>
      {/* Header Controls */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">
            3D SAA Manifold Visualization
          </Typography>
          
          <Stack direction="row" spacing={1}>
            {/* Export Options */}
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Export</InputLabel>
              <Select
                value=""
                label="Export"
                onChange={(e) => handleExportVisualization(e.target.value as any)}
              >
                <MenuItem value="png">PNG Image</MenuItem>
                <MenuItem value="gltf">GLTF Model</MenuItem>
                <MenuItem value="obj">OBJ Model</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={() => {
                // Open visualization settings dialog
              }}
            >
              Settings
            </Button>
          </Stack>
        </Box>

        {/* Analysis Info */}
        <Box sx={{ mt: 1, display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Analysis ID: {currentAnalysis.analysisId.slice(0, 12)}...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            •
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {currentAnalysis.result?.anomalies.length || 0} anomalies detected
          </Typography>
          <Typography variant="body2" color="text.secondary">
            •
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Generated: {new Date(currentAnalysis.result?.metadata.analysisTimestamp || '').toLocaleString()}
          </Typography>
        </Box>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <Stack alignItems="center" spacing={2}>
            <CircularProgress size={60} />
            <Typography variant="body1">
              Generating 3D manifold visualization...
            </Typography>
          </Stack>
        </Box>
      )}

      {/* 3D Visualization */}
      {!loading && (
        <SAAManifoldViewer
          manifoldData={manifoldData}
          anomalies={currentAnalysis.result?.anomalies || []}
          options={visualizationOptions}
          onOptionsChange={handleOptionsChange}
          isLoading={loading}
        />
      )}
    </Box>
  );
};