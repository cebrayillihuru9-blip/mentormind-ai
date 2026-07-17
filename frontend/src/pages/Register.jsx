import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
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
    setSuccess("");
    setLoading(true);

    try {
      await api.post("/users/register", form);

      setSuccess("Qeydiyyat uğurla tamamlandı.");

      setTimeout(() => {
        navigate("/login");
      }, 700);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Qeydiyyat zamanı xəta baş verdi."
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
          <span className="eyebrow">Gələcəyini qur</span>

          <h1>
            Təcrübədən öyrən,
            <br />
            daha sürətli inkişaf et.
          </h1>

          <p>
            Məqsədinə uyğun mentor tap, görüş rezervasiya et
            və şəxsi inkişaf planını idarə et.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <form className="auth-card" onSubmit={handleSubmit}>
          <div>
            <span className="eyebrow">Yeni hesab</span>
            <h2>Qeydiyyatdan keçin</h2>
            <p className="muted">
              MentorMind AI dünyasına bir neçə saniyədə qoşulun.
            </p>
          </div>

          {error && <div className="alert error">{error}</div>}
          {success && <div className="alert success">{success}</div>}

          <label>
            Ad və soyad
            <input
              name="full_name"
              placeholder="Ad Soyad"
              value={form.full_name}
              onChange={handleChange}
              minLength={2}
              required
            />
          </label>

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
              minLength={6}
              required
            />
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? "Hesab yaradılır..." : "Hesab yarat"}
          </button>

          <p className="auth-footer">
            Artıq hesabınız var? <Link to="/login">Daxil olun</Link>
          </p>
        </form>
      </section>
    </main>
  );
}

export default Register;
