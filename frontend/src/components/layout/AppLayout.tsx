import React, { useState } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Science,
  Visibility,
  DataObject,
  History,
  Settings,
  Help,
  ChevronLeft,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 280;

interface AppLayoutProps {
  children: React.ReactNode;
}

interface NavigationItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  description?: string;
}

const navigationItems: NavigationItem[] = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/',
    description: 'Overview and quick actions'
  },
  {
    text: 'Analysis',
    icon: <Science />,
    path: '/analysis',
    description: 'Create new SAA analysis'
  },
  {
    text: 'Visualization',
    icon: <Visibility />,
    path: '/visualization',
    description: '3D manifold visualization'
  },
  {
    text: 'Data Explorer',
    icon: <DataObject />,
    path: '/data',
    description: 'Browse flux data and sources'
  },
  {
    text: 'History',
    icon: <History />,
    path: '/history',
    description: 'Previous analyses and results'
  },
];

const settingsItems: NavigationItem[] = [
  {
    text: 'Settings',
    icon: <Settings />,
    path: '/settings',
    description: 'Application preferences'
  },
  {
    text: 'Help',
    icon: <Help />,
    path: '/help',
    description: 'Documentation and support'
  },
];

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('lg'));
  const navigate = useNavigate();
  const location = useLocation();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopOpen, setDesktopOpen] = useState(true);

  const handleDrawerToggle = () => {
    if (isMobile) {
      setMobileOpen(!mobileOpen);
    } else {
      setDesktopOpen(!desktopOpen);
    }
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const renderNavigationItems = (items: NavigationItem[], showDivider = false) => (
    <>
      {showDivider && <Divider sx={{ my: 1 }} />}
      {items.map((item) => (
        <ListItem key={item.path} disablePadding>
          <ListItemButton
            selected={location.pathname === item.path}
            onClick={() => handleNavigation(item.path)}
            sx={{
              minHeight: 48,
              px: 2.5,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: desktopOpen || mobileOpen ? 3 : 'auto',
                justifyContent: 'center',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.text}
              secondary={item.description}
              sx={{
                opacity: desktopOpen || mobileOpen ? 1 : 0,
                '& .MuiListItemText-secondary': {
                  fontSize: '0.75rem',
                  color: 'text.secondary',
                },
              }}
            />
          </ListItemButton>
        </ListItem>
      ))}
    </>
  );

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: desktopOpen || mobileOpen ? 'space-between' : 'center',
          px: [1],
        }}
      >
        {(desktopOpen || mobileOpen) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Science color="primary" />
            <Typography variant="h6" noWrap component="div" color="primary">
              SAA Platform
            </Typography>
          </Box>
        )}
        {!isMobile && (
          <IconButton onClick={handleDrawerToggle} size="small">
            <ChevronLeft />
          </IconButton>
        )}
      </Toolbar>

      <Divider />

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List>
          {renderNavigationItems(navigationItems)}
          {renderNavigationItems(settingsItems, true)}
        </List>
      </Box>

      {/* Footer */}
      {(desktopOpen || mobileOpen) && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            SAA Manifold Research Platform
          </Typography>
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            Version 1.0.0
          </Typography>
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { lg: desktopOpen ? `calc(100% - ${drawerWidth}px)` : '100%' },
          ml: { lg: desktopOpen ? `${drawerWidth}px` : 0 },
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            South Atlantic Anomaly Analysis
          </Typography>

          {/* Connection Status */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'success.main', // Would be dynamic based on connection status
              }}
            />
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              Connected
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { lg: desktopOpen ? drawerWidth : theme.spacing(7) }, flexShrink: { lg: 0 } }}
        aria-label="navigation"
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', lg: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', lg: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: desktopOpen ? drawerWidth : theme.spacing(7),
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
            },
          }}
          open={desktopOpen}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: {
            lg: desktopOpen ? `calc(100% - ${drawerWidth}px)` : `calc(100% - ${theme.spacing(7)})`
          },
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};