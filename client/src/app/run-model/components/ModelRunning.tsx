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
import axios from "axios";
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
  coords,
  buffer,
  onFinishedRunning,
  onReportCompletion,
}: {
  location: string | undefined;
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
    const client = localStorage.getItem("clientId");
    const encodedClientId = encodeURIComponent(client || "");
    const encodedCoords = encodeURIComponent(coords.join(" "));
    const encodedBuffer = encodeURIComponent(buffer);
    try {
      axios.delete(`http://localhost:8080/api/clients/${client}/model/start`);
    } catch (err) {
      console.error("Cleanup failed", err);
    }

    // run on unmount to delete intermediate variables

    if (encodedLocation) {
      const eventSource = new EventSource(
        `http://localhost:8080/api/pipeline?location=${encodedLocation}&client_id=${encodedClientId}&coords=${encodedCoords}&buffer=${encodedBuffer}`
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
            setProgressBar(message.node[1] / 16);
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
      <Typography>
        Note: Reloading or navigating from the page may result in a wait for
        data in newly loaded pages, while the model workflow is terminated.
      </Typography>
    </Grid>
  );
}
