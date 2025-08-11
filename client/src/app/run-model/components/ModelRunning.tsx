"use client";

import {
  Grid,
  Box,
  Typography,
  Link,
  Accordion,
  AccordionDetails,
  AccordionSummary,
} from "@mui/material";

import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import { useState, useEffect } from "react";
import UploadWidget from "./UploadWidget";
import dynamic from "next/dynamic";
import { EventSource } from "eventsource";

const ResultMap = dynamic(() => import("../../../components/ResultMap"), {
  ssr: false,
});

export default function ModelRunning({
  location,
  query = "Gravitational Energy",
  coords,
}: {
  location: string | undefined;
  query: string;
  coords: [number, number];
}) {
  useEffect(() => {
    var encodedLocation = null;
    if (location) {
      encodedLocation = encodeURIComponent(location);
    }
    const encodedQuery = encodeURIComponent(query.trim());
    const encodedTag = encodeURIComponent("Area Demographics");
    const client = localStorage.getItem("clientId");
    const encodedClientId = encodeURIComponent(client || "");
    const encodedCoords = encodeURIComponent(coords.join(" "));

    if (encodedLocation && encodedQuery) {
      const eventSource = new EventSource(
        `http://localhost:8080/api/pipeline?location=${encodedLocation}&query=${encodedQuery}&tag=${encodedTag}&client_id=${encodedClientId}&coords=${encodedCoords}`
      );
      eventSource.onmessage = function (event) {
        console.log("Message:", event.data);
        // add response to ui
        const status = document.getElementById("status");
        if (!status) return;

        if (event.data === "DONE") {
          console.log("Event source closed.");
          eventSource.close();
        } else {
          status.innerText = event.data + "\n";
        }
      };
      eventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        eventSource.close();
      };
    }
  });
  return (
    <Grid
      container
      justifyContent="center"
      alignItems="center"
      style={{ minHeight: "100vh" }}
    >
      <Typography id="status">Model running...</Typography>
    </Grid>
  );
}
