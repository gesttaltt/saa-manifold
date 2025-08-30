import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

export const Help: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Help & Documentation
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Help documentation interface coming soon...</Typography>
      </Paper>
    </Box>
  );
};