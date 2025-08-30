import { useState, useCallback, useEffect } from 'react';
import {
  AnalysisRequest,
  AnalysisResult,
  AnalysisStatus,
  GeographicRegion,
} from '@types/saa.types';
import apiService from '@services/api.service';
import webSocketService from '@services/websocket.service';

interface UseSAAAnalysisReturn {
  // State
  currentAnalysis: AnalysisResult | null;
  analysisStatus: AnalysisStatus | null;
  isAnalyzing: boolean;
  progress: number;
  error: string | null;
  
  // Actions
  startAnalysis: (request: AnalysisRequest) => Promise<void>;
  cancelAnalysis: () => Promise<void>;
  retryAnalysis: () => Promise<void>;
  clearError: () => void;
  
  // Utilities
  getAnalysisById: (analysisId: string) => Promise<AnalysisResult | null>;
}

export const useSAAAnalysis = (): UseSAAAnalysisReturn => {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [lastRequest, setLastRequest] = useState<AnalysisRequest | null>(null);

  // Setup WebSocket handlers for real-time updates
  useEffect(() => {
    webSocketService.updateHandlers({
      onProgressUpdate: (update) => {
        setProgress(update.progress);
        setAnalysisStatus(prev => prev ? {
          ...prev,
          progressPercentage: update.progress,
          currentStage: update.stage,
        } : null);
      },
      
      onAnalysisComplete: (result) => {
        setCurrentAnalysis(result);
        setIsAnalyzing(false);
        setProgress(100);
        setAnalysisStatus(prev => prev ? {
          ...prev,
          status: 'completed',
          progressPercentage: 100,
        } : null);
      },
      
      onError: (errorMessage) => {
        setError(errorMessage);
        setIsAnalyzing(false);
        setAnalysisStatus(prev => prev ? {
          ...prev,
          status: 'failed',
          errorMessage,
        } : null);
      },
    });

    return () => {
      if (isAnalyzing) {
        webSocketService.disconnect();
      }
    };
  }, [isAnalyzing]);

  const startAnalysis = useCallback(async (request: AnalysisRequest) => {
    try {
      setError(null);
      setIsAnalyzing(true);
      setProgress(0);
      setCurrentAnalysis(null);
      setLastRequest(request);

      // Submit analysis request
      const response = await apiService.analyzeRegion(request);
      
      if (response.status === 'completed') {
        // Analysis completed immediately (e.g., cached result)
        setCurrentAnalysis(response);
        setIsAnalyzing(false);
        setProgress(100);
      } else {
        // Analysis is running - set up real-time monitoring
        setAnalysisStatus({
          analysisId: response.analysisId,
          status: response.status,
          progressPercentage: 0,
          currentStage: 'initializing',
        });

        // Connect to WebSocket for progress updates
        webSocketService.subscribeToAnalysis(response.analysisId);
        
        // Poll for status updates as backup
        pollAnalysisStatus(response.analysisId);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed to start';
      setError(errorMessage);
      setIsAnalyzing(false);
      setProgress(0);
    }
  }, []);

  const pollAnalysisStatus = useCallback(async (analysisId: string) => {
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes with 5-second intervals
    
    const poll = async () => {
      try {
        const status = await apiService.getAnalysisStatus(analysisId);
        setAnalysisStatus(status);
        setProgress(status.progressPercentage);

        if (status.status === 'completed') {
          // Fetch final results
          const result = await apiService.getAnalysisResult(analysisId);
          setCurrentAnalysis(result);
          setIsAnalyzing(false);
          return;
        } else if (status.status === 'failed') {
          setError(status.errorMessage || 'Analysis failed');
          setIsAnalyzing(false);
          return;
        }

        // Continue polling if still running
        if (status.status === 'running' && attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000);
        } else if (attempts >= maxAttempts) {
          setError('Analysis timed out');
          setIsAnalyzing(false);
        }
      } catch (err) {
        console.error('Error polling analysis status:', err);
        // Don't fail on polling errors, WebSocket might still work
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 10000); // Longer interval on error
        }
      }
    };

    setTimeout(poll, 2000); // Start polling after 2 seconds
  }, []);

  const cancelAnalysis = useCallback(async () => {
    if (!analysisStatus?.analysisId) {
      return;
    }

    try {
      await apiService.cancelAnalysis(analysisStatus.analysisId);
      setIsAnalyzing(false);
      setProgress(0);
      setAnalysisStatus(null);
      webSocketService.disconnect();
    } catch (err) {
      console.error('Failed to cancel analysis:', err);
      setError('Failed to cancel analysis');
    }
  }, [analysisStatus?.analysisId]);

  const retryAnalysis = useCallback(async () => {
    if (lastRequest) {
      await startAnalysis(lastRequest);
    }
  }, [lastRequest, startAnalysis]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const getAnalysisById = useCallback(async (analysisId: string): Promise<AnalysisResult | null> => {
    try {
      const result = await apiService.getAnalysisResult(analysisId);
      return result;
    } catch (err) {
      console.error('Failed to get analysis:', err);
      return null;
    }
  }, []);

  return {
    // State
    currentAnalysis,
    analysisStatus,
    isAnalyzing,
    progress,
    error,
    
    // Actions
    startAnalysis,
    cancelAnalysis,
    retryAnalysis,
    clearError,
    
    // Utilities
    getAnalysisById,
  };
};