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

import dynamic from "next/dynamic";

const ResultMap = dynamic(() => import("../../components/ResultMap"), {
  ssr: false,
});

export default function Map() {
  return (
    <Grid
      container
      justifyContent="center"
      alignItems="center"
      style={{ minHeight: "100vh" }}
    >
      <Typography>Placeholder</Typography>
    </Grid>
  );
}
