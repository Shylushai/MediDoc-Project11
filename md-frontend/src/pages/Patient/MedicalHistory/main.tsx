import {
  Autocomplete,
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
} from "@mui/material";
import { isAxiosError } from "axios";
import { useEffect, useState } from "react";
import api from "../../../api";
import Menu from "@mui/icons-material/Menu";

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}

export default function MedicalHistory({ user }) {
  const [data, setData] = useState([]);
  const [dataList, setDataList] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState("");
  const filterOptions = [
    { value: "allergy", label: "Allergy" },
    { value: "immunisation", label: "Immunisation" },
    { value: "medicine", label: "Medicine" },
    { value: "testresult", label: "Test Results" },
    { value: "document", label: "Document" },
    { value: "", label: "None" },
  ];
  const cardTypeLabelMap = new Map();
  cardTypeLabelMap.set("allergy", "Allergy");
  cardTypeLabelMap.set("immunisation", "Immunisation");
  cardTypeLabelMap.set("medicine", "Medicine");
  cardTypeLabelMap.set("testresult", "Test Results");
  cardTypeLabelMap.set("document", "Document");
  cardTypeLabelMap.set("", "None");

  const handleFilterChange = (event) => {
    setFilterType(event.target.value);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/patient/get_record", {
          params: { patient_id: user.patient_id },
        });
        console.log(response.data);
        setData(response.data);

        const dataList = [];
        for (const arr in response.data) {
          response.data[arr].map((item) => {
            item.type = arr;
            dataList.push(item);
          });
        }
        setDataList(dataList);
        setLoading(false);
      } catch (error) {
        if (isAxiosError(error)) {
          setError(error.response);
        } else {
          console.error(error);
        }
      }
    };
    fetchData();
  }, []);

  return (
    <Box sx={{ display: "flex", width: "100%" }}>
      <Box sx={{ flexGrow: 1 }}>
        <h1>Medical History</h1>
        <FormControl sx={{ width: "10rem" }}>
          <InputLabel id="filter-select-label">Filter By Type</InputLabel>
          <Select
            labelId="filter-select-label"
            value={filterType}
            label="Filter By Type"
            onChange={handleFilterChange}
            defaultValue=""
          >
            {filterOptions.map((option) => (
              <MenuItem value={option.value}>{option.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <p>Current Year: {new Date().getFullYear()}</p>
        {(filterType
          ? dataList?.filter((item) => item.type === filterType)
          : dataList
        )?.map((item, index) => (
          <>
            <Card
              sx={{
                display: "flex",
                justifyContent: "space-between",
                marginY: "1rem",
                width: "100%",
              }}
              key={"index" + "card-type-records-" + index}
            >
              <Box sx={{ display: "flex", flexDirection: "column" }}>
                <CardContent>
                  <h2>{cardTypeLabelMap.get(item.type)}</h2>
                  {Object.entries(item).map(([key, value]) => (
                    <p key={key}>
                      {capitalizeFirstLetter(key.replace(/_/g, " "))}: {value}
                    </p>
                  ))}
                </CardContent>
              </Box>
              <Box sx={{ display: "flex", flexDirection: "column" }}>
                <CardContent>
                  <p>{item.date}</p>
                </CardContent>
              </Box>
            </Card>
          </>
        ))}
        {/* {dataList?.map((item, index) => (
          <Card
            sx={{
              display: "flex",
              justifyContent: "space-between",
              marginY: "1rem",
              width: "100%",
            }}
            key={"index" + "card-type-records-" + index}
          >
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <CardContent>
                <h2>{cardTypeLabelMap.get(item.type)}</h2>
                {Object.entries(item).map(([key, value]) => (
                  <p key={key}>
                    {capitalizeFirstLetter(key.replace(/_/g, " "))}: {value}
                  </p>
                ))}
              </CardContent>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <CardContent>
                <p>{item.date}</p>
              </CardContent>
            </Box>
          </Card>
        ))} */}
      </Box>
    </Box>
  );
}
