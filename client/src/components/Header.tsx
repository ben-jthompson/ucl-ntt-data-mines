import React, { useEffect } from "react";
import { usePathname } from "next/navigation";
import NextLink from "next/link";
import {
  AppBar,
  Toolbar,
  Container,
  Button,
  Typography,
  Box,
  useTheme,
} from "@mui/material";
import { v4 as uuidv4 } from "uuid";

const Header = () => {
  const pathname = usePathname();
  const theme = useTheme();

  const navLinks = [
    { href: "/run-model", label: "Run Model" },
    { href: "/reports", label: "Reports" },
  ];

  useEffect(() => {
    let clientId = localStorage.getItem("clientId");

    if (!clientId) {
      // if this is first visit
      clientId = uuidv4();
      localStorage.setItem("clientId", clientId);
    }
  });

  return (
    <AppBar position="sticky" color="default" elevation={4}>
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ justifyContent: "space-between" }}>
          {/* Logo or Title */}
          <Typography
            variant="h6"
            component={NextLink}
            href="/"
            sx={{
              textDecoration: "none",
              color: theme.palette.primary.main,
              fontWeight: "bold",
              cursor: "pointer",
              "&:hover": { color: theme.palette.primary.dark },
            }}
          >
            Data Center Suitability
          </Typography>

          {/* Navigation Links */}
          <Box>
            {navLinks.map(({ href, label }) => {
              const isActive = pathname === href;
              return (
                <Button
                  key={href}
                  component={NextLink}
                  href={href}
                  color={isActive ? "primary" : "inherit"}
                  sx={{
                    mx: 1,
                    fontWeight: isActive ? "bold" : "normal",
                    borderBottom: isActive
                      ? `3px solid ${theme.palette.primary.main}`
                      : "3px solid transparent",
                    borderRadius: 0,
                    textTransform: "none",
                    "&:hover": {
                      backgroundColor: "transparent",
                      borderBottom: `3px solid ${theme.palette.primary.main}`,
                    },
                  }}
                >
                  {label}
                </Button>
              );
            })}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
