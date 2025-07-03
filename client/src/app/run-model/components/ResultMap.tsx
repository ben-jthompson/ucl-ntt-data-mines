"use client";

import { MapContainer, TileLayer, Marker, Circle, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Apply default marker
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

function LocationMarker({
  coords,
  radius,
}: {
  coords: [number, number] | null;
  radius: number;
}) {
  return coords ? (
    <>
      <Marker position={coords}>
        <Popup>
          lat: {Math.round(coords[0] * 10000) / 10000}; lng:{" "}
          {Math.round(coords[1] * 10000) / 10000}
        </Popup>
      </Marker>
      <Circle center={coords} radius={radius} />
    </>
  ) : null;
}

export default function ResultMap({
  coords,
  radius,
}: {
  coords: [number, number] | null;
  radius: number;
}) {
  return (
    <MapContainer
      center={{ lat: 53.505, lng: -0.09 }}
      zoom={6}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      <LocationMarker coords={coords} radius={radius} />
    </MapContainer>
  );
}
