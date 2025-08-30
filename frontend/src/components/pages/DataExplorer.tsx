import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

export const DataExplorer: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Explorer
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Data exploration interface coming soon...</Typography>
      </Paper>
    </Box>
  );
};