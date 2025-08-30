import React, { useMemo, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Grid, Box as DreiBox } from '@react-three/drei';
import { Box, Paper, Typography, Slider, FormControlLabel, Switch, Stack } from '@mui/material';
import * as THREE from 'three';

import { ManifoldData, VisualizationOptions, SAAAnomaly } from '@types/saa.types';
import { FluxManifoldMesh } from './FluxManifoldMesh';
import { AnomalyMarkers } from './AnomalyMarkers';
import { MagneticFieldLines } from './MagneticFieldLines';
import { CoordinateAxes } from './CoordinateAxes';
import { ViewportControls } from './ViewportControls';

interface SAAManifoldViewerProps {
  manifoldData: ManifoldData | null;
  anomalies: SAAAnomaly[];
  options: VisualizationOptions;
  onOptionsChange: (options: Partial<VisualizationOptions>) => void;
  isLoading?: boolean;
}

export const SAAManifoldViewer: React.FC<SAAManifoldViewerProps> = ({
  manifoldData,
  anomalies,
  options,
  onOptionsChange,
  isLoading = false,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraPosition, setCameraPosition] = useState<[number, number, number]>([50, 50, 50]);
  const [selectedAnomaly, setSelectedAnomaly] = useState<string | null>(null);

  // Process manifold data for Three.js
  const processedManifoldData = useMemo(() => {
    if (!manifoldData?.geometry) return null;

    const { vertices, faces, fluxValues } = manifoldData.geometry;
    
    // Convert to Three.js geometry
    const geometry = new THREE.BufferGeometry();
    
    // Convert vertices (lon, lat, alt) to Three.js coordinates
    const positions = new Float32Array(vertices.length * 3);
    for (let i = 0; i < vertices.length; i++) {
      const [lon, lat, alt] = vertices[i];
      // Convert geographic coordinates to 3D Cartesian
      // Scale for visualization: longitude -> x, latitude -> y, altitude -> z
      positions[i * 3] = lon;
      positions[i * 3 + 1] = lat;
      positions[i * 3 + 2] = alt / 100; // Scale altitude for better visualization
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    // Set faces
    const indices = new Uint32Array(faces.flat());
    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    
    // Add flux values as vertex colors
    const colors = new Float32Array(vertices.length * 3);
    const colorMap = new THREE.Color();
    const minFlux = manifoldData.metadata.fluxStatistics.minFlux;
    const maxFlux = manifoldData.metadata.fluxStatistics.maxFlux;
    
    for (let i = 0; i < vertices.length; i++) {
      const fluxValue = fluxValues[i];
      const normalizedFlux = (fluxValue - minFlux) / (maxFlux - minFlux);
      
      // Use plasma colormap approximation
      colorMap.setHSL(0.8 - normalizedFlux * 0.8, 0.9, 0.4 + normalizedFlux * 0.4);
      colors[i * 3] = colorMap.r;
      colors[i * 3 + 1] = colorMap.g;
      colors[i * 3 + 2] = colorMap.b;
    }
    
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.computeNormals();
    
    return {
      geometry,
      material: new THREE.MeshStandardMaterial({
        vertexColors: true,
        opacity: options.opacity,
        transparent: true,
        wireframe: options.meshResolution === 'low',
      }),
    };
  }, [manifoldData, options.opacity, options.meshResolution]);

  const handleAnomalySelect = (anomalyId: string | null) => {
    setSelectedAnomaly(anomalyId);
    
    if (anomalyId && anomalies) {
      const anomaly = anomalies.find(a => a.id === anomalyId);
      if (anomaly) {
        // Focus camera on selected anomaly
        const { longitude, latitude, altitude } = anomaly.centerCoordinates;
        setCameraPosition([longitude + 20, latitude + 20, altitude / 100 + 20]);
      }
    }
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          height: 600,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.paper',
          borderRadius: 2,
        }}
      >
        <Typography variant="h6" color="text.secondary">
          Generating 3D manifold visualization...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: 600, position: 'relative' }}>
      {/* 3D Canvas */}
      <Paper sx={{ height: '100%', overflow: 'hidden', borderRadius: 2 }}>
        <Canvas
          ref={canvasRef}
          camera={{
            position: cameraPosition,
            fov: 50,
            near: 0.1,
            far: 1000,
          }}
          shadows
          style={{ background: 'linear-gradient(to bottom, #1e3c72, #2a5298)' }}
        >
          {/* Lighting */}
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[50, 50, 50]}
            intensity={0.8}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-50, -50, 50]} intensity={0.3} />

          {/* Environment */}
          <Environment preset="space" />

          {/* Coordinate system */}
          <CoordinateAxes />

          {/* Ground grid */}
          <Grid
            position={[0, 0, -1]}
            args={[200, 200]}
            cellSize={10}
            cellThickness={0.5}
            cellColor="#444"
            sectionSize={50}
            sectionThickness={1}
            sectionColor="#666"
          />

          {/* Flux manifold mesh */}
          {processedManifoldData && (
            <FluxManifoldMesh
              geometry={processedManifoldData.geometry}
              material={processedManifoldData.material}
              options={options}
            />
          )}

          {/* SAA anomaly markers */}
          {manifoldData?.anomalyMarkers && (
            <AnomalyMarkers
              markers={manifoldData.anomalyMarkers}
              selectedId={selectedAnomaly}
              onSelect={handleAnomalySelect}
              showLabels={options.showAnomalyMarkers}
            />
          )}

          {/* Magnetic field lines */}
          {options.includeMagneticFieldLines && (
            <MagneticFieldLines
              region={{
                longitudeMin: -90,
                longitudeMax: 0,
                latitudeMin: -50,
                latitudeMax: 0,
                altitudeMin: 400,
                altitudeMax: 600,
              }}
            />
          )}

          {/* Interactive controls */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            maxDistance={200}
            minDistance={10}
            maxPolarAngle={Math.PI}
            target={[0, 0, 0]}
          />
        </Canvas>

        {/* Overlay controls */}
        <ViewportControls
          onCameraReset={() => setCameraPosition([50, 50, 50])}
          onExportImage={() => {
            // Export canvas as image
            if (canvasRef.current) {
              const link = document.createElement('a');
              link.download = 'saa-manifold.png';
              link.href = canvasRef.current.toDataURL();
              link.click();
            }
          }}
        />
      </Paper>

      {/* Visualization Controls Panel */}
      <Paper
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          p: 2,
          width: 300,
          maxHeight: 'calc(100% - 32px)',
          overflow: 'auto',
        }}
      >
        <Typography variant="h6" gutterBottom>
          Visualization Controls
        </Typography>

        <Stack spacing={2}>
          {/* Opacity Control */}
          <Box>
            <Typography variant="body2" gutterBottom>
              Opacity: {Math.round(options.opacity * 100)}%
            </Typography>
            <Slider
              value={options.opacity}
              onChange={(_, value) => onOptionsChange({ opacity: value as number })}
              min={0.1}
              max={1.0}
              step={0.1}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
            />
          </Box>

          {/* Animation Speed */}
          <Box>
            <Typography variant="body2" gutterBottom>
              Animation Speed: {options.animationSpeed}x
            </Typography>
            <Slider
              value={options.animationSpeed}
              onChange={(_, value) => onOptionsChange({ animationSpeed: value as number })}
              min={0.1}
              max={3.0}
              step={0.1}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${value}x`}
            />
          </Box>

          {/* Toggle Options */}
          <FormControlLabel
            control={
              <Switch
                checked={options.showAnomalyMarkers}
                onChange={(e) => onOptionsChange({ showAnomalyMarkers: e.target.checked })}
              />
            }
            label="Show Anomaly Markers"
          />

          <FormControlLabel
            control={
              <Switch
                checked={options.includeMagneticFieldLines}
                onChange={(e) => onOptionsChange({ includeMagneticFieldLines: e.target.checked })}
              />
            }
            label="Magnetic Field Lines"
          />

          {/* Color Scheme Selection */}
          <Box>
            <Typography variant="body2" gutterBottom>
              Color Scheme
            </Typography>
            <select
              value={options.colorScheme}
              onChange={(e) => onOptionsChange({ 
                colorScheme: e.target.value as VisualizationOptions['colorScheme']
              })}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ccc',
              }}
            >
              <option value="plasma">Plasma</option>
              <option value="viridis">Viridis</option>
              <option value="jet">Jet</option>
              <option value="rainbow">Rainbow</option>
            </select>
          </Box>

          {/* Mesh Resolution */}
          <Box>
            <Typography variant="body2" gutterBottom>
              Mesh Resolution
            </Typography>
            <select
              value={options.meshResolution}
              onChange={(e) => onOptionsChange({ 
                meshResolution: e.target.value as VisualizationOptions['meshResolution']
              })}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ccc',
              }}
            >
              <option value="low">Low (Wireframe)</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </Box>
        </Stack>

        {/* Manifold Statistics */}
        {manifoldData?.metadata && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>
              Manifold Statistics
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Vertices: {manifoldData.metadata.vertexCount.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Faces: {manifoldData.metadata.faceCount.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Data Points: {manifoldData.metadata.dataPointsUsed.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Anomalies: {manifoldData.metadata.anomaliesIncluded}
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Selected Anomaly Info */}
      {selectedAnomaly && (
        <Paper
          sx={{
            position: 'absolute',
            bottom: 16,
            right: 16,
            p: 2,
            width: 280,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Selected Anomaly
          </Typography>
          {(() => {
            const anomaly = anomalies.find(a => a.id === selectedAnomaly);
            if (!anomaly) return <Typography>Anomaly not found</Typography>;
            
            return (
              <Stack spacing={1}>
                <Typography variant="body2">
                  <strong>ID:</strong> {anomaly.id.slice(0, 8)}...
                </Typography>
                <Typography variant="body2">
                  <strong>Position:</strong> {anomaly.centerCoordinates.longitude.toFixed(2)}°, {anomaly.centerCoordinates.latitude.toFixed(2)}°
                </Typography>
                <Typography variant="body2">
                  <strong>Altitude:</strong> {anomaly.centerCoordinates.altitude.toFixed(0)} km
                </Typography>
                <Typography variant="body2">
                  <strong>Peak Intensity:</strong> {anomaly.intensityPeak.value.toFixed(1)} {anomaly.intensityPeak.units}
                </Typography>
                <Typography variant="body2">
                  <strong>Confidence:</strong> {(anomaly.confidenceLevel * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2">
                  <strong>Extent:</strong> {anomaly.spatialExtent.characteristicLength.toFixed(0)} km
                </Typography>
              </Stack>
            );
          })()}
        </Paper>
      )}
    </Box>
  );
};