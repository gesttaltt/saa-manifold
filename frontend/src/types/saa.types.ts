// Domain types for SAA analysis and visualization

export interface GeographicCoordinates {
  longitude: number;
  latitude: number;
  altitude: number;
}

export interface GeomagneticCoordinates {
  magneticLongitude: number;
  magneticLatitude: number;
  lShell: number;
  magneticLocalTime: number;
}

export interface GeographicRegion {
  longitudeMin: number;
  longitudeMax: number;
  latitudeMin: number;
  latitudeMax: number;
  altitudeMin: number;
  altitudeMax: number;
}

export interface SpatialBounds {
  longitudeSpan: number;
  latitudeSpan: number;
  altitudeSpan: number;
  characteristicLength: number;
}

export interface FluxIntensity {
  value: number;
  uncertainty: number;
  confidenceLevel: number;
  units: 'particles/cm²/s' | 'particles/cm²/s/sr' | 'particles/m²/s';
}

export interface EnergySpectrum {
  energyBins: Record<string, number>; // Energy bin -> flux value
  particleType: 'electron' | 'proton' | 'alpha' | 'heavy_ion';
  spectralIndex?: number;
}

export interface FluxData {
  electronFlux: FluxIntensity;
  protonFlux: FluxIntensity;
  measurementTimestamp: string;
  dataQuality: 'high' | 'medium' | 'low' | 'unknown';
  dataSource: string;
  energySpectrum?: EnergySpectrum;
  magneticFieldStrength?: number; // nT
}

export interface SAAAnomaly {
  id: string;
  centerCoordinates: GeographicCoordinates;
  intensityPeak: FluxIntensity;
  spatialExtent: SpatialBounds;
  detectionTimestamp: string;
  confidenceLevel: number;
  temporalStability?: number;
  driftRate?: number; // degrees/year
}

export interface ManifoldGeometry {
  vertices: number[][]; // [x, y, z] coordinates
  faces: number[][]; // Triangle indices
  fluxValues: number[];
}

export interface ColorMapping {
  minValue: number;
  maxValue: number;
  colorScale: 'plasma' | 'viridis' | 'jet' | 'rainbow' | 'custom';
  scaleType: 'linear' | 'logarithmic';
}

export interface AnomalyMarker {
  id: string;
  position: [number, number, number]; // [lon, lat, alt]
  intensity: number;
  confidence: number;
  radius: number;
  color: string;
  label: string;
}

export interface ManifoldData {
  geometry: ManifoldGeometry;
  materials: {
    colorMapping: ColorMapping;
    opacity: number;
    wireframe: boolean;
  };
  anomalyMarkers: AnomalyMarker[];
  metadata: {
    generationTimestamp: string;
    dataPointsUsed: number;
    anomaliesIncluded: number;
    gridResolution: [number, number, number];
    vertexCount: number;
    faceCount: number;
    fluxStatistics: {
      minFlux: number;
      maxFlux: number;
      meanFlux: number;
      stdFlux: number;
    };
  };
}

export interface AnalysisRequest {
  region: GeographicRegion;
  resolution: {
    longitudeStep: number;
    latitudeStep: number;
    altitudeStep: number;
  };
  dataSources: string[];
  analysisType: 'full_manifold' | 'anomaly_detection_only' | 'flux_mapping';
}

export interface AnalysisResult {
  analysisId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: {
    anomalies: SAAAnomaly[];
    manifoldData?: ManifoldData;
    metadata: {
      totalPoints: number;
      analysisTimestamp: string;
      processingTimeSeconds: number;
      dataQualityScore: number;
    };
  };
  error?: string;
  processingTimeSeconds?: number;
}

export interface AnalysisStatus {
  analysisId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progressPercentage: number;
  currentStage: string;
  estimatedCompletion?: string;
  errorMessage?: string;
}

export interface DataSource {
  id: string;
  name: string;
  description: string;
  version: string;
  coverage: {
    altitudeRange?: [number, number];
    temporalRange?: [string, string];
    spatialCoverage?: string;
  };
  available: boolean;
  lastUpdated: string;
  dataQuality: 'high' | 'medium' | 'low';
}

// Visualization types
export interface VisualizationOptions {
  colorScheme: ColorMapping['colorScale'];
  opacity: number;
  meshResolution: 'low' | 'medium' | 'high';
  includeMagneticFieldLines: boolean;
  showAnomalyMarkers: boolean;
  animationSpeed: number;
}

export interface CameraPosition {
  position: [number, number, number];
  target: [number, number, number];
  up: [number, number, number];
}

export interface ViewportSettings {
  camera: CameraPosition;
  lighting: {
    ambientIntensity: number;
    directionalIntensity: number;
    directionalPosition: [number, number, number];
  };
  background: {
    type: 'solid' | 'gradient' | 'skybox';
    color: string;
    gradientColors?: string[];
  };
}

// API response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  timestamp: string;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'progress_update' | 'analysis_complete' | 'error' | 'heartbeat';
  payload: any;
  timestamp: string;
}

export interface ProgressUpdate {
  analysisId: string;
  progress: number;
  stage: string;
  timestamp: string;
}

// User interface types
export interface FilterOptions {
  intensityRange: [number, number];
  confidenceThreshold: number;
  spatialExtentRange: [number, number];
  timeRange?: [string, string];
  dataSources: string[];
}

export interface ExportOptions {
  format: 'json' | 'csv' | 'netcdf' | 'hdf5' | 'gltf' | 'obj';
  includeMetadata: boolean;
  includeVisualization: boolean;
  resolution?: 'low' | 'medium' | 'high';
  filename?: string;
}