import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import BigHomeButton from "./BigHomeButton";
import { MedicalInformation } from "@mui/icons-material";

const elements = [
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
  {
    label: "Medical History",
    icon: <MedicalInformation />,
    path: "medHistory",
  },
];

export default function Dashboard({ user }) {
  return (
    <Box sx={{ display: "flex" }}>
      <Box
        component="main"
        sx={{
          backgroundColor: (theme) =>
            theme.palette.mode === "light"
              ? theme.palette.grey[100]
              : theme.palette.grey[900],
          flexGrow: 1,
          height: "100vh",
          overflow: "auto",
        }}
      >
        {/* <Toolbar /> */}
        <h1>Medical History</h1>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper
              sx={{
                p: 2,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <Grid container spacing={1}>
                {elements.map((element, index) => {
                  const key = index + "btn-elx-r-";
                  return (
                    <Grid item xs={12} md={4} lg={3} key={key}>
                      <BigHomeButton
                        label={element.label}
                        icon={element.icon}
                        path={element.path}
                      />
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
}
