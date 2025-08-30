import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import { AnomalyMarker } from '@types/saa.types';

interface AnomalyMarkersProps {
  markers: AnomalyMarker[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  showLabels: boolean;
}

interface MarkerSphereProps {
  marker: AnomalyMarker;
  isSelected: boolean;
  onClick: () => void;
}

const MarkerSphere: React.FC<MarkerSphereProps> = ({ marker, isSelected, onClick }) => {
  const sphereRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = React.useState(false);

  // Calculate marker size based on intensity and confidence
  const baseRadius = Math.max(0.5, Math.min(3.0, marker.radius / 100));
  const intensityScale = Math.max(0.5, Math.min(2.0, marker.intensity / 1000));
  const radius = baseRadius * intensityScale * (isSelected ? 1.5 : 1.0);

  // Animation
  useFrame((state, delta) => {
    if (sphereRef.current) {
      // Gentle pulsing animation for selected marker
      if (isSelected) {
        const pulse = 1 + 0.1 * Math.sin(state.clock.elapsedTime * 3);
        sphereRef.current.scale.setScalar(pulse);
      } else {
        sphereRef.current.scale.setScalar(1);
      }

      // Hover effect
      if (hovered && !isSelected) {
        const hover = 1 + 0.05 * Math.sin(state.clock.elapsedTime * 5);
        sphereRef.current.scale.setScalar(hover);
      }
    }
  });

  // Convert color to Three.js color
  const color = new THREE.Color(marker.color);

  return (
    <group position={marker.position}>
      {/* Main marker sphere */}
      <mesh
        ref={sphereRef}
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          setHovered(false);
          document.body.style.cursor = 'auto';
        }}
      >
        <sphereGeometry args={[radius, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 0.3 : hovered ? 0.2 : 0.1}
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Confidence ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius * 1.2, radius * 1.4, 32]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.3 * marker.confidence}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Intensity glow effect */}
      <mesh>
        <sphereGeometry args={[radius * 2, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.1 * (marker.intensity / 2000)}
        />
      </mesh>
    </group>
  );
};

export const AnomalyMarkers: React.FC<AnomalyMarkersProps> = ({
  markers,
  selectedId,
  onSelect,
  showLabels,
}) => {
  return (
    <group>
      {markers.map((marker) => (
        <React.Fragment key={marker.id}>
          {/* Marker sphere */}
          <MarkerSphere
            marker={marker}
            isSelected={selectedId === marker.id}
            onClick={() => onSelect(selectedId === marker.id ? null : marker.id)}
          />

          {/* Label */}
          {showLabels && (
            <Text
              position={[
                marker.position[0],
                marker.position[1],
                marker.position[2] + 5
              ]}
              fontSize={1}
              color={marker.color}
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.1}
              outlineColor="#000000"
            >
              {marker.label}
            </Text>
          )}

          {/* Selected marker info */}
          {selectedId === marker.id && (
            <group>
              {/* Selection highlight ring */}
              <mesh
                position={marker.position}
                rotation={[Math.PI / 2, 0, 0]}
              >
                <ringGeometry args={[marker.radius / 50, marker.radius / 40, 32]} />
                <meshBasicMaterial
                  color="#ffffff"
                  transparent
                  opacity={0.8}
                  side={THREE.DoubleSide}
                />
              </mesh>

              {/* Info panel background */}
              <mesh
                position={[
                  marker.position[0] + 8,
                  marker.position[1] + 3,
                  marker.position[2]
                ]}
              >
                <planeGeometry args={[12, 6]} />
                <meshBasicMaterial
                  color="#000000"
                  transparent
                  opacity={0.7}
                />
              </mesh>

              {/* Info text */}
              <Text
                position={[
                  marker.position[0] + 8,
                  marker.position[1] + 4,
                  marker.position[2] + 0.1
                ]}
                fontSize={0.8}
                color="#ffffff"
                anchorX="center"
                anchorY="top"
              >
                {`Intensity: ${marker.intensity.toFixed(1)}\nConfidence: ${(marker.confidence * 100).toFixed(1)}%`}
              </Text>
            </group>
          )}
        </React.Fragment>
      ))}
    </group>
  );
};