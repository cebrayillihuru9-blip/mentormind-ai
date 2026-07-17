import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = new URLSearchParams();
      data.append("username", form.email);
      data.append("password", form.password);

      const response = await api.post("/users/login", data, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify(response.data.user || {})
      );

      navigate("/dashboard");
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Email və ya şifrə yanlışdır."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-layout">
      <section className="auth-promo">
        <div className="brand">MentorMind AI</div>

        <div className="auth-promo-content">
          <span className="eyebrow">İnkişafını sürətləndir</span>

          <h1>
            Doğru mentorla
            <br />
            doğru istiqamətə get.
          </h1>

          <p>
            Peşəkar mentorlar, fərdi inkişaf planları və
            süni intellekt dəstəkli tövsiyələr bir platformada.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <form className="auth-card" onSubmit={handleSubmit}>
          <div>
            <span className="eyebrow">Xoş gəlmisiniz</span>
            <h2>Hesabınıza daxil olun</h2>
            <p className="muted">
              İnkişaf yolunuza qaldığınız yerdən davam edin.
            </p>
          </div>

          {error && <div className="alert error">{error}</div>}

          <label>
            Email
            <input
              name="email"
              type="email"
              placeholder="email@example.com"
              value={form.email}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Şifrə
            <input
              name="password"
              type="password"
              placeholder="Minimum 6 simvol"
              value={form.password}
              onChange={handleChange}
              required
            />
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? "Daxil olunur..." : "Daxil ol"}
          </button>

          <p className="auth-footer">
            Hesabınız yoxdur? <Link to="/">Qeydiyyatdan keçin</Link>
          </p>
        </form>
      </section>
    </main>
  );
}

export default Login;
