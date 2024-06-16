import * as React from "react";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import PeopleIcon from "@mui/icons-material/People";
import BarChartIcon from "@mui/icons-material/BarChart";
import LayersIcon from "@mui/icons-material/Layers";
import AssignmentIcon from "@mui/icons-material/Assignment";
import { Link } from "react-router-dom";

export const PatientSideMenuListItemBtn = ({
  label,
  path,
  icon,
}: {
  label: string;
  path: string;
  icon: React.ReactNode;
}) => {
  return (
    <Link to={path} style={{ textDecoration: "none", color: "black" }}>
      <ListItemButton>
        <ListItemIcon>{icon}</ListItemIcon>
        <ListItemText primary={label} />
      </ListItemButton>
    </Link>
  );
};

export const mainListItems = (
  <React.Fragment>
    <PatientSideMenuListItemBtn label="Home" path="" icon={<PeopleIcon />} />
    <PatientSideMenuListItemBtn
      label="Account"
      path="account"
      icon={<DashboardIcon />}
    />
    <PatientSideMenuListItemBtn
      label="Appointment"
      path="appointment"
      icon={<AssignmentIcon />}
    />
  </React.Fragment>
);

export const secondaryListItems = (
  <React.Fragment>
    <ListItemButton>
      <ListItemIcon>
        <AssignmentIcon />
      </ListItemIcon>
      <ListItemText primary="Log Out" />
    </ListItemButton>
  </React.Fragment>
);
