import {
  WebSocketMessage,
  ProgressUpdate,
  AnalysisStatus,
} from '@types/saa.types';

interface WebSocketEventHandlers {
  onProgressUpdate?: (update: ProgressUpdate) => void;
  onAnalysisComplete?: (result: any) => void;
  onError?: (error: string) => void;
  onConnectionChange?: (connected: boolean) => void;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private maxReconnectAttempts: number = 5;
  private reconnectAttempts: number = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingTimer: NodeJS.Timeout | null = null;
  private handlers: WebSocketEventHandlers = {};
  private subscriptions: Set<string> = new Set();

  private readonly wsBaseUrl: string;

  constructor() {
    this.wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws';
  }

  connect(handlers: WebSocketEventHandlers = {}): void {
    this.handlers = { ...this.handlers, ...handlers };

    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.ws = new WebSocket(`${this.wsBaseUrl}/general`);
      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.handleConnectionError();
    }
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = (event) => {
      console.log('WebSocket connected:', event);
      this.reconnectAttempts = 0;
      this.handlers.onConnectionChange?.(true);
      this.startPing();
      
      // Resubscribe to previous subscriptions
      this.subscriptions.forEach(subscription => {
        this.subscribe(subscription);
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.handlers.onConnectionChange?.(false);
      this.stopPing();
      
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.handleConnectionError();
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'progress_update':
        this.handlers.onProgressUpdate?.(message.payload as ProgressUpdate);
        break;
      
      case 'analysis_complete':
        this.handlers.onAnalysisComplete?.(message.payload);
        break;
      
      case 'error':
        this.handlers.onError?.(message.payload.message || 'WebSocket error');
        break;
      
      case 'heartbeat':
        // Respond to server ping
        this.send({ type: 'pong', payload: {}, timestamp: new Date().toISOString() });
        break;
      
      default:
        console.log('Unknown WebSocket message type:', message.type);
    }
  }

  private handleConnectionError(): void {
    this.handlers.onError?.('WebSocket connection failed');
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      this.connect();
    }, this.reconnectInterval);
  }

  private startPing(): void {
    this.pingTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          type: 'heartbeat',
          payload: {},
          timestamp: new Date().toISOString()
        });
      }
    }, 30000); // Ping every 30 seconds
  }

  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }

  // Subscribe to analysis progress updates
  subscribeToAnalysis(analysisId: string): void {
    const subscription = `analysis:${analysisId}`;
    this.subscriptions.add(subscription);
    this.subscribe(subscription);
  }

  // Subscribe to flux data stream
  subscribeToFluxStream(coordinates: {
    longitude: number;
    latitude: number;
    altitude: number;
  }, updateInterval: number = 60): void {
    const subscription = 'flux-stream';
    this.subscriptions.add(subscription);
    
    this.send({
      type: 'subscribe',
      payload: {
        subscription: 'flux-stream',
        coordinates,
        updateInterval
      },
      timestamp: new Date().toISOString()
    });
  }

  private subscribe(subscription: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({
        type: 'subscribe',
        payload: { subscription },
        timestamp: new Date().toISOString()
      });
    }
  }

  unsubscribe(subscription: string): void {
    this.subscriptions.delete(subscription);
    
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({
        type: 'unsubscribe',
        payload: { subscription },
        timestamp: new Date().toISOString()
      });
    }
  }

  disconnect(): void {
    this.subscriptions.clear();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    this.stopPing();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'DISCONNECTED';
      default:
        return 'UNKNOWN';
    }
  }

  // Update event handlers
  updateHandlers(handlers: Partial<WebSocketEventHandlers>): void {
    this.handlers = { ...this.handlers, ...handlers };
  }

  // Analysis-specific WebSocket connection
  connectToAnalysis(analysisId: string, handlers: WebSocketEventHandlers = {}): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.close();
    }

    try {
      this.ws = new WebSocket(`${this.wsBaseUrl}/analysis/${analysisId}`);
      this.handlers = { ...this.handlers, ...handlers };
      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to create analysis WebSocket connection:', error);
      handlers.onError?.('Failed to connect to analysis updates');
    }
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;