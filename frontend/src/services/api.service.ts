import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  AnalysisRequest,
  AnalysisResult,
  AnalysisStatus,
  DataSource,
  GeographicCoordinates,
  FluxData,
  ManifoldData,
  ApiResponse,
  ApiError,
} from '@types/saa.types';

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 300000, // 5 minutes timeout for long analyses
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for adding auth tokens
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health and status endpoints
  async getHealth(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async getDataSources(): Promise<DataSource[]> {
    const response = await this.client.get<ApiResponse<{ dataSources: DataSource[] }>>('/data-sources');
    return response.data.data?.dataSources || response.data.dataSources;
  }

  // SAA Analysis endpoints
  async analyzeRegion(request: AnalysisRequest): Promise<AnalysisResult> {
    try {
      const response = await this.client.post<AnalysisResult>('/saa/analyze-region', request);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
    try {
      const response = await this.client.get<AnalysisStatus>(`/saa/analysis/${analysisId}/status`);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async getAnalysisResult(analysisId: string): Promise<AnalysisResult> {
    try {
      const response = await this.client.get<AnalysisResult>(`/saa/analysis/${analysisId}`);
      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async cancelAnalysis(analysisId: string): Promise<boolean> {
    try {
      const response = await this.client.delete(`/saa/analysis/${analysisId}`);
      return response.status === 200;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  // Flux data endpoints
  async getPointFlux(coordinates: GeographicCoordinates): Promise<FluxData> {
    try {
      const params = {
        longitude: coordinates.longitude,
        latitude: coordinates.latitude,
        altitude: coordinates.altitude,
      };
      const response = await this.client.get<ApiResponse<FluxData>>('/flux/point', { params });
      return response.data.data || response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async getRegionalFlux(request: {
    region: {
      longitudeMin: number;
      longitudeMax: number;
      latitudeMin: number;
      latitudeMax: number;
      altitude: number;
    };
    resolution: number;
    dataSource: string;
  }): Promise<FluxData[]> {
    try {
      const response = await this.client.post<ApiResponse<FluxData[]>>('/flux/region', request);
      return response.data.data || response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  // Visualization endpoints
  async generate3DManifold(request: {
    analysisId: string;
    visualizationOptions: {
      colorScheme: string;
      opacity: number;
      meshResolution: string;
      includeMagneticFieldLines: boolean;
    };
  }): Promise<ManifoldData> {
    try {
      const response = await this.client.post<ApiResponse<ManifoldData>>('/visualization/3d-manifold', request);
      return response.data.data || response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async exportVisualization(request: {
    analysisId: string;
    format: 'gltf' | 'obj' | 'ply';
    includeTextures: boolean;
  }): Promise<Blob> {
    try {
      const response = await this.client.post('/visualization/export', request, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async exportData(request: {
    analysisId: string;
    format: 'json' | 'csv' | 'netcdf' | 'hdf5';
    includeMetadata: boolean;
  }): Promise<Blob> {
    try {
      const response = await this.client.post('/data/export', request, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  // Historical data endpoints
  async getHistoricalAnalyses(params: {
    region?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
  }): Promise<AnalysisResult[]> {
    try {
      const response = await this.client.get<ApiResponse<AnalysisResult[]>>('/saa/historical', { params });
      return response.data.data || response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async getFluxTimeSeries(request: {
    coordinates: GeographicCoordinates;
    startDate: string;
    endDate: string;
    resolution: 'hourly' | 'daily' | 'monthly';
  }): Promise<FluxData[]> {
    try {
      const response = await this.client.post<ApiResponse<FluxData[]>>('/flux/time-series', request);
      return response.data.data || response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  // Utility methods
  private handleApiError(error: AxiosError): Error {
    if (error.response?.data) {
      const apiError = error.response.data as ApiError;
      return new Error(apiError.error?.message || 'API request failed');
    } else if (error.request) {
      return new Error('Network error - please check your connection');
    } else {
      return new Error(error.message || 'Unknown error occurred');
    }
  }

  // Upload file for analysis
  async uploadDataFile(file: File, dataType: string): Promise<{ fileId: string; filename: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('dataType', dataType);

      const response = await this.client.post('/data/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          // You can emit this progress to a store or event system
          console.log(`Upload Progress: ${percentCompleted}%`);
        },
      });

      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  // Configuration management
  async getConfiguration(): Promise<any> {
    try {
      const response = await this.client.get('/config');
      return response.data;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }

  async updateConfiguration(config: any): Promise<boolean> {
    try {
      const response = await this.client.put('/config', config);
      return response.status === 200;
    } catch (error) {
      throw this.handleApiError(error as AxiosError);
    }
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;