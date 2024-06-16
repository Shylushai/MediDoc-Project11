import * as React from "react";
import { Button, SvgIconTypeMap, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export default function BigHomeButton({
  label,
  icon,
  path,
}: {
  label: string;
  icon: React.ReactNode;
  path: string;
}) {
  return (
    <React.Fragment>
      <Link to={path} style={{ textDecoration: "none" }}>
        <Button endIcon={icon} variant="contained" fullWidth sx={{minHeight: "10rem"}}>
          <Typography
            variant="button"
            display="block"
            sx={{ paddingY: "2rem" }}
          >
            {label}
          </Typography>
        </Button>
      </Link>
    </React.Fragment>
  );
}
