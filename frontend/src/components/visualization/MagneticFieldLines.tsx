import React, { useMemo } from 'react';
import { Line } from '@react-three/drei';
import * as THREE from 'three';
import { GeographicRegion } from '@types/saa.types';

interface MagneticFieldLinesProps {
  region: GeographicRegion;
  fieldLineCount?: number;
  color?: string;
  opacity?: number;
}

export const MagneticFieldLines: React.FC<MagneticFieldLinesProps> = ({
  region,
  fieldLineCount = 20,
  color = '#4fc3f7',
  opacity = 0.6,
}) => {
  // Generate magnetic field lines based on dipole field approximation
  const fieldLines = useMemo(() => {
    const lines: THREE.Vector3[][] = [];
    
    // Magnetic dipole parameters (simplified)
    const magneticPolePosition = new THREE.Vector3(-164, 86.5, 0); // Approximate magnetic north pole
    const earthRadius = 6371; // km
    
    // Generate field lines starting from various points
    for (let i = 0; i < fieldLineCount; i++) {
      const line: THREE.Vector3[] = [];
      
      // Starting point within the region
      const startLon = region.longitudeMin + (region.longitudeMax - region.longitudeMin) * (i / fieldLineCount);
      const startLat = region.latitudeMin + (region.latitudeMax - region.latitudeMin) * 0.5;
      const startAlt = region.altitudeMin;
      
      // Trace field line using simplified dipole field
      let currentPos = new THREE.Vector3(startLon, startLat, startAlt / 100); // Scale altitude
      line.push(currentPos.clone());
      
      // Trace field line points
      for (let step = 0; step < 50; step++) {
        // Calculate magnetic field direction (simplified dipole)
        const fieldDirection = calculateDipoleFieldDirection(
          currentPos,
          magneticPolePosition,
          earthRadius
        );
        
        // Step along field line
        const stepSize = 2.0; // Degrees
        currentPos.add(fieldDirection.multiplyScalar(stepSize));
        
        // Stop if we go too far outside the region
        if (currentPos.x < region.longitudeMin - 20 || 
            currentPos.x > region.longitudeMax + 20 ||
            currentPos.y < region.latitudeMin - 20 || 
            currentPos.y > region.latitudeMax + 20 ||
            currentPos.z > 20) { // Above visualization range
          break;
        }
        
        line.push(currentPos.clone());
      }
      
      if (line.length > 2) {
        lines.push(line);
      }
    }
    
    return lines;
  }, [region, fieldLineCount]);

  return (
    <group>
      {fieldLines.map((line, index) => (
        <Line
          key={index}
          points={line}
          color={color}
          lineWidth={1}
          transparent
          opacity={opacity}
        />
      ))}
    </group>
  );
};

// Helper function to calculate dipole field direction
function calculateDipoleFieldDirection(
  position: THREE.Vector3,
  polePosition: THREE.Vector3,
  earthRadius: number
): THREE.Vector3 {
  // Simplified dipole field calculation
  // In reality, this would use full IGRF-13 spherical harmonics
  
  // Convert to spherical coordinates relative to magnetic pole
  const toRadians = Math.PI / 180;
  
  // Vector from magnetic pole to position
  const deltaPos = position.clone().sub(polePosition);
  
  // Simplified dipole field direction
  // Points roughly toward magnetic poles with latitude dependence
  const latitudeFactor = Math.sin(position.y * toRadians);
  const longitudeFactor = Math.cos(position.x * toRadians);
  
  // Field direction (simplified)
  const fieldDirection = new THREE.Vector3(
    -deltaPos.x * 0.01,
    -latitudeFactor * 0.02,
    longitudeFactor * 0.015
  );
  
  return fieldDirection.normalize();
}