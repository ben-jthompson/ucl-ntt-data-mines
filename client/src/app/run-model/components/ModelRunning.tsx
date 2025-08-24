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
import { ReportFile } from "@/types/ReportFile";

const ResultMap = dynamic(() => import("../../../components/ResultMap"), {
  ssr: false,
});

export default function ModelRunning({
  location,
  query = "Gravitational Energy",
  coords,
  buffer,
  onFinishedRunning,
  onReportCompletion,
}: {
  location: string | undefined;
  query: string;
  coords: [number, number];
  buffer: number;
  onFinishedRunning: (running: boolean) => void;
  onReportCompletion: (report: ReportFile) => void;
}) {
  const [progressBar, setProgressBar] = useState(0.1);

  useEffect(() => {
    onFinishedRunning(true);
    var encodedLocation = null;
    if (location) {
      encodedLocation = encodeURIComponent(location);
    }
    const encodedQuery = encodeURIComponent(query.trim());
    // TODO: change - not needed
    const encodedTag = encodeURIComponent("Area Demographics");
    const client = localStorage.getItem("clientId");
    const encodedClientId = encodeURIComponent(client || "");
    const encodedCoords = encodeURIComponent(coords.join(" "));
    const encodedBuffer = encodeURIComponent(buffer);

    if (encodedLocation && encodedQuery) {
      const eventSource = new EventSource(
        `http://localhost:8080/api/pipeline?location=${encodedLocation}&query=${encodedQuery}&tag=${encodedTag}&client_id=${encodedClientId}&coords=${encodedCoords}&buffer=${encodedBuffer}`
      );
      eventSource.onmessage = function (event) {
        // add response to ui
        const status = document.getElementById("status");
        if (!status) return;
        try {
          const message = JSON.parse(event.data);
          console.log("[MESSAGE] " + JSON.stringify(message));
          if (message.type === "node_change") {
            status.innerText = message.node[0] + "\n";
            setProgressBar(message.node[1] / 12);
            console.log(status.innerText);
          }
          if (message.type === "node_change" && message.done === "true") {
            console.log("Event source closed.");
            const report = {
              file_name: message.report.file_name,
              display_name: message.report.display_name,
              description: message.report.description,
              id: message.report.id,
              coords: message.report.coords,
              upload_date: message.report.upload_date,
            };
            console.log("[REPORT]: ", report);
            eventSource.close();
            onFinishedRunning(false);
            onReportCompletion(report);
          }
        } catch (err) {
          // console.warn("Non-JSON SSE:", event.data);
          console.log("diff output");
        }
      };
      eventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        eventSource.close();
        onFinishedRunning(false);
      };
    }
  }, []);
  return (
    <Grid
      container
      justifyContent="center"
      alignItems="center"
      style={{ minHeight: "100vh" }}
    >
      <progress value={progressBar} />
      <Typography id="status">Model running...</Typography>
    </Grid>
  );
}
