import { useState } from "react";
import api from "../api/axios";

function Register() {

    const [form, setForm] = useState({
        full_name: "",
        email: "",
        password: ""
    });

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value
        });
    };


    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await api.post(
                "/users/register",
                form
            );

            console.log(response.data);

            alert("Qeydiyyat uğurludur");

        } catch (error) {
            console.log(error.response?.data);
            alert("Xəta baş verdi");
        }
    };


    return (
        <div>
            <h2>Register</h2>

            <form onSubmit={handleSubmit}>

                <input
                    name="full_name"
                    placeholder="Ad Soyad"
                    onChange={handleChange}
                />

                <input
                    name="email"
                    placeholder="Email"
                    type="email"
                    onChange={handleChange}
                />

                <input
                    name="password"
                    placeholder="Şifrə"
                    type="password"
                    onChange={handleChange}
                />

                <button type="submit">
                    Register
                </button>

            </form>

        </div>
    );
}

export default Register;