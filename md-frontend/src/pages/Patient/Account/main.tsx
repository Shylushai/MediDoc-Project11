import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Grid,
  OutlinedInput,
  Paper,
  TextField,
  Typography,
  styled,
} from "@mui/material";
import { isAxiosError } from "axios";
import { useEffect, useState } from "react";
import api from "../../../api";
import { Controller, useForm } from "react-hook-form";

const FormGrid = styled(Grid)(() => ({
  display: "flex",
  flexDirection: "column",
}));

const formLayout = [
  {
    label: "Personal Information",
    fields: [
      {
        label: "First name",
        name: "first_name",
        type: "name",
        placeholder: "John",
        autoComplete: "first name",
        required: true,
        editable: false,
      },
      {
        label: "Last name",
        name: "last_name",
        type: "last_name",
        placeholder: "Snow",
        autoComplete: "last name",
        required: true,
        editable: false,
      },
      {
        label: "Address",
        name: "address",
        type: "address",
        placeholder: "Street name and number",
        autoComplete: "saddress-line",
        required: true,
        editable: true,
      },
      {
        label: "Email",
        name: "email",
        type: "email",
        placeholder: "example@abcmail.com",
        autoComplete: "email",
        required: true,
        editable: true,
      },
      {
        label: "Phone",
        name: "contact",
        type: "phone",
        placeholder: "04XXXXXXXX",
        autoComplete: "phone",
        required: true,
        editable: true,
      },
      {
        label: "Date of Birth",
        name: "dob",
        type: "dob",
        placeholder: "YYYY-MM-DD",
        autoComplete: "dob",
        required: true,
        editable: false,
      },
    ],
  },
  {
    label: "Emergency Information",
    fields: [
      {
        label: "First name",
        name: "sub_first_name",
        type: "name",
        placeholder: "John",
        autoComplete: "first name",
        required: true,
        editable: true,
      },
      {
        label: "Last name",
        name: "sub_last_name",
        type: "last-name",
        placeholder: "Snow",
        autoComplete: "last name",
        required: true,
        editable: true,
      },
      {
        label: "Address",
        name: "sub_address",
        type: "address",
        placeholder: "Street name and number",
        autoComplete: "saddress-line",
        required: true,
        editable: true,
      },
      {
        label: "Email",
        name: "sub_email",
        type: "email",
        placeholder: "example@abcmail.com",
        autoComplete: "email",
        required: true,
        editable: true,
      },
    ],
  },
];

const AccountFormField = ({
  name,
  control,
  label,
  type,
  placeholder,
  required,
  editable,
  isEditing,
}) => {
  return (
    <Controller
      name={name}
      control={control}
      render={({
        field: { onChange, value },
        fieldState: { error },
        formState,
      }) => (
        <FormGrid item xs={12} md={6}>
          <TextField
            //variant={isEditing && editable ? "outlined" : "standard"}
            variant="standard"
            id={name}
            name={name}
            label={label}
            type={type}
            placeholder={placeholder}
            required={required}
            value={value}
            onChange={onChange}
            disabled={!isEditing || !editable}
            inputProps={{ readOnly: !editable }}
          />
        </FormGrid>
      )}
    />
  );
};

export default function Account({ user }) {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);

  const { handleSubmit, control, setValue } = useForm({
    defaultValues: {
      //Set default values here so that the form is not empty when rendered
      first_name: "",
      last_name: "",
      address: "",
      email: "",
      contact: "",
      dob: "",
      sub_first_name: "",
      sub_last_name: "",
      sub_address: "",
      sub_email: "",
    },
  });

  const FormFields = formLayout.map((section, index) => {
    const sectionLabel = (
      <>
        <FormGrid item xs={6} key={"idx-fr-" + index}>
          <Typography variant="h6" component="p">
            {section.label}
          </Typography>
        </FormGrid>
        <FormGrid
          item
          xs={6}
          sx={{
            flexDirection: "row",
            justifyContent: "flex-end",
          }}
        >
          <Button onClick={() => setIsEditing(!isEditing)} variant="outlined">
            {isEditing ? "Cancel" : "Edit"}
          </Button>
        </FormGrid>
        {section.fields.map((field, index) => (
          <AccountFormField
            name={field.name}
            control={control}
            label={field.label}
            type={field.type}
            placeholder={field.placeholder}
            required={field.required}
            key={"idx-aff-" + index + field.name}
            editable={field.editable}
            isEditing={isEditing}
          />
        ))}
      </>
    );
    return sectionLabel;
  });

  const onSubmit = (data) => {
    setIsEditing(false);
    console.log(data);
    const submitData = {
      user: {
        patient_id: user.patient_id,
        first_name: data.first_name,
        last_name: data.last_name,
        address: data.address,
        email: data.email,
        contact: data.contact,
        dob: data.dob,
      },
      emergency_contact: {
        first_name: data.sub_first_name,
        last_name: data.sub_last_name,
        address: data.sub_address,
        email: data.sub_email,
        contact: data.sub_contact,
      },
    };
    console.log(submitData);
    const postData = async () => {
      try {
        const response = await api.post("/patient/", submitData);
        console.log(response.data);
      } catch (error) {
        if (isAxiosError(error)) {
          setError(error.response);
        } else {
          console.error(error);
        }
      }
    };
    postData();
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get("/patient", {
          params: { patient_id: user.patient_id },
        });
        console.log(response.data);
        setData(response.data);
        for (const kex in response.data.emergency_contact) {
          console.log(
            "sub_" + kex,
            response.data.emergency_contact["sub_" + kex]
          );
          setValue("sub_" + kex, response.data.emergency_contact[kex]);
        }
        for (const key in response.data.user) {
          setValue(key, response.data.user[key]);
        }
        //setValue("name", response.data.name);
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
    <Box sx={{width: "100%" }}>
      <Box sx={{  }}>
        <h1>My Profile</h1>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Paper elevation={3} sx={{ padding: 4, marginRight: 8 }}>
            <Grid container spacing={3}>
              {FormFields}

              <FormGrid item xs={12}>
                {
                  <Button
                    variant="outlined"
                    color="secondary"
                    type="submit"
                    size="large"
                    disabled={!isEditing}
                  >
                    Submit
                  </Button>
                }
              </FormGrid>
            </Grid>
          </Paper>
        </form>
      </Box>
    </Box>
  );
}
