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


            alert("Login uğurludur ✅");
            window.location.href = "/dashboard";


        } catch (error) {

            console.log(error.response?.data);

            alert(
                error.response?.data?.detail ||
                "Login xətası"
            );
        }
    };


    return (
        <div>

            <h2>Login</h2>

            <form onSubmit={handleSubmit}>

                <input
                    name="email"
                    type="email"
                    placeholder="Email"
                    onChange={handleChange}
                    required
                />


                <br />


                <input
                    name="password"
                    type="password"
                    placeholder="Şifrə"
                    onChange={handleChange}
                    required
                />


                <br />


                <button type="submit">
                    Daxil ol
                </button>

            </form>

        </div>
    );
}


export default Login;