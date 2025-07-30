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

export default function ModelRunning() {
  useEffect(() => {
    const eventSource = new EventSource(
      "http://localhost:8080/api/run_pipeline?location=Nottingham&query=Water%20Heat%20Nottinghamshire%20Mine%20Reuse"
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
        status.innerText += event.data + "\n";
      }
    };

    eventSource.onerror = function (error) {
      console.error("EventSource failed:", error);
      eventSource.close();
    };
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
