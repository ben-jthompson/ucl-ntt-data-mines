"use client";

import { Box, Button, Container, Typography } from "@mui/material";
import NextLink from "next/link";
import { useTheme } from "@mui/material/styles";

export default function Home() {
  const theme = useTheme();

  return (
    <Box
      sx={{
        width: "100%",
        minHeight: "100vh",
        backgroundColor: "#f0f0f0", // light map vibe
        backgroundImage: `url('/map-background.png')`, // optional image overlay
        backgroundRepeat: "no-repeat",
        backgroundSize: "cover",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        pt: 10, // space below header
      }}
    >
      <Container
        maxWidth="sm"
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 3,
          alignItems: "center",
          textAlign: "center",
        }}
      >
        {/* Main Buttons */}
        <Box
          sx={{
            display: "flex",
            gap: 2,
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          <Button
            component={NextLink}
            href="/run-model"
            variant="contained"
            color="primary"
            sx={{ minWidth: 120, fontWeight: "bold" }}
          >
            Run Model
          </Button>
          <Button
            component={NextLink}
            href="/reports"
            variant="contained"
            color="primary"
            sx={{ minWidth: 120, fontWeight: "bold" }}
          >
            Reports
          </Button>
          <Button
            component={NextLink}
            href="/how-it-works"
            variant="contained"
            color="primary"
            sx={{ minWidth: 120, fontWeight: "bold" }}
          >
            How It Works
          </Button>
        </Box>
      </Container>
    </Box>
  );
}
