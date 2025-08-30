from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from scipy.spatial.distance import cdist
from scipy.interpolate import RBFInterpolator
import logging
from datetime import datetime

from ...domain.entities.saa_anomaly import SAAAnomaly
from ...domain.value_objects.coordinates import GeographicCoordinates, GeographicRegion
from ...domain.value_objects.flux_data import FluxData


class ManifoldGenerationService:
    """
    Service for generating 3D flux manifolds from SAA analysis data.
    
    This service creates visualization-ready 3D manifolds that represent
    the spatial distribution of particle flux, enabling interactive
    exploration of SAA structures.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
    
    async def generate_manifold(
        self,
        flux_data: List[FluxData],
        region: GeographicRegion,
        anomalies: List[SAAAnomaly],
        resolution: Optional[Tuple[int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Generate 3D manifold data from flux measurements and detected anomalies.
        
        Args:
            flux_data: List of flux measurements
            region: Geographic region being visualized
            anomalies: Detected SAA anomalies
            resolution: Grid resolution (lon_points, lat_points, alt_points)
            
        Returns:
            Dictionary containing manifold geometry and metadata
        """
        if not flux_data:
            raise ManifoldGenerationError("No flux data provided for manifold generation")
        
        # Set default resolution
        resolution = resolution or (50, 50, 10)
        
        self._logger.info(
            f"Generating 3D manifold with resolution {resolution} "
            f"for {len(flux_data)} data points"
        )
        
        try:
            # Step 1: Create regular grid for interpolation
            grid_coords = self._create_regular_grid(region, resolution)
            
            # Step 2: Interpolate flux values onto grid
            interpolated_flux = await self._interpolate_flux_field(
                flux_data, grid_coords
            )
            
            # Step 3: Generate mesh geometry
            vertices, faces = await self._generate_mesh_geometry(
                grid_coords, interpolated_flux, region
            )
            
            # Step 4: Calculate color mapping and materials
            color_mapping = self._calculate_color_mapping(interpolated_flux)
            
            # Step 5: Add anomaly markers
            anomaly_markers = self._create_anomaly_markers(anomalies)
            
            # Step 6: Generate metadata
            metadata = self._generate_metadata(
                flux_data, anomalies, resolution, len(vertices), len(faces)
            )
            
            manifold_data = {
                "geometry": {
                    "vertices": vertices.tolist(),
                    "faces": faces.tolist(),
                    "flux_values": interpolated_flux.flatten().tolist()
                },
                "materials": {
                    "color_mapping": color_mapping,
                    "opacity": 0.8,
                    "wireframe": False
                },
                "anomaly_markers": anomaly_markers,
                "metadata": metadata
            }
            
            self._logger.info(
                f"Manifold generation completed: {len(vertices)} vertices, "
                f"{len(faces)} faces"
            )
            
            return manifold_data
            
        except Exception as e:
            self._logger.error(f"Manifold generation failed: {str(e)}")
            raise ManifoldGenerationError(f"Generation failed: {str(e)}") from e
    
    def _create_regular_grid(
        self,
        region: GeographicRegion,
        resolution: Tuple[int, int, int]
    ) -> np.ndarray:
        """Create a regular 3D grid of coordinates within the region."""
        lon_points, lat_points, alt_points = resolution
        
        # Create coordinate arrays
        longitudes = np.linspace(region.longitude_min, region.longitude_max, lon_points)
        latitudes = np.linspace(region.latitude_min, region.latitude_max, lat_points)
        altitudes = np.linspace(region.altitude_min, region.altitude_max, alt_points)
        
        # Create meshgrid
        LON, LAT, ALT = np.meshgrid(longitudes, latitudes, altitudes, indexing='ij')
        
        # Flatten and combine into coordinate array
        coords = np.column_stack([
            LON.flatten(),
            LAT.flatten(),
            ALT.flatten()
        ])
        
        return coords
    
    async def _interpolate_flux_field(
        self,
        flux_data: List[FluxData],
        grid_coords: np.ndarray
    ) -> np.ndarray:
        """
        Interpolate flux values from measurement points to regular grid.
        
        Uses Radial Basis Function (RBF) interpolation for smooth results.
        """
        if not flux_data:
            return np.zeros(len(grid_coords))
        
        # Extract measurement coordinates and flux values
        # Note: In real implementation, coordinates would be stored in FluxData
        measurement_coords = []
        flux_values = []
        
        for i, data in enumerate(flux_data):
            # Placeholder coordinates - would come from actual data
            coords = [
                -45.0 + (i % 10) * 1.0,  # longitude
                -20.0 + (i // 10) * 1.0,  # latitude
                500.0  # altitude
            ]
            measurement_coords.append(coords)
            flux_values.append(data.total_flux().value)
        
        measurement_coords = np.array(measurement_coords)
        flux_values = np.array(flux_values)
        
        # Handle edge case of single measurement
        if len(measurement_coords) == 1:
            # Use distance-based falloff from single point
            distances = cdist(grid_coords, measurement_coords).flatten()
            max_distance = np.max(distances)
            if max_distance > 0:
                interpolated = flux_values[0] * np.exp(-distances / (max_distance * 0.3))
            else:
                interpolated = np.full(len(grid_coords), flux_values[0])
        else:
            # Use RBF interpolation
            try:
                rbf_interpolator = RBFInterpolator(
                    measurement_coords,
                    flux_values,
                    kernel='gaussian',
                    epsilon=1.0,
                    smoothing=0.1
                )
                interpolated = rbf_interpolator(grid_coords)
            except Exception as e:
                self._logger.warning(f"RBF interpolation failed: {e}, using nearest neighbor")
                # Fallback to nearest neighbor
                interpolated = self._nearest_neighbor_interpolation(
                    measurement_coords, flux_values, grid_coords
                )
        
        return interpolated
    
    def _nearest_neighbor_interpolation(
        self,
        measurement_coords: np.ndarray,
        flux_values: np.ndarray,
        grid_coords: np.ndarray
    ) -> np.ndarray:
        """Fallback nearest neighbor interpolation."""
        distances = cdist(grid_coords, measurement_coords)
        nearest_indices = np.argmin(distances, axis=1)
        return flux_values[nearest_indices]
    
    async def _generate_mesh_geometry(
        self,
        grid_coords: np.ndarray,
        flux_values: np.ndarray,
        region: GeographicRegion
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate mesh vertices and faces for 3D visualization.
        
        Creates an isosurface at significant flux levels and a base surface.
        """
        # Reshape flux values back to 3D grid
        # For now, create a simple surface representation
        
        # Calculate significant flux threshold
        flux_threshold = np.percentile(flux_values[flux_values > 0], 75)
        
        # Find points above threshold
        significant_points = grid_coords[flux_values >= flux_threshold]
        significant_flux = flux_values[flux_values >= flux_threshold]
        
        if len(significant_points) == 0:
            # No significant flux, create base surface
            vertices, faces = self._create_base_surface(region)
        else:
            # Create manifold surface from significant points
            vertices, faces = self._create_flux_surface(
                significant_points, significant_flux, region
            )
        
        return vertices, faces
    
    def _create_base_surface(self, region: GeographicRegion) -> Tuple[np.ndarray, np.ndarray]:
        """Create a base surface when no significant flux is detected."""
        # Create a simple rectangular surface at mean altitude
        mean_alt = (region.altitude_min + region.altitude_max) / 2
        
        vertices = np.array([
            [region.longitude_min, region.latitude_min, mean_alt],
            [region.longitude_max, region.latitude_min, mean_alt],
            [region.longitude_max, region.latitude_max, mean_alt],
            [region.longitude_min, region.latitude_max, mean_alt]
        ])
        
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ])
        
        return vertices, faces
    
    def _create_flux_surface(
        self,
        points: np.ndarray,
        flux_values: np.ndarray,
        region: GeographicRegion
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create surface mesh from flux points using Delaunay triangulation."""
        from scipy.spatial import ConvexHull
        
        # Use 2D projection for surface generation (ignore altitude for now)
        points_2d = points[:, :2]  # longitude, latitude
        
        try:
            # Create convex hull for triangulation
            hull = ConvexHull(points_2d)
            
            # Create vertices with flux-weighted altitudes
            vertices = []
            for i, point in enumerate(points):
                # Weight altitude by flux intensity
                flux_weight = flux_values[i] / np.max(flux_values)
                weighted_alt = region.altitude_min + (region.altitude_max - region.altitude_min) * flux_weight
                vertices.append([point[0], point[1], weighted_alt])
            
            vertices = np.array(vertices)
            faces = hull.simplices
            
            return vertices, faces
            
        except Exception as e:
            self._logger.warning(f"Surface generation failed: {e}, using base surface")
            return self._create_base_surface(region)
    
    def _calculate_color_mapping(self, flux_values: np.ndarray) -> Dict[str, Any]:
        """Calculate color mapping parameters for visualization."""
        valid_flux = flux_values[flux_values > 0]
        
        if len(valid_flux) == 0:
            min_val, max_val = 0.0, 1.0
        else:
            min_val = float(np.min(valid_flux))
            max_val = float(np.max(valid_flux))
        
        return {
            "min_value": min_val,
            "max_value": max_val,
            "color_scale": "plasma",  # Default colormap
            "scale_type": "linear"
        }
    
    def _create_anomaly_markers(self, anomalies: List[SAAAnomaly]) -> List[Dict[str, Any]]:
        """Create markers for detected anomalies."""
        markers = []
        
        for anomaly in anomalies:
            marker = {
                "id": anomaly.id,
                "position": [
                    anomaly.center_coordinates.longitude,
                    anomaly.center_coordinates.latitude,
                    anomaly.center_coordinates.altitude
                ],
                "intensity": anomaly.intensity_peak.value,
                "confidence": anomaly.confidence_level,
                "radius": anomaly.spatial_extent.characteristic_length,
                "color": self._get_anomaly_color(anomaly.intensity_peak.value),
                "label": f"SAA-{anomaly.id[:8]}"
            }
            markers.append(marker)
        
        return markers
    
    def _get_anomaly_color(self, intensity: float) -> str:
        """Get color for anomaly marker based on intensity."""
        # Simple intensity-based color mapping
        if intensity > 2000:
            return "#ff0000"  # Red for high intensity
        elif intensity > 1000:
            return "#ff8800"  # Orange for medium intensity
        else:
            return "#ffff00"  # Yellow for low intensity
    
    def _generate_metadata(
        self,
        flux_data: List[FluxData],
        anomalies: List[SAAAnomaly],
        resolution: Tuple[int, int, int],
        vertex_count: int,
        face_count: int
    ) -> Dict[str, Any]:
        """Generate metadata for the manifold."""
        flux_values = [data.total_flux().value for data in flux_data]
        
        return {
            "generation_timestamp": datetime.utcnow().isoformat(),
            "data_points_used": len(flux_data),
            "anomalies_included": len(anomalies),
            "grid_resolution": resolution,
            "vertex_count": vertex_count,
            "face_count": face_count,
            "flux_statistics": {
                "min_flux": float(np.min(flux_values)) if flux_values else 0.0,
                "max_flux": float(np.max(flux_values)) if flux_values else 0.0,
                "mean_flux": float(np.mean(flux_values)) if flux_values else 0.0,
                "std_flux": float(np.std(flux_values)) if flux_values else 0.0
            },
            "generation_parameters": {
                "interpolation_method": "rbf",
                "surface_threshold_percentile": 75,
                "smoothing_factor": 0.1
            }
        }


class ManifoldGenerationError(Exception):
    """Raised when manifold generation fails."""
    pass