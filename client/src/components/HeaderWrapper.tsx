"use client";

import { Box, CssBaseline } from "@mui/material";
import Header from "../components/Header";
import { ThemeProvider } from "@mui/material/styles";
import theme from "../styles/theme";

export default function HeaderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: "100vh" }}>
        <Header />
        <main>{children}</main>
      </Box>
    </ThemeProvider>
  );
}
