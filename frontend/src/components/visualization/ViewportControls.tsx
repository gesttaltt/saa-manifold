import React from 'react';
import { 
  Box, 
  IconButton, 
  Tooltip, 
  Paper,
  Stack 
} from '@mui/material';
import {
  CameraAlt,
  Refresh,
  Fullscreen,
  FullscreenExit,
  ZoomIn,
  ZoomOut,
  CenterFocusStrong,
} from '@mui/icons-material';

interface ViewportControlsProps {
  onCameraReset: () => void;
  onExportImage: () => void;
  onFullscreen?: () => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onCenter?: () => void;
  isFullscreen?: boolean;
}

export const ViewportControls: React.FC<ViewportControlsProps> = ({
  onCameraReset,
  onExportImage,
  onFullscreen,
  onZoomIn,
  onZoomOut,
  onCenter,
  isFullscreen = false,
}) => {
  return (
    <Paper
      sx={{
        position: 'absolute',
        top: 16,
        right: 16,
        p: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: 0.5,
        bgcolor: 'rgba(255, 255, 255, 0.9)',
        backdropFilter: 'blur(10px)',
      }}
    >
      <Stack spacing={0.5}>
        {/* Camera Reset */}
        <Tooltip title="Reset Camera View" placement="left">
          <IconButton size="small" onClick={onCameraReset}>
            <Refresh />
          </IconButton>
        </Tooltip>

        {/* Center View */}
        {onCenter && (
          <Tooltip title="Center on Anomalies" placement="left">
            <IconButton size="small" onClick={onCenter}>
              <CenterFocusStrong />
            </IconButton>
          </Tooltip>
        )}

        {/* Zoom Controls */}
        {onZoomIn && (
          <Tooltip title="Zoom In" placement="left">
            <IconButton size="small" onClick={onZoomIn}>
              <ZoomIn />
            </IconButton>
          </Tooltip>
        )}

        {onZoomOut && (
          <Tooltip title="Zoom Out" placement="left">
            <IconButton size="small" onClick={onZoomOut}>
              <ZoomOut />
            </IconButton>
          </Tooltip>
        )}

        {/* Fullscreen Toggle */}
        {onFullscreen && (
          <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"} placement="left">
            <IconButton size="small" onClick={onFullscreen}>
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        )}

        {/* Export Image */}
        <Tooltip title="Export as Image" placement="left">
          <IconButton size="small" onClick={onExportImage}>
            <CameraAlt />
          </IconButton>
        </Tooltip>
      </Stack>
    </Paper>
  );
};