import { Box, Card, CardContent } from "@mui/material";
import { isAxiosError } from "axios";
import { useEffect, useState } from "react";
import api from "../../../api";

const mockData = [
  {
    type: "Allergy",
    name: "Peanuts",
    reaction: "Anaphylaxis",
    date: "2021-10-10",
  },
  {
    type: "Allergy",
    name: "Shellfish",
    reaction: "Hives",
    date: "2021-09-09",
  },
  {
    type: "Allergy",
    name: "Milk",
    reaction: "Wheezing",
    date: "2021-08-08",
  },
  {
    type: "Allergy",
    name: "Eggs",
    reaction: "Rash",
    date: "2021-07-07",
  },
  {
    type: "Allergy",
    name: "Soy",
    reaction: "Itching",
    date: "2021-06-06",
  },
  {
    type: "Immunisation",
    name: "MMR",
    date: "2021-01-01",
  },
  {
    type: "Immunisation",
    name: "Hepatitis B",
    date: "2021-02-02",
  },
  {
    type: "Immunisation",
    name: "Influenza",
    date: "2021-03-03",
  },
  {
    type: "Immunisation",
    name: "Chickenpox",
    date: "2021-04-04",
  },
  {
    type: "Immunisation",
    name: "Polio",
    date: "2021-05-05",
  },
  {
    type: "Document",
    name: "Medical Report",
    date: "2021-02-02",
  },
  {
    type: "Document",
    name: "Prescription",
    date: "2021-03-03",
  },
  {
    type: "Document",
    name: "Discharge Summary",
    date: "2021-04-04",
  },
  {
    type: "Document",
    name: "Test Report",
    date: "2021-05-05",
  },
  {
    type: "Document",
    name: "Insurance Claim",
    date: "2021-06-06",
  },
  {
    type: "Test Result",
    name: "Blood Test",
    result: "Normal",
    date: "2021-03-03",
  },
  {
    type: "Test Result",
    name: "Urine Test",
    result: "Normal",
    date: "2021-04-04",
  },
  {
    type: "Test Result",
    name: "MRI Scan",
    result: "Normal",
    date: "2021-05-05",
  },
  {
    type: "Test Result",
    name: "X-Ray",
    result: "Normal",
    date: "2021-06-06",
  },
  {
    type: "Test Result",
    name: "ECG",
    result: "Normal",
    date: "2021-07-07",
  },
  {
    type: "Medicine",
    name: "Paracetamol",
    dosage: "500mg",
    frequency: "Twice a day",
    date: "2021-04-04",
  },
  {
    type: "Medicine",
    name: "Ibuprofen",
    dosage: "200mg",
    frequency: "Once a day",
    date: "2021-05-05",
  },
  {
    type: "Medicine",
    name: "Amoxicillin",
    dosage: "250mg",
    frequency: "Three times a day",
    date: "2021-06-06",
  },
  {
    type: "Medicine",
    name: "Cetirizine",
    dosage: "10mg",
    frequency: "Once a day",
    date: "2021-07-07",
  },
  {
    type: "Medicine",
    name: "Diazepam",
    dosage: "5mg",
    frequency: "As needed",
    date: "2021-08-08",
  },
  {
    type: "Scan",
    name: "MRI",
    result: "Normal",
    date: "2021-05-05",
  },
  {
    type: "Scan",
    name: "CT",
    result: "Normal",
    date: "2021-06-06",
  },
  {
    type: "Scan",
    name: "X-Ray",
    result: "Normal",
    date: "2021-07-07",
  },
  {
    type: "Scan",
    name: "Ultrasound",
    result: "Normal",
    date: "2021-08-08",
  },
  {
    type: "Scan",
    name: "PET",
    result: "Normal",
    date: "2021-09-09",
  },
  {
    type: "Hospital Visit",
    reason: "Checkup",
    date: "2021-06-06",
  },
  {
    type: "Hospital Visit",
    reason: "Surgery",
    date: "2021-07-07",
  },
  {
    type: "Hospital Visit",
    reason: "Emergency",
    date: "2021-08-08",
  },
  {
    type: "Hospital Visit",
    reason: "Follow-up",
    date: "2021-09-09",
  },
  {
    type: "Hospital Visit",
    reason: "Consultation",
    date: "2021-10-10",
  },
];

export default function MedicalHistory({ user }) {
  const [data, setData] = useState([]);
  const [dataList, setDataList] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

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
        <p>Filtered By: None</p>
        <p>Current Year: {new Date().getFullYear()}</p>
        {dataList?.map((item, index) => (
          <Card
            sx={{
              display: "flex",
              justifyContent: "space-between",
              marginY: "1rem",
              width: "100%",
            }}
          >
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <CardContent>
                <h2>{item.type}</h2>
                <p>{item.name}</p>
                <p>{item.allergy_name}</p>
                <p>{item.medicine_name}</p>
                <p>{item.immunisation_name}</p>
                <p>{item.document_name}</p>
                <p>{item.testresult_name}</p>
                <p>{item.reaction}</p>
                <p>{item.reason}</p>
                <p>{item.result}</p>
                <p>{item.dosage}</p>
                <p>{item.frequency}</p>
              </CardContent>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <CardContent>
                <p>{item.date}</p>
              </CardContent>
            </Box>
          </Card>
        ))}
      </Box>
    </Box>
  );
}
