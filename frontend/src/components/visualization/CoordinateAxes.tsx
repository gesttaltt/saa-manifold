import React from 'react';
import { Text } from '@react-three/drei';
import * as THREE from 'three';

export const CoordinateAxes: React.FC = () => {
  return (
    <group>
      {/* X-axis (Longitude) - Red */}
      <mesh>
        <cylinderGeometry args={[0.1, 0.1, 100, 8]} />
        <meshBasicMaterial color="#ff0000" />
        <mesh rotation={[0, 0, Math.PI / 2]} position={[50, 0, 0]}>
          <cylinderGeometry args={[0.1, 0.1, 100, 8]} />
          <meshBasicMaterial color="#ff0000" />
        </mesh>
      </mesh>
      
      {/* X-axis arrow */}
      <mesh position={[95, 0, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.5, 2, 8]} />
        <meshBasicMaterial color="#ff0000" />
      </mesh>
      
      {/* X-axis label */}
      <Text
        position={[100, 0, 2]}
        fontSize={2}
        color="#ff0000"
        anchorX="center"
        anchorY="middle"
      >
        Longitude (°)
      </Text>

      {/* Y-axis (Latitude) - Green */}
      <mesh rotation={[0, 0, Math.PI / 2]} position={[0, 50, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 100, 8]} />
        <meshBasicMaterial color="#00ff00" />
      </mesh>
      
      {/* Y-axis arrow */}
      <mesh position={[0, 95, 0]}>
        <coneGeometry args={[0.5, 2, 8]} />
        <meshBasicMaterial color="#00ff00" />
      </mesh>
      
      {/* Y-axis label */}
      <Text
        position={[0, 100, 2]}
        fontSize={2}
        color="#00ff00"
        anchorX="center"
        anchorY="middle"
      >
        Latitude (°)
      </Text>

      {/* Z-axis (Altitude) - Blue */}
      <mesh position={[0, 0, 5]}>
        <cylinderGeometry args={[0.1, 0.1, 10, 8]} />
        <meshBasicMaterial color="#0000ff" />
      </mesh>
      
      {/* Z-axis arrow */}
      <mesh position={[0, 0, 9.5]}>
        <coneGeometry args={[0.5, 2, 8]} />
        <meshBasicMaterial color="#0000ff" />
      </mesh>
      
      {/* Z-axis label */}
      <Text
        position={[2, 0, 12]}
        fontSize={2}
        color="#0000ff"
        anchorX="center"
        anchorY="middle"
      >
        Altitude (×100 km)
      </Text>

      {/* Origin marker */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.3, 8, 8]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>

      {/* Grid lines for reference */}
      {/* Longitude grid lines */}
      {Array.from({ length: 19 }, (_, i) => {
        const lon = -90 + i * 5;
        return (
          <group key={`lon-${lon}`}>
            <mesh rotation={[0, 0, Math.PI / 2]} position={[lon, 0, 0]}>
              <cylinderGeometry args={[0.02, 0.02, 100, 4]} />
              <meshBasicMaterial color="#333333" transparent opacity={0.3} />
            </mesh>
            
            {/* Longitude labels */}
            {i % 4 === 0 && (
              <Text
                position={[lon, -52, 0]}
                fontSize={1}
                color="#666666"
                anchorX="center"
                anchorY="middle"
              >
                {lon}°
              </Text>
            )}
          </group>
        );
      })}

      {/* Latitude grid lines */}
      {Array.from({ length: 11 }, (_, i) => {
        const lat = -50 + i * 5;
        return (
          <group key={`lat-${lat}`}>
            <mesh position={[0, lat, 0]}>
              <cylinderGeometry args={[0.02, 0.02, 180, 4]} />
              <meshBasicMaterial color="#333333" transparent opacity={0.3} />
            </mesh>
            
            {/* Latitude labels */}
            {i % 2 === 0 && (
              <Text
                position={[-92, lat, 0]}
                fontSize={1}
                color="#666666"
                anchorX="center"
                anchorY="middle"
              >
                {lat}°
              </Text>
            )}
          </group>
        );
      })}

      {/* Earth surface representation */}
      <mesh position={[0, 0, -1]} rotation={[Math.PI / 2, 0, 0]}>
        <circleGeometry args={[120, 64]} />
        <meshBasicMaterial 
          color="#4a90e2" 
          transparent 
          opacity={0.1}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
};