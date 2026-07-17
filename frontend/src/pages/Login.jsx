import { useState } from "react";
import api from "../api/axios";

function Login() {

    const [form, setForm] = useState({
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
            const data = new URLSearchParams();

            data.append("username", form.email);
            data.append("password", form.password);


            const response = await api.post(
                "/users/login",
                data,
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                }
            );


            console.log(response.data);

            localStorage.setItem(
                "token",
                response.data.access_token
            );


            alert("Login uğurludur");


        } catch (error) {

            console.log(error.response?.data);

            alert("Xəta baş verdi");
        }
    };


    return (
        <div>

            <h2>Login</h2>

            <form onSubmit={handleSubmit}>

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
                    Daxil ol
                </button>

            </form>

        </div>
    );
}

export default Login;