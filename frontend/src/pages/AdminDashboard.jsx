import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

const roleNames = {
  user: "İstifadəçi",
  mentor: "Mentor",
  admin: "Admin",
};

function AdminDashboard() {
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("user");
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [notice, setNotice] = useState(null);

  const [mentorForm, setMentorForm] = useState({
    expertise: "",
    bio: "",
    hourly_rate: "",
  });

  const storedAdmin = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "{}");
    } catch {
      return {};
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    const initializeAdmin = async () => {
      try {
        const response = await api.get("/admin/users");

        if (!cancelled) {
          setUsers(response.data);
        }
      } catch (error) {
        if (!cancelled) {
          setNotice({
            type: "error",
            text:
              error.response?.data?.detail ||
              "İstifadəçilər yüklənmədi.",
          });
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void initializeAdmin();

    return () => {
      cancelled = true;
    };
  }, []);

  const refreshUsers = async () => {
    const response = await api.get("/admin/users");
    setUsers(response.data);
  };

  const statistics = useMemo(
    () => ({
      total: users.length,
      users: users.filter((user) => user.role === "user").length,
      mentors: users.filter((user) => user.role === "mentor").length,
      admins: users.filter((user) => user.role === "admin").length,
    }),
    [users]
  );

  const filteredUsers = useMemo(() => {
    const value = search.trim().toLowerCase();

    return users.filter((user) => {
      const matchesRole =
        roleFilter === "all" || user.role === roleFilter;

      const matchesSearch =
        !value ||
        `${user.full_name} ${user.email} ${user.role} ${
          user.mentor?.expertise || ""
        }`
          .toLowerCase()
          .includes(value);

      return matchesRole && matchesSearch;
    });
  }, [users, search, roleFilter]);

  const openMentorForm = (user) => {
    setSelectedUser(user);

    setMentorForm({
      expertise: user.mentor?.expertise || "",
      bio: user.mentor?.bio || "",
      hourly_rate: user.mentor?.hourly_rate || "",
    });

    setNotice(null);

    window.setTimeout(() => {
      document
        .getElementById("mentor-conversion-form")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 50);
  };

  const saveMentor = async (event) => {
    event.preventDefault();

    if (!selectedUser) {
      return;
    }

    setActionLoading(`mentor-${selectedUser.id}`);
    setNotice(null);

    try {
      await api.post(
        `/admin/users/${selectedUser.id}/make-mentor`,
        {
          expertise: mentorForm.expertise.trim(),
          bio: mentorForm.bio.trim(),
          hourly_rate: Number(mentorForm.hourly_rate),
        }
      );

      await refreshUsers();

      setNotice({
        type: "success",
        text: `${selectedUser.full_name} mentor edildi.`,
      });

      setSelectedUser(null);
      setMentorForm({
        expertise: "",
        bio: "",
        hourly_rate: "",
      });

      setRoleFilter("mentor");
    } catch (error) {
      setNotice({
        type: "error",
        text:
          error.response?.data?.detail ||
          "İstifadəçi mentor edilə bilmədi.",
      });
    } finally {
      setActionLoading("");
    }
  };

  const removeMentorRole = async (user) => {
    const confirmed = window.confirm(
      `${user.full_name} üçün mentor rolu silinsin?`
    );

    if (!confirmed) {
      return;
    }

    setActionLoading(`remove-${user.id}`);
    setNotice(null);

    try {
      await api.put(`/admin/users/${user.id}/make-user`);
      await refreshUsers();

      setNotice({
        type: "success",
        text: `${user.full_name} adi istifadəçiyə çevrildi.`,
      });
    } catch (error) {
      setNotice({
        type: "error",
        text:
          error.response?.data?.detail ||
          "Mentor rolu silinə bilmədi.",
      });
    } finally {
      setActionLoading("");
    }
  };

  const deleteUser = async (user) => {
    const confirmed = window.confirm(
      `${user.full_name} hesabı tam silinsin?\n\nBu əməliyyat geri qaytarılmır.`
    );

    if (!confirmed) {
      return;
    }

    setActionLoading(`delete-${user.id}`);
    setNotice(null);

    try {
      await api.delete(`/admin/users/${user.id}`);
      await refreshUsers();

      if (selectedUser?.id === user.id) {
        setSelectedUser(null);
      }

      setNotice({
        type: "success",
        text: `${user.full_name} hesabı silindi.`,
      });
    } catch (error) {
      setNotice({
        type: "error",
        text:
          error.response?.data?.detail ||
          "İstifadəçi silinə bilmədi.",
      });
    } finally {
      setActionLoading("");
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  if (loading) {
    return (
      <div className="page-loader">
        Admin paneli yüklənir...
      </div>
    );
  }

  return (
    <main className="dashboard-layout">
      <aside className="sidebar admin-sidebar">
        <div className="brand">MentorMind AI</div>

        <div className="admin-sidebar-label">
          İdarəetmə paneli
        </div>

        <nav>
          <button
            className={`nav-item ${
              roleFilter === "user" ? "active" : ""
            }`}
            onClick={() => setRoleFilter("user")}
          >
            İstifadəçilər
          </button>

          <button
            className={`nav-item ${
              roleFilter === "mentor" ? "active" : ""
            }`}
            onClick={() => setRoleFilter("mentor")}
          >
            Mentorlar
          </button>

          <button
            className={`nav-item ${
              roleFilter === "admin" ? "active" : ""
            }`}
            onClick={() => setRoleFilter("admin")}
          >
            Adminlər
          </button>
        </nav>

        <div className="admin-sidebar-user">
          <strong>{storedAdmin.full_name}</strong>
          <span>{storedAdmin.email}</span>
        </div>

        <button className="logout-button" onClick={logout}>
          Çıxış
        </button>
      </aside>

      <section className="dashboard-content">
        <header className="dashboard-header">
          <div>
            <span className="eyebrow">Admin paneli</span>
            <h1>Platformanın idarə edilməsi</h1>
            <p className="muted">
              İstifadəçiləri, mentorları və admin hesablarını
              ayrı-ayrılıqda idarə edin.
            </p>
          </div>

          <div className="user-badge">
            <div className="avatar">A</div>

            <div>
              <strong>{storedAdmin.full_name}</strong>
              <span>Administrator</span>
            </div>
          </div>
        </header>

        {notice && (
          <div className={`alert ${notice.type}`}>
            {notice.text}
          </div>
        )}

        <section className="stats-grid">
          <article
            className={`stat-card clickable-stat ${
              roleFilter === "all" ? "selected" : ""
            }`}
            onClick={() => setRoleFilter("all")}
          >
            <span>Ümumi hesablar</span>
            <strong>{statistics.total}</strong>
          </article>

          <article
            className={`stat-card clickable-stat ${
              roleFilter === "user" ? "selected" : ""
            }`}
            onClick={() => setRoleFilter("user")}
          >
            <span>İstifadəçilər</span>
            <strong>{statistics.users}</strong>
          </article>

          <article
            className={`stat-card clickable-stat ${
              roleFilter === "mentor" ? "selected" : ""
            }`}
            onClick={() => setRoleFilter("mentor")}
          >
            <span>Mentorlar</span>
            <strong>{statistics.mentors}</strong>
          </article>

          <article
            className={`stat-card clickable-stat ${
              roleFilter === "admin" ? "selected" : ""
            }`}
            onClick={() => setRoleFilter("admin")}
          >
            <span>Adminlər</span>
            <strong>{statistics.admins}</strong>
          </article>
        </section>

        <section className="section-heading">
          <div>
            <span className="eyebrow">
              {roleFilter === "all"
                ? "Bütün hesablar"
                : roleNames[roleFilter]}
            </span>

            <h2>
              {roleFilter === "all"
                ? "Bütün hesablar"
                : `${roleNames[roleFilter]} siyahısı`}
            </h2>
          </div>

          <input
            className="search-input"
            placeholder="Ad, email və ya ixtisas..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </section>

        <div className="role-filter-bar">
          {[
            ["all", "Hamısı", statistics.total],
            ["user", "İstifadəçilər", statistics.users],
            ["mentor", "Mentorlar", statistics.mentors],
            ["admin", "Adminlər", statistics.admins],
          ].map(([value, label, count]) => (
            <button
              key={value}
              className={`filter-chip ${
                roleFilter === value ? "active" : ""
              }`}
              onClick={() => setRoleFilter(value)}
            >
              {label}
              <span>{count}</span>
            </button>
          ))}
        </div>

        <section className="admin-user-list">
          {filteredUsers.map((user) => (
            <article className="admin-user-card" key={user.id}>
              <div className="admin-user-main">
                <div className="avatar">
                  {user.full_name.charAt(0).toUpperCase()}
                </div>

                <div className="admin-user-info">
                  <strong>{user.full_name}</strong>
                  <span>{user.email}</span>

                  {user.mentor && (
                    <small>
                      {user.mentor.expertise} ·{" "}
                      {user.mentor.hourly_rate} AZN/saat
                    </small>
                  )}
                </div>
              </div>

              <div className="admin-user-actions">
                <span className={`role-badge ${user.role}`}>
                  {roleNames[user.role] || user.role}
                </span>

                {user.role === "user" && (
                  <button
                    className="primary-button small"
                    onClick={() => openMentorForm(user)}
                  >
                    Mentor et
                  </button>
                )}

                {user.role === "mentor" && (
                  <>
                    <button
                      className="secondary-button"
                      onClick={() => openMentorForm(user)}
                    >
                      Redaktə et
                    </button>

                    <button
                      className="secondary-button"
                      disabled={
                        actionLoading === `remove-${user.id}`
                      }
                      onClick={() => removeMentorRole(user)}
                    >
                      User et
                    </button>
                  </>
                )}

                {user.role !== "admin" && (
                  <button
                    className="danger-button"
                    disabled={
                      actionLoading === `delete-${user.id}`
                    }
                    onClick={() => deleteUser(user)}
                  >
                    {actionLoading === `delete-${user.id}`
                      ? "Silinir..."
                      : "Sil"}
                  </button>
                )}
              </div>
            </article>
          ))}
        </section>

        {filteredUsers.length === 0 && (
          <div className="empty-state">
            <h3>Hesab tapılmadı</h3>
            <p>
              Seçilən filtrə uyğun hesab mövcud deyil.
            </p>
          </div>
        )}

        {selectedUser && (
          <section
            id="mentor-conversion-form"
            className="admin-mentor-section"
          >
            <div className="section-heading">
              <div>
                <span className="eyebrow">
                  Mentor məlumatları
                </span>

                <h2>{selectedUser.full_name}</h2>
                <p className="muted">{selectedUser.email}</p>
              </div>

              <button
                className="text-button"
                onClick={() => setSelectedUser(null)}
              >
                Formu bağla
              </button>
            </div>

            <form
              className="panel-card admin-mentor-form"
              onSubmit={saveMentor}
            >
              <label>
                İxtisas
                <input
                  placeholder="Python Backend, React, UI/UX..."
                  value={mentorForm.expertise}
                  onChange={(event) =>
                    setMentorForm({
                      ...mentorForm,
                      expertise: event.target.value,
                    })
                  }
                  required
                />
              </label>

              <label>
                Saatlıq qiymət
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  value={mentorForm.hourly_rate}
                  onChange={(event) =>
                    setMentorForm({
                      ...mentorForm,
                      hourly_rate: event.target.value,
                    })
                  }
                  required
                />
              </label>

              <label className="admin-form-full">
                Mentor haqqında məlumat
                <textarea
                  rows="6"
                  value={mentorForm.bio}
                  onChange={(event) =>
                    setMentorForm({
                      ...mentorForm,
                      bio: event.target.value,
                    })
                  }
                  required
                />
              </label>

              <div className="admin-form-full admin-form-buttons">
                <button
                  className="primary-button"
                  disabled={
                    actionLoading ===
                    `mentor-${selectedUser.id}`
                  }
                >
                  {selectedUser.role === "mentor"
                    ? "Mentor məlumatlarını yenilə"
                    : "İstifadəçini mentor et"}
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setSelectedUser(null)}
                >
                  Ləğv et
                </button>
              </div>
            </form>
          </section>
        )}
      </section>
    </main>
  );
}

export default AdminDashboard;
