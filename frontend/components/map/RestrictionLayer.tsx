'use client';

import React, { useEffect } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';

interface RestrictionLayerProps {
  data: GeoJSON.FeatureCollection;
  visible?: boolean;
  onSelectRestriction?: (props: any) => void;
}

const SOURCE_ID = 'restrictions-source';
const FILL_LAYER_ID = 'restrictions-fill-layer';
const OUTLINE_LAYER_ID = 'restrictions-outline-layer';

export const RestrictionLayer: React.FC<RestrictionLayerProps> = ({
  data,
  visible = true,
  onSelectRestriction,
}) => {
  const { map, isLoaded } = useMarineMap();

  useEffect(() => {
    if (!map || !isLoaded) return;

    const safeAddPolygon = () => {
      if (!map.isStyleLoaded()) {
        map.once('styledata', safeAddPolygon);
        return;
      }

      if (!map.getSource(SOURCE_ID)) {
        map.addSource(SOURCE_ID, {
          type: 'geojson',
          data,
        });

        // Layer 1: Restricted area fill
        map.addLayer({
          id: FILL_LAYER_ID,
          type: 'fill',
          source: SOURCE_ID,
          paint: {
            'fill-color': '#ef4444',
            'fill-opacity': 0.22,
          },
        });

        // Layer 2: Restricted area perimeter border
        map.addLayer({
          id: OUTLINE_LAYER_ID,
          type: 'line',
          source: SOURCE_ID,
          paint: {
            'line-color': '#ef4444',
            'line-width': 2.2,
            'line-dasharray': [3, 2],
          },
        });

        map.on('mouseenter', FILL_LAYER_ID, () => {
          map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', FILL_LAYER_ID, () => {
          map.getCanvas().style.cursor = '';
        });

        const popup = new maplibregl.Popup({
          offset: 14,
          closeButton: true,
        });

        map.on('click', FILL_LAYER_ID, (e) => {
          if (!e.features || !e.features[0]) return;
          const props = e.features[0].properties;
          const coordinates = e.lngLat;

          if (props) {
            popup
              .setLngLat(coordinates)
              .setHTML(`
                <div style="font-family: inherit; font-size: 11px; padding: 6px 8px; color: #0a1324; max-width: 240px;">
                  <div style="display: flex; align-items: center; gap: 4px; color: #b91c1c; font-weight: 700; margin-bottom: 3px;">
                    <span>⛔ RESTRICTED AREA</span>
                  </div>
                  <strong style="color: #1e293b; font-size: 12px;">${props.name}</strong>
                  <p style="font-size: 10px; color: #475569; margin: 4px 0;">${props.description}</p>
                  <div style="background: #fef2f2; border-left: 2.5px solid #ef4444; padding: 4px; font-size: 9.5px; color: #991b1b;">
                    ${props.legal_notice}
                  </div>
                  <div style="margin-top: 4px; font-size: 9px; color: #64748b;">
                    Auth: <em>${props.authority}</em>
                  </div>
                </div>
              `)
              .addTo(map);

            if (onSelectRestriction) {
              onSelectRestriction(props);
            }
          }
        });
      } else {
        const source = map.getSource(SOURCE_ID) as maplibregl.GeoJSONSource;
        source.setData(data);
      }

      if (map.getLayer(FILL_LAYER_ID)) {
        map.setLayoutProperty(FILL_LAYER_ID, 'visibility', visible ? 'visible' : 'none');
      }
      if (map.getLayer(OUTLINE_LAYER_ID)) {
        map.setLayoutProperty(OUTLINE_LAYER_ID, 'visibility', visible ? 'visible' : 'none');
      }
    };

    safeAddPolygon();

    return () => {
      if (map && map.getStyle()) {
        if (map.getLayer(OUTLINE_LAYER_ID)) map.removeLayer(OUTLINE_LAYER_ID);
        if (map.getLayer(FILL_LAYER_ID)) map.removeLayer(FILL_LAYER_ID);
        if (map.getSource(SOURCE_ID)) map.removeSource(SOURCE_ID);
      }
    };
  }, [map, isLoaded, data, visible]);

  return null;
};
