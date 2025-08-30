import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Alert,
  LinearProgress,
  Stack,
  Divider,
} from '@mui/material';
import { PlayArrow, Stop, Refresh } from '@mui/icons-material';

import { useSAAAnalysis } from '@hooks/useSAAAnalysis';
import { AnalysisRequest, GeographicRegion, DataSource } from '@types/saa.types';
import apiService from '@services/api.service';

export const Analysis: React.FC = () => {
  const {
    currentAnalysis,
    analysisStatus,
    isAnalyzing,
    progress,
    error,
    startAnalysis,
    cancelAnalysis,
    retryAnalysis,
    clearError,
  } = useSAAAnalysis();

  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [formData, setFormData] = useState({
    longitudeMin: -90,
    longitudeMax: 0,
    latitudeMin: -50,
    latitudeMax: 0,
    altitudeMin: 400,
    altitudeMax: 600,
    longitudeStep: 1.0,
    latitudeStep: 1.0,
    altitudeStep: 10.0,
    selectedDataSources: ['ae9_ap9'],
    analysisType: 'full_manifold' as const,
  });

  useEffect(() => {
    loadDataSources();
  }, []);

  const loadDataSources = async () => {
    try {
      const sources = await apiService.getDataSources();
      setDataSources(sources);
    } catch (err) {
      console.error('Failed to load data sources:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    const region: GeographicRegion = {
      longitudeMin: formData.longitudeMin,
      longitudeMax: formData.longitudeMax,
      latitudeMin: formData.latitudeMin,
      latitudeMax: formData.latitudeMax,
      altitudeMin: formData.altitudeMin,
      altitudeMax: formData.altitudeMax,
    };

    const request: AnalysisRequest = {
      region,
      resolution: {
        longitudeStep: formData.longitudeStep,
        latitudeStep: formData.latitudeStep,
        altitudeStep: formData.altitudeStep,
      },
      dataSources: formData.selectedDataSources,
      analysisType: formData.analysisType,
    };

    await startAnalysis(request);
  };

  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const loadPresetRegion = (preset: string) => {
    switch (preset) {
      case 'saa_core':
        setFormData(prev => ({
          ...prev,
          longitudeMin: -60,
          longitudeMax: -20,
          latitudeMin: -40,
          latitudeMax: -10,
          altitudeMin: 400,
          altitudeMax: 600,
        }));
        break;
      case 'south_america':
        setFormData(prev => ({
          ...prev,
          longitudeMin: -90,
          longitudeMax: -30,
          latitudeMin: -60,
          latitudeMax: 20,
          altitudeMin: 300,
          altitudeMax: 800,
        }));
        break;
      case 'south_atlantic':
        setFormData(prev => ({
          ...prev,
          longitudeMin: -50,
          longitudeMax: 20,
          latitudeMin: -50,
          latitudeMax: 0,
          altitudeMin: 400,
          altitudeMax: 600,
        }));
        break;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Typography variant="h4" component="h1" gutterBottom>
        SAA Region Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Configure and run analysis of the South Atlantic Anomaly manifold structure.
      </Typography>

      <Grid container spacing={3}>
        {/* Analysis Configuration */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Configuration
            </Typography>

            <form onSubmit={handleSubmit}>
              <Stack spacing={3}>
                {/* Preset Regions */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Quick Presets
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Button size="small" onClick={() => loadPresetRegion('saa_core')}>
                      SAA Core
                    </Button>
                    <Button size="small" onClick={() => loadPresetRegion('south_america')}>
                      South America
                    </Button>
                    <Button size="small" onClick={() => loadPresetRegion('south_atlantic')}>
                      South Atlantic
                    </Button>
                  </Stack>
                </Box>

                <Divider />

                {/* Geographic Region */}
                <Typography variant="subtitle1">Geographic Region</Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      label="Longitude Min"
                      type="number"
                      value={formData.longitudeMin}
                      onChange={(e) => handleFieldChange('longitudeMin', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: -180, max: 180, step: 0.1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Longitude Max"
                      type="number"
                      value={formData.longitudeMax}
                      onChange={(e) => handleFieldChange('longitudeMax', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: -180, max: 180, step: 0.1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Latitude Min"
                      type="number"
                      value={formData.latitudeMin}
                      onChange={(e) => handleFieldChange('latitudeMin', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: -90, max: 90, step: 0.1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Latitude Max"
                      type="number"
                      value={formData.latitudeMax}
                      onChange={(e) => handleFieldChange('latitudeMax', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: -90, max: 90, step: 0.1 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Altitude Min (km)"
                      type="number"
                      value={formData.altitudeMin}
                      onChange={(e) => handleFieldChange('altitudeMin', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 0, max: 50000, step: 10 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      label="Altitude Max (km)"
                      type="number"
                      value={formData.altitudeMax}
                      onChange={(e) => handleFieldChange('altitudeMax', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 0, max: 50000, step: 10 }}
                    />
                  </Grid>
                </Grid>

                {/* Resolution Settings */}
                <Typography variant="subtitle1">Resolution</Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <TextField
                      label="Lon Step (°)"
                      type="number"
                      value={formData.longitudeStep}
                      onChange={(e) => handleFieldChange('longitudeStep', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 0.1, max: 10, step: 0.1 }}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      label="Lat Step (°)"
                      type="number"
                      value={formData.latitudeStep}
                      onChange={(e) => handleFieldChange('latitudeStep', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 0.1, max: 10, step: 0.1 }}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      label="Alt Step (km)"
                      type="number"
                      value={formData.altitudeStep}
                      onChange={(e) => handleFieldChange('altitudeStep', parseFloat(e.target.value))}
                      fullWidth
                      size="small"
                      inputProps={{ min: 1, max: 100, step: 1 }}
                    />
                  </Grid>
                </Grid>

                {/* Data Sources */}
                <FormControl fullWidth>
                  <InputLabel>Data Sources</InputLabel>
                  <Select
                    multiple
                    value={formData.selectedDataSources}
                    onChange={(e) => handleFieldChange('selectedDataSources', e.target.value)}
                    renderValue={(selected) => selected.join(', ')}
                  >
                    {dataSources.map((source) => (
                      <MenuItem key={source.id} value={source.id}>
                        <Checkbox checked={formData.selectedDataSources.includes(source.id)} />
                        {source.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Analysis Type */}
                <FormControl fullWidth>
                  <InputLabel>Analysis Type</InputLabel>
                  <Select
                    value={formData.analysisType}
                    onChange={(e) => handleFieldChange('analysisType', e.target.value)}
                  >
                    <MenuItem value="full_manifold">Full Manifold Analysis</MenuItem>
                    <MenuItem value="anomaly_detection_only">Anomaly Detection Only</MenuItem>
                    <MenuItem value="flux_mapping">Flux Mapping</MenuItem>
                  </Select>
                </FormControl>

                {/* Submit Button */}
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={isAnalyzing}
                  startIcon={isAnalyzing ? <Stop /> : <PlayArrow />}
                  fullWidth
                >
                  {isAnalyzing ? 'Cancel Analysis' : 'Start Analysis'}
                </Button>

                {/* Retry Button */}
                {error && !isAnalyzing && (
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={retryAnalysis}
                    fullWidth
                  >
                    Retry Analysis
                  </Button>
                )}
              </Stack>
            </form>
          </Paper>
        </Grid>

        {/* Analysis Status and Results */}
        <Grid item xs={12} lg={8}>
          <Stack spacing={2}>
            {/* Error Display */}
            {error && (
              <Alert severity="error" onClose={clearError}>
                {error}
              </Alert>
            )}

            {/* Analysis Progress */}
            {isAnalyzing && analysisStatus && (
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Analysis Progress
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    {analysisStatus.currentStage}
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={progress} 
                    sx={{ mt: 1, height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {Math.round(progress)}% complete
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">
                    Analysis ID: {analysisStatus.analysisId.slice(0, 12)}...
                  </Typography>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={cancelAnalysis}
                    startIcon={<Stop />}
                  >
                    Cancel
                  </Button>
                </Box>
              </Paper>
            )}

            {/* Analysis Results */}
            {currentAnalysis && currentAnalysis.status === 'completed' && (
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>

                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.main', borderRadius: 2, color: 'white' }}>
                      <Typography variant="h4">
                        {currentAnalysis.result?.anomalies.length || 0}
                      </Typography>
                      <Typography variant="body2">
                        Anomalies Detected
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'secondary.main', borderRadius: 2, color: 'white' }}>
                      <Typography variant="h4">
                        {currentAnalysis.result?.metadata.totalPoints.toLocaleString() || '0'}
                      </Typography>
                      <Typography variant="body2">
                        Data Points
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.main', borderRadius: 2, color: 'white' }}>
                      <Typography variant="h4">
                        {currentAnalysis.processingTimeSeconds?.toFixed(1) || '0'}s
                      </Typography>
                      <Typography variant="body2">
                        Processing Time
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.main', borderRadius: 2, color: 'white' }}>
                      <Typography variant="h4">
                        {((currentAnalysis.result?.metadata.dataQualityScore || 0) * 100).toFixed(0)}%
                      </Typography>
                      <Typography variant="body2">
                        Data Quality
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                {/* Detected Anomalies */}
                {currentAnalysis.result?.anomalies && currentAnalysis.result.anomalies.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Detected Anomalies
                    </Typography>
                    <Stack spacing={1}>
                      {currentAnalysis.result.anomalies.map((anomaly, index) => (
                        <Box
                          key={anomaly.id}
                          sx={{
                            p: 2,
                            bgcolor: 'background.default',
                            borderRadius: 1,
                            border: 1,
                            borderColor: 'divider',
                          }}
                        >
                          <Grid container spacing={2} alignItems="center">
                            <Grid item xs={12} sm={3}>
                              <Typography variant="body1" fontWeight="medium">
                                Anomaly #{index + 1}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                ID: {anomaly.id.slice(0, 8)}...
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={3}>
                              <Typography variant="body2">
                                <strong>Position:</strong><br />
                                {anomaly.centerCoordinates.longitude.toFixed(2)}°, {anomaly.centerCoordinates.latitude.toFixed(2)}°
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={3}>
                              <Typography variant="body2">
                                <strong>Peak Intensity:</strong><br />
                                {anomaly.intensityPeak.value.toFixed(1)} {anomaly.intensityPeak.units}
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={3}>
                              <Typography variant="body2">
                                <strong>Confidence:</strong><br />
                                {(anomaly.confidenceLevel * 100).toFixed(1)}%
                              </Typography>
                            </Grid>
                          </Grid>
                        </Box>
                      ))}
                    </Stack>
                  </Box>
                )}

                {/* Action Buttons */}
                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => window.open('/visualization', '_blank')}
                    startIcon={<Visibility />}
                  >
                    View 3D Visualization
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => {
                      // Export functionality
                    }}
                    startIcon={<Download />}
                  >
                    Export Results
                  </Button>
                </Box>
              </Paper>
            )}

            {/* No Results State */}
            {!currentAnalysis && !isAnalyzing && (
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Science sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Ready to Analyze
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Configure your analysis parameters and click "Start Analysis" to begin.
                </Typography>
              </Paper>
            )}
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
};