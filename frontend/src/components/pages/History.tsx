import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

export const History: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analysis History
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Historical analyses interface coming soon...</Typography>
      </Paper>
    </Box>
  );
};