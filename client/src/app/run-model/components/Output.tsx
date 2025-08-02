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
import axios from "axios";
import dynamic from "next/dynamic";
const ResultMap = dynamic(() => import("../../../components/ResultMap"), {
  ssr: false,
});

export default function Output({
  coords,
  radius,
}: {
  coords: [number, number];
  radius: number;
}) {
  useEffect(() => {
    const client = localStorage.getItem("clientId");
    axios
      .post(`http://localhost:8080/api/clients/${client}/files/zip`, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        console.log("Upload successful:", response.data);
        // TODO add id assignment
      });
  });
  return (
    coords && (
      <>
        <div>
          Coords: {coords[0]}, {coords[1]}
          Radius: {radius}
        </div>
        ;<div> Results</div>
        <ResultMap coords={coords} radius={radius} result={true} />
      </>
    )
  );
}
